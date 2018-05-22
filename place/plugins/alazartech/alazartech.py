"""PLACE module for the AlazarTech ATS660 and ATS9440 oscilloscope cards.

Oscilloscopes are at the heart of many data acquisition experiments and contain
many configuration options. At the time of this writing, this PLACE module is
by far the most complex. However, even though it is complex, it still follows
the basic PLACE philosophy of config/update/cleanup.

This module can be used as an example for how to program complex instruments
into the PLACE system.
"""
from math import ceil
from time import sleep
from ctypes import c_void_p
import matplotlib.pyplot as plt
import numpy as np

from place.plugins.instrument import Instrument
try:
    from . import atsapi as ats
except OSError:
    from . import dummy_atsapi as ats
setattr(ats, 'TRIG_FORCE', -1)

class ATSGeneric(Instrument, ats.Board):
    """Generic AlazarTech oscillscope card.

    All AlazarTech cards use the same underlying driver. This class provides
    access to these universal features. This class should be overridden if
    classes are needed for specific cards.

    .. note::

        This class currently only supports boards providing data in an
        unsigned, 2 bytes per sample, format. It should support 12, 14, and
        16-bits per sample.  If 8-bits per sample is desired, functionality
        will need to be added to this class.

    AlazarTech requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    clock_source              string         the timing clock to use
                                             (must name a constant from the ATS driver file)
    clock_edge                string         the edge of the clock signal to use
                                             (must name a constant from the ATS driver file)
    trigger_operation         string         how the trigger engine signals are joined
                                             (must name a constant from the ATS driver file)
    trigger_engine_1          string         the first trigger engine to use
                                             (must name a constant from the ATS driver file)
    trigger_source_1          string         the source of the first trigger
                                             (must name a constant from the ATS driver file)
    trigger_slope_1           string         the signal slope that the first trigger
                                             responds to
    trigger_level_1           int            the signal level of the first trigger, where
                                             ``128`` is near 0 volts, ``0`` is the minimun
                                             input range, and ``255`` is the maximum input
                                             range
                                             (must name a constant from the ATS driver file)
    trigger_engine_2          string         the second trigger engine to use
                                             (must name a constant from the ATS driver file)
    trigger_source_2          string         the source of the second trigger
                                             (must name a constant from the ATS driver file)
    trigger_slope_2           string         the signal slope that the second trigger
                                             responds to
                                             (must name a constant from the ATS driver file)
    trigger_level_2           int            the signal level of the second trigger, where
                                             ``128`` is near 0 volts, ``0`` is the minimun
                                             input range, and ``255`` is the maximum input
                                             range
    pre_trigger_samples       int            number of samples to return prior to the trigger
    post_trigger_samples      int            number of samples to return after the trigger
    records                   int            the number of records to acquire (per update)
    average                   bool           ``True`` if records should be averaged into one
    sample_rate               string         the sample rate to be used on the card
                                             (must name a constant from the ATS driver file)
    decimation                int            a decimation factor for the signal
    plot                      string         ``'yes'`` if plotting should occur
    analog_inputs             list           configuration data for the input channels
                                             (see the ``AnalogInput`` class for more info)
    ========================= ============== ================================================

    AlazarTech will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    bits_per_sample           int            the bits resolution of samples taken
    samples_per_record        int            the number of samples in each record saved by
                                             PLACE
    sampling_rate             int            the integer calculation of the sampling rate
                                             (in samples/second)
    ========================= ============== ================================================

    AlazarTech will produce the following experimental data:

    +---------------+-------------------------+-------------------------+
    | Heading       | Type                    | Meaning                 |
    +===============+=========================+=========================+
    | trace         | (channel,record,sample) | the trace data recorded |
    |               | array of uint16         | on the oscilloscope     |
    +---------------+-------------------------+-------------------------+

    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``trace`` will be recorded as ``ATS9440-trace`` when using the
        ATS9440 oscilloscope card. The reason for this is because NumPy will
        not check for duplicate heading names automatically so prepending the
        class name greatly reduces the likelihood of duplication.

    Example code for reading AlazarTech data from a PLACE .npy file::

        import numpy as np
        with open('scan_data_000.npy', 'rb') as f:
            data = np.load(f)
        heading = 'ATS660-trace'
        row = 0
        alazartech_data = data[heading][row]
        channel = 0
        record = 0
        sample = 9
        sample10 = alazartech_data[channel][record][sample]

    In this example, we are looking at the data in a file named
    ``scan_data_000.npy``. This file is created after the first update in a
    PLACE experiment and contains one row of data. The AlazarTech data is
    therefore located in the column named ``'ATS660-trace'`` and row ``0``.
    From there, we can examine the data as desired.
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
        self._updates = None
        self._analog_inputs = None
        self._data = None
        self._samples = None
        self._sample_rate = None

    def config(self, metadata, total_updates):
        """Configure the AlazarTech oscilliscope card.

        This method is responsible for reading configuration date from
        ``self._config`` and using this data to configure the oscilloscope card
        for data acquisition. We mirror the steps suggested by the SDK Guide:

        .. epigraph::

            "*Before acquiring data from a board system, an application must
            configure the timebase, analog inputs, and trigger system settings
            for each board in the board system.*"

            -- ATS SDK Guide

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
        self._updates = total_updates
        # execute configuration commands on the card
        self._config_timebase(metadata)
        self._config_analog_inputs()
        self._config_trigger_system()
        self._config_record()
        _, c_bits = self.getChannelInfo()
        metadata['bits_per_sample'] = c_bits.value
        self._samples = (self._config['pre_trigger_samples']
                         + self._config['post_trigger_samples'])
        metadata['samples_per_record'] = self._samples
        if self._config['plot'] == 'yes':
            plt.figure(self.__class__.__name__)
            plt.clf()
            plt.ion()

    def update(self, update_number):
        """Record a trace using the current configuration.

        :param update_number: This will be the current update number (starting
                              with 0) of the experiment. Instruments could
                              certainly count the number of updates themselves,
                              but this is provided as a convenience.
        :type update_number: int

        :returns: a multi-dimensional array containing the channel, record, and
                  sample data.
        :rtype: numpy.array dtype='(*number_channels*, *number_records*,
                *number_samples*)uint16'
        """
        # build data array
        channels = len(self._config['analog_inputs'])
        if self._config['average']:
            records = 1
        else:
            records = self._config['records']
        type_str = '({},{},{}){}'.format(channels,
                                         records,
                                         self._samples,
                                         ATSGeneric._data_type)
        field = '{}-trace'.format(self.__class__.__name__)
        self._data = np.zeros((1,), dtype=[(field, type_str)])
        self.startCapture()
        self._wait_for_trigger()
        self._read_from_card()
        if self._config['plot'] == 'yes':
            plt.figure(self.__class__.__name__)
            self._draw_plot(update_number)
        return self._data.copy()

    def cleanup(self, abort=False):
        """Display the final plot, unless aborted or plotting is disabled.

        :param abort: indicates the scan has been stopped rather than having
                      finished normally
        :type abort: bool
        """
        if abort is False and self._config['plot'] == 'yes':
            plt.figure(self.__class__.__name__)
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()

    def _config_timebase(self, metadata):
        """Sets the capture clock"""
        sample_rate = getattr(ats, self._config['sample_rate'])
        self._sample_rate = _sample_rate_to_hertz(sample_rate)
        metadata["sampling_rate"] = self._sample_rate
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
            #pylint: disable=protected-access
            analog_input._initialize_on_board(self)
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

    def _config_record(self):
        """Sets the record size and count on the card"""
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
            #pylint: disable=protected-access
            channel = analog_input._get_input_channel()
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
                    field = '{}-trace'.format(self.__class__.__name__)
                    self._data[field][0][channel_number][i] = value_data
            # save the average record only if average is requested
            if self._config['average'] is True:
                averaged_record = data.mean(axis=0)[:-16]
                value_data = self._convert_to_values(averaged_record)
                field = '{}-trace'.format(self.__class__.__name__)
                self._data[field][0][channel_number][0] = value_data

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

    def _draw_plot(self, update_number):
        pre_trig = self._config['pre_trigger_samples']
        post_trig = self._config['post_trigger_samples']
        first_record = 0
        usec_delta = 1000000.0 / self._sample_rate
        times = np.arange(-(pre_trig), post_trig) * usec_delta
        num_channels = len(self._data['{}-trace'.format(self.__class__.__name__)][0])
        _, c_bits = self.getChannelInfo()
        bits = c_bits.value

        for i, channel in enumerate(self._data['{}-trace'.format(self.__class__.__name__)][0]):
            plt.subplot(2, num_channels, i + 1)
            plt.cla()
            plt.plot(times,
                     channel[first_record],
                     label=self._config['analog_inputs'][i]['input_channel'])
            plt.xlabel(r'$\mu$secs')
            plt.ylim((0, 2**bits))
            plt.title('Update {:03}'.format(update_number))
            plt.tight_layout()
            plt.pause(0.05)

            plt.subplot(2, num_channels, i + 1 + num_channels)
            axes = plt.gca()
            trace = channel[first_record] / 2**(bits-1) + update_number - 1
            axes.plot(trace, times, color='black', linewidth=0.5)
            axes.fill_betweenx(
                times,
                trace,
                update_number,
                where=trace > update_number,
                color='black')
            plt.xlim((-1, self._updates))
            plt.xlabel('Update Number')
            plt.ylabel(r'$\mu$secs')
            plt.tight_layout()
            plt.pause(0.05)



class AnalogInput:
    #pylint: disable=too-few-public-methods
    """Class describing a specific input (channel) on the AlazarTech card.

    Each AlazarTech card can have many input channels. Instead of maintaining
    configuration data for all inputs, we dynamically create configuration
    objects containing the data for just one input. This data is provided as a
    list of configurations in the AlazarTech configuration data.

    AnalogInput requires the following configuration data (found in
    ``self._config['analog_inputs']`` and passed to the constructor):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    input_channel             string         the channel associated with this input
                                             (must name a constant from the ATS driver file)
    input_coupling            string         AC or DC coupling
                                             (must name a constant from the ATS driver file)
    input_range               string         the voltage input range
                                             (must name a constant from the ATS driver file)
    input_impedance           string         the selected impedance for the input
                                             (must name a constant from the ATS driver file)
    ========================= ============== ================================================
    """
    def __init__(self, channel, coupling, input_range, impedance):
        self._input_channel = channel
        self._input_coupling = coupling
        self._input_range = input_range
        self._input_impedance = impedance

    def _get_input_channel(self):
        """Get the input channel for this input.

        :returns: the constant value of the input channel
        :rtype: int
        """
        return self._input_channel

    def _get_input_range(self):
        """Get the input range for this input.

        :returns: the constant value of the input range
        :rtype: int
        """
        return self._input_range

    def _initialize_on_board(self, board):
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
