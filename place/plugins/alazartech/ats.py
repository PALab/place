"""PLACE module to control AlazarTech cards"""
import json
from time import sleep
from ctypes import cdll, c_void_p
import numpy as np

from . import atsapi as ats

class ATSGeneric(ats.Board):
    """Class which supports all Alazar controllers.

    This class should be overridden if classes are needed for specific cards.

    Note: This class currently only supports boards providing data in an
    unsigned, 2 bytes per sample, format. It should support 12, 14, and 16 bits
    per sample. If 8 bits per sample is desired, that functionality will need
    to be added to this class.
    """
    _libc = cdll.LoadLibrary('libc.so.6')
    _bytes_per_sample = 2
    _data_type = np.dtype('<u'+str(_bytes_per_sample)) # (<)little-endian, (u)unsigned

    def __init__(self, system_id=1, board_id=1):
        """Constructor

        :param system_id: system to address
        :type system_id: int

        :param board_id: board to address
        :type board_id: int
        """
        super(ATSGeneric, self).__init__(system_id, board_id)
        self._config = None
        self._analog_inputs = None

    # Public methods
    def config(self, config_string):
        """Configure the Alazar card

        This method is responsible for reading all the data from the
        configuration input and setting up the card for scanning.

        From the ATS-SDK-Guide...
            "Before acquiring data from a board system, an application must
            configure the timebase, analog inputs, and trigger system settings
            for each board in the board system."

        After configuring the board, this method also performs the first data
        acquisition steps by setting the record size and the record count.

        :param config_string: the JSON-formatted configuration
        :type config_string: str

        :raises NotImplementedError: if the number of bits per sample is out of range
        """
        # store JSON data
        self._config = json.loads(config_string)
        # execute configuration commands on the card
        self._config_timebase()
        self._config_analog_inputs()
        self._config_trigger_system()
        self.setRecordSize(self._config['pre_trigger_samples'],
                           self._config['post_trigger_samples'])
        self.setRecordCount(1)

    def update(self):
        """Record a trace using the current configuration"""
        self.startCapture()
        self._wait_for_trigger()
        for analog_input in self._analog_inputs:
            record = analog_input.get_record()
            channel = analog_input.channel
            self._read_to_record(record, channel)
            max_volts = _input_range_to_volts(analog_input.input_range)
            volt_data = self._convert_to_volts(record, max_volts)
            print(volt_data)

    def cleanup(self):
        """Free any resources used by card"""
        pass

    # Private methods
    def _config_timebase(self):
        """Sets the capture clock"""
        self.setCaptureClock(getattr(ats, self._config['clock_source']),
                             getattr(ats, self._config['sample_rate']),
                             getattr(ats, self._config['clock_edge']),
                             self._config['decimation'])

    def _config_analog_inputs(self):
        """Specify the desired input range, termination, and coupling of an
        input channel
        """
        pre_trig = self._config['pre_trigger_samples']
        post_trig = self._config['post_trigger_samples']
        samples = pre_trig + post_trig
        self._analog_inputs = []
        for input_data in self._config['analog_inputs']:
            analog_input = AnalogInput(getattr(ats, input_data['input_channel']),
                                       getattr(ats, input_data['input_coupling']),
                                       getattr(ats, input_data['input_range']),
                                       getattr(ats, input_data['input_impedance']))
            analog_input.set_record(np.ndarray(samples, ATSGeneric._data_type))
            analog_input.initialize_on_board(self)
            self._analog_inputs.append(analog_input)

    def _config_trigger_system(self):
        """Configure each of the two trigger engines"""
        self.setTriggerOperation(getattr(ats, self._config['trigger_operation']),
                                 getattr(ats, self._config['trigger_engine_1']),
                                 getattr(ats, self._config['trigger_source_1']),
                                 getattr(ats, self._config['trigger_slope_1']),
                                 self._config['trigger_level_1'],
                                 getattr(ats, self._config['trigger_engine_2']),
                                 getattr(ats, self._config['trigger_source_2']),
                                 getattr(ats, self._config['trigger_slope_2']),
                                 self._config['trigger_level_2'])

    def _wait_for_trigger(self, timeout=30, force=False):
        """Wait for a trigger event until the timeout.

        This method will wait for a trigger event, but will eventually timeout.
        When this happens, it will either raise an error or force a trigger
        event, depending on the input.

        :param timeout: number of seconds to wait for a trigger event
        :type timeout: int

        :param force: if true, will perform a software trigger if timeout occurs
        :type force: bool

        :raises RuntimeError: if timeout occurs and force is set to False
        """
        for _ in range(timeout):
            if not self.busy():
                break
            sleep(0.1)
        else:
            if force:
                self.forceTrigger()
                while self.busy():
                    sleep(0.1)
            else:
                raise RuntimeError("Trigger event never occurred")

    def _read_to_record(self, record, channel):
        """Reads the last record from the card memory into the data buffer.

        :param record: the buffer to copy data into
        :type record: numpy.ndarray

        :param channel: ATS constant associated with the desired input
        :type channel: int

        :raises ValueError: if data record buffer is None
        """
        if record is None:
            raise ValueError("no buffer is associated with this input")
        # parameters
        record_num = 1
        transfer_offset = 0
        transfer_length = record.size
        # read data from card
        self.read(channel,
                  record.ctypes.data_as(c_void_p),
                  ATSGeneric._bytes_per_sample,
                  record_num,
                  transfer_offset,
                  transfer_length)

    def _convert_to_volts(self, data, max_volts):
        """Convert ATS data to voltages.

        Data is converted to voltages using the method described in the
        ATS-SDK-Guide.

        :param data: the values read from the ATS card
        :type data: numpy.ndarray

        :param max_volts: the max voltage for the input range
        :type max_volts: float

        :returns: voltages
        :rtype: numpy.ndarray

        :raises NotImplementedError: if bits per sample is out of range
        """
        _, bits = self.getChannelInfo()
        if not 8 < bits <= 16:
            raise NotImplementedError("bits per sample must be between 9 and 16")
        bit_shift = 16 - bits
        midpoint = (1 << (bits - 1)) - 0.5
        convert_to_voltages = np.vectorize(
            lambda x: max_volts * ((x >> bit_shift) - midpoint) / midpoint,
            otypes=[np.float]
            )
        return convert_to_voltages(np.copy(data))

class AnalogInput:
    """An Alazar input configuration."""
    def __init__(self, channel, coupling, input_range, impedance):
        self._input_channel = channel
        self._input_coupling = coupling
        self._input_range = input_range
        self._input_impedance = impedance
        self._record = None

    def get_record(self):
        """Get the record associated with this input.

        :returns: the data buffer for this input
        :rtype: numpy.ndarray
        """
        return self._record

    def set_record(self, record):
        """Set the record associated with this input.

        :param record: the data buffer for this input
        :type record: numpy.ndarray
        """
        self._record = record

    def initialize_on_board(self, board):
        """Initialize analog input on board.

        :param board: the ATS card to use
        :type board: ATSGeneric
        """
        board(self._input_channel,
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
def _input_range_to_volts(constant):
    """Translate input range constants

    :param constant: the ATS constant representing the input range
    :type constant: int

    :returns: maximum voltage for the given input range
    :rtype: float
    """
    return _INPUT_RANGE_TO_VOLTS[constant]

_INPUT_RANGE_TO_VOLTS = {
    ats.INPUT_RANGE_PM_40_MV: 0.040,
    ats.INPUT_RANGE_PM_50_MV: 0.050,
    ats.INPUT_RANGE_PM_80_MV: 0.080,
    ats.INPUT_RANGE_PM_100_MV:0.100,
    ats.INPUT_RANGE_PM_125_MV:0.125,
    ats.INPUT_RANGE_PM_200_MV:0.200,
    ats.INPUT_RANGE_PM_250_MV:0.250,
    ats.INPUT_RANGE_PM_400_MV:0.400,
    ats.INPUT_RANGE_PM_500_MV:0.500,
    ats.INPUT_RANGE_PM_800_MV:0.800,
    ats.INPUT_RANGE_PM_1_V:   1.000,
    ats.INPUT_RANGE_PM_1_V_25:1.250,
    ats.INPUT_RANGE_PM_2_V:   2.000,
    ats.INPUT_RANGE_PM_2_V_5: 2.500,
    ats.INPUT_RANGE_PM_4_V:   4.000,
    ats.INPUT_RANGE_PM_5_V:   5.000,
    ats.INPUT_RANGE_PM_8_V:   8.000,
    ats.INPUT_RANGE_PM_10_V: 10.000,
    ats.INPUT_RANGE_PM_16_V: 16.000,
    ats.INPUT_RANGE_PM_20_V: 20.000,
    ats.INPUT_RANGE_PM_40_V: 40.000
    }
