"""PLACE module to control AlazarTech cards"""
from math import ceil
from threading import Thread
from time import sleep
from ctypes import c_void_p
import mpld3
import matplotlib.pyplot as plt
import numpy as np

from place.plugins.instrument import Instrument, send_data_thread
from . import atsapi as ats
setattr(ats, 'TRIG_FORCE', -1)

class ATSGeneric(Instrument, ats.Board):
    """Class which supports all Alazar controllers.

    This class should be overridden if classes are needed for specific cards.

    Note: This class currently only supports boards providing data in an
    unsigned, 2 bytes per sample, format. It should support 12, 14, and 16 bits
    per sample. If 8 bits per sample is desired, that functionality will need
    to be added to this class.
    """
    _bytes_per_sample = 2
    _data_type = np.dtype('<u'+str(_bytes_per_sample)) # (<)little-endian, (u)unsigned

    def __init__(self, config):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Instrument.__init__(self, config)
        ats.Board.__init__(self)
        self._analog_inputs = None
        self._data = None

# PUBLIC METHODS

    def config(self, metadata, total_updates):
        """Configure the Alazar card

        This method is responsible for reading all the data from the
        configuration input and setting up the card for scanning.

        From the ATS-SDK-Guide...
            "Before acquiring data from a board system, an application must
            configure the timebase, analog inputs, and trigger system settings
            for each board in the board system."

        After configuring the board, this method also performs the first data
        acquisition steps by setting the record size and the record count.

        :param metadata: PLACE maintains metadata for each scan in a dictionary
                         object. During the configuration phase, this
                         dictionary is passed to each instrument through this
                         function so that relevant instrument data can be
                         recorded into it. Instruments should record
                         information that is relevant to the entire scan, but
                         is also specific to the instrument. For example, if an
                         instrument is using one of many filters during this
                         scan, it would be appropriate to record the filter
                         into the scan metadata.
        :type metadata: dict

        :param total_updates: This value will always be used to inform each
                              instrument of the number of updates (or steps)
                              that will be perfomed during this scan.
                              Instruments should use this value to determine
                              when to perform specific tasks during the scan.
                              For example, some instruments may want to perform
                              a task at the midpoint of a scan and can
                              therefore use this value to determine which
                              update will represent the midpoint.
        :type total_updates: int
        """
        # execute configuration commands on the card
        self._config_timebase(metadata)
        self._config_analog_inputs()
        self._config_trigger_system()
        self._config_record(metadata)
        _, c_bits = self.getChannelInfo()
        metadata['bits_per_sample'] = c_bits.value

    def update(self, update_number, socket=None):
        """Record a trace using the current configuration

        :param update_number: This will be the current update number (starting
                              with 0) of the experiment. Instruments could
                              certainly count the number of updates themselves,
                              but this is provided as a convenience.
        :type update_number: int

        :param socket: socket for plotting data
        :type socket: websocket

        :returns: the array for this trace
        :rtype: numpy.array
        """
        # build data array
        channels = len(self._config['analog_inputs'])
        if self._config['average']:
            records = 1
        else:
            records = self._config['records']
        samples = self._config['pre_trigger_samples'] + self._config['post_trigger_samples']
        type_str = '({},{},{}){}'.format(channels, records, samples, ATSGeneric._data_type)
        self._data = np.zeros((1,), dtype=[('trace', type_str)])
        self.startCapture()
        self._wait_for_trigger()
        self._read_from_card()
        if self._config['plot'] == 'yes':
            if update_number == 0:
                plt.clf()
            self._draw_plot(socket=socket)
        return self._data.copy()

    def cleanup(self, abort=False):
        """Free any resources used by card"""
        if self._config['plot'] == 'yes':
            plt.close('all')

# PRIVATE METHODS

    def _config_timebase(self, metadata):
        """Sets the capture clock"""
        sample_rate = getattr(ats, self._config['sample_rate'])
        metadata["sampling_rate"] = _sample_rate_to_hertz(sample_rate)
        self.setCaptureClock(getattr(ats, self._config['clock_source']),
                             sample_rate,
                             getattr(ats, self._config['clock_edge']),
                             self._config['decimation'])

    def _config_analog_inputs(self):
        """Specify the desired input range, termination, and coupling of an
        input channel
        """
        self._analog_inputs = []
        for input_data in self._config['analog_inputs']:
            analog_input = AnalogInput(getattr(ats, input_data['input_channel']),
                                       getattr(ats, input_data['input_coupling']),
                                       getattr(ats, input_data['input_range']),
                                       getattr(ats, input_data['input_impedance']))
            analog_input.initialize_on_board(self)
            self._analog_inputs.append(analog_input)

    def _config_trigger_system(self):
        """Configure each of the two trigger engines"""
        if self._config['trigger_source_1'] == "TRIG_FORCE":
            source_1 = getattr(ats, "TRIG_CHAN_A")
        else:
            source_1 = getattr(ats, self._config['trigger_source_1'])
        if self._config['trigger_source_2'] == "TRIG_FORCE":
            source_2 = getattr(ats, "TRIG_CHAN_A")
        else:
            source_2 = getattr(ats, self._config['trigger_source_2'])
        self.setTriggerOperation(getattr(ats, self._config['trigger_operation']),
                                 getattr(ats, self._config['trigger_engine_1']),
                                 source_1,
                                 getattr(ats, self._config['trigger_slope_1']),
                                 self._config['trigger_level_1'],
                                 getattr(ats, self._config['trigger_engine_2']),
                                 source_2,
                                 getattr(ats, self._config['trigger_slope_2']),
                                 self._config['trigger_level_2'])

    def _config_record(self, metadata):
        """Sets the record size and count on the card"""
        metadata["number_of_points"] = (self._config['pre_trigger_samples']
                                        + self._config['post_trigger_samples'])
        self.setRecordSize(self._config['pre_trigger_samples'],
                           self._config['post_trigger_samples'])
        self.setRecordCount(self._config['records'])

    def _wait_for_trigger(self, timeout=None):
        """Wait for a trigger event until the timeout.

        This method will wait for a trigger event, but will eventually timeout.
        When this happens, it will either raise an error or force a trigger
        event, depending on the input.

        :param timeout: number of seconds to wait for a trigger event
        :type timeout: int

        :raises RuntimeError: if timeout occurs and force is set to False
        """
        if timeout is None:
            timeout = max(10, self._config['records'])
        for _ in range(ceil(timeout / 0.1)):
            if not self.busy():
                break
            if (self._config['trigger_source_1'] == 'TRIG_FORCE'
                    or self._config['trigger_source_2'] == 'TRIG_FORCE'):
                self.forceTrigger()
            sleep(0.1)
        else:
            raise RuntimeError("timeout occurred before card recorded all records")

    def _read_from_card(self):
        """Reads the records from the card memory into the data buffer."""
        pre_trig = self._config['pre_trigger_samples']
        post_trig = self._config['post_trigger_samples']
        transfer_length = pre_trig + post_trig + 16
        records = self._config['records']
        transfer_offset = -(pre_trig)
        data = np.zeros((records, transfer_length), ATSGeneric._data_type)

        for channel_number, analog_input in enumerate(self._analog_inputs):
            channel = analog_input.get_input_channel()
            for i in range(records):
                record_num = i + 1 # 1-indexed
                # read data from card
                self.read(channel,
                          data[i].ctypes.data_as(c_void_p),
                          ATSGeneric._bytes_per_sample,
                          record_num,
                          transfer_offset,
                          transfer_length)
                # save each record if not being averaged
                if self._config['average'] is False:
                    value_data = self._convert_to_values(data[i][:-16])
                    self._data['trace'][0][channel_number][i] = value_data
            # save the average record only if average is requested
            if self._config['average'] is True:
                averaged_record = data.mean(axis=0, dtype=ATSGeneric._data_type)[:-16]
                value_data = self._convert_to_values(averaged_record)
                self._data['trace'][0][channel_number][0] = value_data

    def _convert_to_values(self, data):
        """Convert ATS data into 16-bit integer values for saving.

        :param data: the values read from the ATS card
        :type data: numpy.ndarray

        :returns: 16-bit integers
        :rtype: numpy.ndarray

        :raises NotImplementedError: if bits per sample is out of range
        """
        _, c_bits = self.getChannelInfo()
        bits = c_bits.value
        if not 8 < bits <= 16:
            raise NotImplementedError("bits per sample must be between 9 and 16")
        bit_shift = 16 - bits
        return np.array(data / 2**bit_shift, dtype=ATSGeneric._data_type)

    def _draw_plot(self, socket=None):
        if socket is None:
            plt.ion()
        for channel in self._data['trace'][0]:
            first_record = 0
            plt.plot(channel[first_record].tolist())
        if socket is None:
            plt.pause(0.05)
        else:
            out = mpld3.fig_to_html(plt.gcf())
            thread = Thread(target=send_data_thread, args=(socket, out))
            thread.start()
            thread.join()

class AnalogInput:
    """An Alazar input configuration."""
    def __init__(self, channel, coupling, input_range, impedance):
        self._input_channel = channel
        self._input_coupling = coupling
        self._input_range = input_range
        self._input_impedance = impedance

    def get_input_channel(self):
        """Get the input channel for this input.

        :returns: the constant value of the input channel
        :rtype: int
        """
        return self._input_channel

    def get_input_range(self):
        """Get the input range for this input.

        :returns: the constant value of the input range
        :rtype: int
        """
        return self._input_range

    def initialize_on_board(self, board):
        """Initialize analog input on board.

        :param board: the ATS card to use
        :type board: ATSGeneric
        """
        board.inputControl(self._input_channel,
                           self._input_coupling,
                           self._input_range,
                           self._input_impedance)

class ATS660(ATSGeneric):
    """Subclass for ATS660"""
    pass

class ATS9440(ATSGeneric):
    """Subclass for ATS9440"""
    pass

# Private functions
def _sample_rate_to_hertz(constant):
    """Translate sample rate constant to hertz.

    :param constant: the ATS constant representing the sample rate
    :type constant: int

    :returns: the sample rate, in hertz
    :rtype: int
    """
    return _SAMPLE_RATE_TO_HERTZ[constant]

_SAMPLE_RATE_TO_HERTZ = {
    ats.SAMPLE_RATE_1KSPS:         1000,
    ats.SAMPLE_RATE_2KSPS:         2000,
    ats.SAMPLE_RATE_5KSPS:         5000,
    ats.SAMPLE_RATE_10KSPS:       10000,
    ats.SAMPLE_RATE_20KSPS:       20000,
    ats.SAMPLE_RATE_50KSPS:       50000,
    ats.SAMPLE_RATE_100KSPS:     100000,
    ats.SAMPLE_RATE_200KSPS:     200000,
    ats.SAMPLE_RATE_500KSPS:     500000,
    ats.SAMPLE_RATE_1MSPS:      1000000,
    ats.SAMPLE_RATE_2MSPS:      2000000,
    ats.SAMPLE_RATE_5MSPS:      5000000,
    ats.SAMPLE_RATE_10MSPS:    10000000,
    ats.SAMPLE_RATE_20MSPS:    20000000,
    ats.SAMPLE_RATE_25MSPS:    25000000,
    ats.SAMPLE_RATE_50MSPS:    50000000,
    ats.SAMPLE_RATE_100MSPS:  100000000,
    ats.SAMPLE_RATE_125MSPS:  125000000,
    ats.SAMPLE_RATE_160MSPS:  160000000,
    ats.SAMPLE_RATE_180MSPS:  180000000,
    ats.SAMPLE_RATE_200MSPS:  200000000,
    ats.SAMPLE_RATE_250MSPS:  250000000,
    ats.SAMPLE_RATE_400MSPS:  400000000,
    ats.SAMPLE_RATE_500MSPS:  500000000,
    ats.SAMPLE_RATE_800MSPS:  800000000,
    ats.SAMPLE_RATE_1000MSPS:1000000000,
    ats.SAMPLE_RATE_1200MSPS:1200000000,
    ats.SAMPLE_RATE_1500MSPS:1500000000,
    ats.SAMPLE_RATE_1600MSPS:1600000000,
    ats.SAMPLE_RATE_1800MSPS:1800000000,
    ats.SAMPLE_RATE_2000MSPS:2000000000,
    ats.SAMPLE_RATE_2400MSPS:2400000000,
    ats.SAMPLE_RATE_3000MSPS:3000000000,
    ats.SAMPLE_RATE_3600MSPS:3600000000,
    ats.SAMPLE_RATE_4000MSPS:4000000000,
    }
