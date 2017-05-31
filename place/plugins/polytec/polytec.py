"""The Polytech vibrometer instrument.

This module allows interfacing with Polytec vibrometer OFV-5000
controller and OFV-505 sensor head. Functions based on Polytec
"RS-232 Interface Commands: OFV-5000 User Manual"

**NOTE** For each polytec controller, different decoders may be
installed. The number assigned to each decoder may also vary,
therefore the decoder functions may need to be modified accordingly.
"""
from time import sleep
import re
from serial import Serial
import serial
from place.config import PlaceConfig
from place.plugins.instrument import Instrument

_NUMBER = r'[-+]?\d*\.\d+|\d+'

class Polytec(Instrument):
    """The polytec class"""
    def __init__(self, config):
        """Constructor"""
        Instrument.__init__(self, config)
        self._serial = None
        self._id = '' # must be set by base class

    def config(self, metadata, total_updates):
        """Configure the vibrometer.

        :param metadata: scan metadata
        :type metadata: dict

        :param total_updates: number of updates for the scan
        :type total_updates: int
        """
        self._serial = Serial(
            port=PlaceConfig().get_config_value(__name__, "port"),
            baudrate=PlaceConfig().get_config_value(__name__, "baudrate"),
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        self._set_range(self._config['range'])

        name = self.__class__.__name__

        metadata[name + '_time_delay'] = self._get_delay()
        metadata[name + '_maximum_frequency'] = self._get_maximum_frequency()

        calibration, calibration_units = self._get_range()

        metadata[name + '_calibration'] = calibration
        metadata[name + '_calibration_units'] = calibration_units

        if self._config['autofocus'] != 'Off':
            self._autofocus_vibrometer(
                span=self._config['autofocus'],
                timeout=self._config['timeout'])

    def update(self, update_number, socket=None):
        """Update the vibrometer.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param socket: connection to the plot iframe in the web interface
        :type socket: websocket
        """
        pass

    def cleanup(self, abort=False):
        """Free resources and cleanup.

        :param abort: indicates that the scan is being aborted and is unfinished
        :type abort: bool
        """
        self._serial.close()

# PRIVATE METHODS

    def _write(self, message):
        """Send a message

        :param message: message to be sent to the Polytec receiver
        :type message: str
        """
        self._serial.write(message.encode())

    def _write_and_readline(self, message):
        """Send a message and get a response.

        :param message: message to be sent to the Polytec receiver
        :type message: str

        :returns: the decoded response
        :rtype: str
        """
        self._write(message)
        return self._serial.readline().decode()

    def _autofocus_vibrometer(self, span='Full', timeout=30):
        """Autofocus the vibrometer.

        :param span: the range in which the vibrometer should look for focus
        :type span: str

        :param timeout: the number of seconds to wait for focus before failing
        :type timeout: int

        :raises RuntimeError: if focus is not found before timeout
        """
        self._write('Set,SensorHead,0,AutoFocusSpan,'+span+'\n')
        self._write('Set,SensorHead,0,AutoFocus,Search\n')
        for _ in range(timeout+1):
            if self._write_and_readline('Get,SensorHead,0,AutoFocusResult\n') == 'Found\n':
                break
            sleep(1)
        else:
            raise RuntimeError('autofocus failed')

    def _get_delay(self):
        """Get time delay.

        :raises NotImplementedError: if not implemented by subclass
        """
        raise NotImplementedError

    def _get_maximum_frequency(self):
        """Get the maximum frequency.

        :returns: the frequency value of the selected decoder
        :rtype: float

        :raises NotImplementedError: if not implemented by subclass
        """
        if self._id == '':
            raise NotImplementedError('class self._id is not defined')
        frequency_string = self._write_and_readline('Get,' + self._id + ',MaxFreq\n')
        return _parse_frequency(frequency_string)

    def _get_range(self):
        """Get the current range.

        :returns: the range string returned from the instrument
        :rtype: str

        :raises NotImplementedError: if not implemented by subclass
        """
        if self._id == '':
            raise NotImplementedError('class self._id is not defined')
        decoder_range = self._write_and_readline('Get,' + self._id + ',Range\n')
        range_num = re.findall(_NUMBER, self._config['range'])
        del_num_r = len(range_num)+1
        calib = float(range_num[0])
        calib_unit = decoder_range[del_num_r:].lstrip()
        return calib, calib_unit

    def _set_range(self, range_):
        """Set the range.

        :param range_: the desired decoder range
        :type range_: str

        :raises NotImplementedError: if not implemented by subclass
        """
        if self._id == '':
            raise NotImplementedError('class self._id is not defined')
        self._write('Set,' + self._id + ',Range,' + range_ + '\n')

class DD300(Polytec):
    """DD-300"""
    def __init__(self, config):
        """Constructor"""
        Polytec.__init__(self, config)
        self._id = 'DisplDec,0'

    def _get_delay(self):
        """Get time delay.

        :returns: always returns 0.0
        :rtype: float
        """
        return 0.0

class DD900(Polytec):
    """DD-900"""
    def __init__(self, config):
        """Constructor"""
        Polytec.__init__(self, config)
        self._id = 'DisplDec,1'

    def _get_delay(self):
        """Get time delay.

        :returns: always returns 0.0
        :rtype: float
        """
        return 0.0

class VD08(Polytec):
    """VD-08"""
    def __init__(self, config):
        """Constructor"""
        Polytec.__init__(self, config)
        self._id = 'VeloDec,0'

    def _get_delay(self):
        """Get time delay.

        :returns: signal typical transit time delay for decoder
        :rtype: float
        """
        delay_string = self._write_and_readline('Get,' + self._id + ',SignalDelay\n')
        return float(re.findall(_NUMBER, delay_string)[0])

class VD09(Polytec):
    """VD-09"""
    def __init__(self, config):
        """Constructor"""
        Polytec.__init__(self, config)
        self._id = 'VeloDec,1'

    def _get_delay(self):
        """Get time delay.

        :returns: signal typical transit time delay for decoder
        :rtype: float
        """
        delay_string = self._write_and_readline('Get,' + self._id + ',SignalDelay\n')
        return float(re.findall(_NUMBER, delay_string)[0])

def _parse_frequency(frequency_string):
    """Calculate a frequency from a string.

    Takes a frequency string and parses it to a float value.

    .. doctest::

        >>> _parse_frequency('20MHz')
        20000000.0
        >>> _parse_frequency('5kHz')
        5000.0
        >>> _parse_frequency('16.6mhz')
        16600000.000000002

    :param frequency_string: string to be parsed
    :type frequency_string: str

    :returns: the frequency value
    :rtype: float

    :raises ValueError: if frequency units are not recognized
    """
    num_str, unit_str = re.match(
        r'([-+]?\d*\.\d+|\d+)([kmg]?Hz)',
        frequency_string,
        re.IGNORECASE
        ).groups()
    if unit_str.lower == 'hz':
        return float(num_str)
    elif unit_str.lower == 'khz':
        return float(num_str) * 10**3
    elif unit_str.lower == 'mhz':
        return float(num_str) * 10**6
    elif unit_str.lower == 'ghz':
        return float(num_str) * 10**9
    else:
        raise ValueError('could not parse units in frequency string')
