"""The Polytec vibrometer instrument.

This module allows interfacing with Polytec vibrometers (e.g. OFV-5000 controller and
OFV-505 sensor head). Functions based on Polytec "RS-232 Interface Commands:
OFV-5000 User Manual"

For each polytec controller, different decoders may be installed.
These values should be stored in the your PLACE config file  (~/.place.cfg).
In addition, the port and baudrate are required for each vibrometer.

For example::

    vd_08 = VeloDec,0
    vd_09 = VeloDec,1
    dd_300 = DisplDec,0
    dd_900 = DisplDec,1
    port = /dev/ttyUSB4
    baudrate = 115200

You will need to change these values as needed to suit your requirements.
"""
import ast
import re
from time import sleep

import numpy as np
import serial
from serial import Serial

from place.config import PlaceConfig
from place.plugins.instrument import Instrument

_NUMBER = r'[-+]?\d*\.\d+|\d+'


class Polytec(Instrument):
    """The generic Polytec laser Doppler vibrometer class.

    .. note::
       See the specific vibrometer model classes for further information

    """

    def __init__(self, config, plotter):
        """Constructor"""
        Instrument.__init__(self, config, plotter)
        self._serial = None
        self._signal = None
        self.min_used = None
        self.max_used = None

    def config(self, metadata, total_updates):
        """Configure the vibrometer.

        :param metadata: experiment metadata
        :type metadata: dict

        :param total_updates: number of updates for the experiment
        :type total_updates: int
        """
        name = self.__class__.__name__
        self._serial = Serial(
            port=PlaceConfig().get_config_value(name, "port"),
            baudrate=PlaceConfig().get_config_value(name, "baudrate"),
            timeout=5,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        self.controller_name = self._get_controller_name()
        metadata['polytec_controller'] =  self.controller_name  

        if self.controller_name == "OFV-5000 Vibrometer Controller":
            self.prefixd = 'dd'
            self.prefixv = 'vd'
        elif self.controller_name == "OFV-5000Xtra Vibrometer Controller":
            self.prefixd = 'dx'
            self.prefixv = 'vx'

        if self._config['{}_300'.format(self.prefixd)]:
            self._setup_decoder(metadata, '{}_300'.format(self.prefixd))

        if self._config['{}_900'.format(self.prefixd)]:
            self._setup_decoder(metadata, '{}_900'.format(self.prefixd))

        try:
            if self._config['{}_08'.format(self.prefixv)]:
                self._setup_decoder(metadata, '{}_08'.format(self.prefixv))
        except:
            pass

        if self._config['{}_09'.format(self.prefixv)]:
            self._setup_decoder(metadata, '{}_09'.format(self.prefixv))

        if self._config['autofocus'] == 'custom':
            curr_set = self._write_and_readline(
                'GetDevInfo,SensorHead,0,Focus\n')
            curr_min, curr_max = ast.literal_eval(curr_set)
            self.min_used = max(curr_min, self._config['area_min'])
            self.max_used = min(curr_max, self._config['area_max'])
            metadata['actual_area_min'] = self.min_used
            metadata['actual_area_max'] = self.max_used

    def update(self, update_number, progress):
        """Update the vibrometer.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param progress: a dictionary of values passed back to your Elm app
        :type progress: dict

        :returns: an array containing the signal level
        :rtype: numpy.array dtype='uint64'
        """
        if self._config['autofocus'] != 'none':
            if update_number == 0 or self._config['autofocus_everytime'] is True:
                self._autofocus_vibrometer(
                    span=self._config['autofocus'],
                    timeout=self._config['timeout'])
        signal_level = self._get_signal_level()
        field = '{}-signal'.format(self.__class__.__name__)
        data = np.array([(signal_level,)], dtype=[(field, 'uint64')])
        if self._config['plot']:
            self._draw_plot(signal_level, update_number, progress)
        return data

    def cleanup(self, abort=False):
        """Free resources and cleanup.

        Display the final plot, unless aborted or plotting is disabled.

        :param abort: indicates that the experiment is being aborted and is unfinished
        :type abort: bool
        """
        if abort is False:
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
        return self._serial.readline().decode('ascii', 'replace')

    def _setup_decoder(self, metadata, name):
        """Set the range for the decoder and obtain metadata

        :param metadata: experiment metadata
        :type metadata: dict

        :param name: the name to use for the decoder
        :type name: str
        """
        id_ = PlaceConfig().get_config_value(self.__class__.__name__, name)
        self._set_range(id_, self._config[name + '_range'])
        if name == '{}_08'.format(self.prefixv) or name == '{}_09'.format(self.prefixv):
            metadata[name + '_time_delay'] = self._get_delay(id_)
            metadata[name +
                     '_maximum_frequency'] = self._get_maximum_frequency(id_)
        calibration, calibration_units = self._get_range(name, id_)
        metadata[name + '_calibration'] = calibration
        metadata[name + '_calibration_units'] = calibration_units

    def _autofocus_vibrometer(self, span='Full', timeout=30):
        """Autofocus the vibrometer.

        :param span: the range in which the vibrometer should look for focus
        :type span: str

        :param timeout: the number of seconds to wait for focus before failing
        :type timeout: int

        :raises RuntimeError: if focus is not found before timeout
        """

        if self._config['autofocus'] == 'custom':
            self._write('Set,SensorHead,0,AutoFocusArea,{},{}\n'.format(
                self.min_used, self.max_used))
        else:
            self._write('Set,SensorHead,0,AutoFocusSpan,'+span+'\n')

        self._write('Set,SensorHead,0,AutoFocus,Search\n')
        countdown = timeout
        tick = 1
        while countdown > 0:
            sleep(tick)
            countdown -= tick
            if self._write_and_readline('Get,SensorHead,0,AutoFocusResult\n') == 'Found\n':
                break
        else:
            print("Polytec: Autofocus failed. Continuing.")
            #raise RuntimeError('autofocus failed')

    def _get_delay(self, id_):
        """Get time delay.

        :param id_: the identification string for the decoder
        :type id_: str

        :returns: the delay time
        :rtype: float
        """
        delay_string = self._write_and_readline(
            'Get,' + id_ + ',SignalDelay\n')
        return float(re.findall(_NUMBER, delay_string)[0])

    def _get_controller_name(self):
        """Get the name of the controller.

        :returns: the name of the controller
        :rtype: string
        """
        controller_string = self._write_and_readline(
            'GetDevInfo,Controller,0,Name\n')
        name = controller_string[:-1]
        if name != '':
            return name
        else:
            raise RuntimeError('Polytec controller name could not be found. This might be a connection problem.')

    def _get_maximum_frequency(self, id_):
        """Get the maximum frequency.

        :param id_: the identification string for the decoder
        :type id_: str

        :returns: the frequency value of the selected decoder
        :rtype: float

        :raises ValueError: if maximum frequency is not available
        """
        frequency_string = self._write_and_readline(
            'Get,' + id_ + ',MaxFreq\n')
        if frequency_string == 'Not Available':
            raise ValueError(
                'maximum frequency for {} not available'.format(id_))
        return _parse_frequency(frequency_string)

    def _get_range(self, name, id_):
        """Get the current range.

        :param name: the name for the decoder
        :type name: str

        :param id_: the identification string for the decoder
        :type id_: str

        :returns: the range value and units returned from the instrument
        :rtype: float, string

        :raises ValueError: if decoder name is not recognized
        """
        decoder_range = self._write_and_readline('Get,' + id_ + ',Range\n')
        if name == '{}_300'.format(self.prefixd):
            range_num = re.findall(_NUMBER, self._config['{}_300_range'.format(self.prefixd)])
        elif name == '{}_900'.format(self.prefixd):
            raw_num = re.findall(_NUMBER, self._config['{}_900_range'.format(self.prefixd)])
            range_num = [string.replace('um', 'µm') for string in raw_num]
        elif name == '{}_08'.format(self.prefixv):
            range_num = re.findall(_NUMBER, self._config['{}_08_range'.format(self.prefixv)])
        elif name == '{}_09'.format(self.prefixv):
            range_num = re.findall(_NUMBER, self._config['{}_09_range'.format(self.prefixv)])
        else:
            raise ValueError('unknown decoder: ' + name)
        del_num_r = len(range_num)+1
        calib = float(range_num[0])
        calib_unit = decoder_range[del_num_r:].lstrip()
        return calib, calib_unit

    def _set_range(self, id_, range_):
        """Set the range.

        :param id_: the identification string for the decoder
        :type id_: str

        :param range_: the desired decoder range
        :type range_: str
        """
        self._write('Set,' + id_ + ',Range,' + range_ + '\n')

    def _get_signal_level(self):
        return int(self._write_and_readline('Get,SignalLevel,0,Value\n'))

    def _draw_plot(self, signal_level, update_number, progress):
        if update_number == 0:
            self._signal = [signal_level]
        else:
            self._signal.append(signal_level)
        title = 'Signal level at each PLACE update'
        self.plotter.view(
            title,
            [
                self.plotter.line(
                    self._signal,
                    color='purple',
                    shape='cross',
                    label='signal'
                )
            ]
        )
        # TODO: add axis labels when PLACE supports it
        # plt.xlabel('trace')
        # plt.ylabel('signal level')

class OFV5000(Polytec):
    """The Polytec OFV-5000 laser Doppler vibrometer class. This class
    inherits all the methods from the generic Polytec class.

    This module requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    dd_300                    bool           flag indicating use of the DD-300
    dd_300_range              string         the range of DD-300
    dd_900                    bool           flag indicating use of the DD-900
    dd_900_range              string         the range of DD-900
    vd_08                     bool           flag indicating use of the VD-08
    vd_08_range               string         the range of VD-08
    vd_09                     bool           flag indicating use of the VD-09
    vd_09_range               string         the range of VD-09
    autofocus                 string         the type of autofocus span
    area_min                  int            the minimum autofocus range (if specified)
    area_max                  int            the maximum autofocus range (if specified)
    autofocus_everytime       bool           flag indicating if autofocus should be
                                             performed at every update
    timeout                   float          number of seconds to wait for autofocus
    plot                      bool           turns live plotting on or off
    ========================= ============== ================================================

    The Polytec module will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    actual_area_min           int            the actual minimum autofocus range used
    actual_area_max           int            the actual maximum autofocus range used
    vd_08_time_delay          float          the decoder time delay (if used)
    vd_08_maximum_frequency   float          the decoder maximum frequency (if used)
    vd_09_time_delay          float          the decoder time delay (if used)
    vd_09_maximum_frequency   float          the decoder maximum frequency (if used)
    dd_300_calibration        float          the decoder calibration (if used)
    dd_300_calibration_units  string         the decoder units (if used)
    dd_900_calibration        float          the decoder calibration (if used)
    dd_900_calibration_units  string         the decoder units (if used)
    vd_08_calibration         float          the decoder calibration (if used)
    vd_08_calibration_units   string         the decoder units (if used)
    vd_09_calibration         float          the decoder calibration (if used)
    vd_09_calibration_units   string         the decoder units (if used)
    ========================= ============== ================================================

    This module will produce the following experimental data:

    +---------------+-------------------------+---------------------------+
    | Heading       | Type                    | Meaning                   |
    +===============+=========================+===========================+
    | signal        | uint64                  | the signal level recorded |
    |               |                         | from the vibrometer       |
    +---------------+-------------------------+---------------------------+

    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``signal`` will be recorded as ``OFV5000-signal`` when using
        the OFV5000 vibrometer. The reason for this is because NumPy will not
        check for duplicate heading names automatically, so prepending the
        class name greatly reduces the likelihood of duplication.

    """
    
    def serial_port_query(self, serial_port, field_name):
        """Query if the instrument is connected to serial_port

        :param serial_port: the serial port to query
        :type serial_port: string

        :returns: whether or not serial_port is the correct port
        :rtype: bool
        """

        try:
            for i in range(2):
                with Serial(
                    port=serial_port,
                    baudrate=115200,
                    timeout=0.5,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS) as _serial:
                
                    message = 'GetDevInfo,Controller,0,Name\n'
                    _serial.write(message.encode())
                    response = _serial.read_until().decode('ascii', 'replace')
                if "OFV-5000" in response and "X" not in response:
                    break
            else:
                return False
            return True
        except (serial.SerialException, serial.SerialTimeoutException):
            return False


class OFV5000X(Polytec):
    """The Polytec OFV-5000X laser Doppler vibrometer class. This class
    inherits all the methods from the generic Polytec class.

    This module requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    dx_300                    bool           flag indicating use of the DX-300
    dx_300_range              string         the range of DX-300
    dx_900                    bool           flag indicating use of the DX-900
    dx_900_range              string         the range of DX-900
    vx_09                     bool           flag indicating use of the VX-09
    vx_09_range               string         the range of VX-09
    autofocus                 string         the type of autofocus span
    area_min                  int            the minimum autofocus range (if specified)
    area_max                  int            the maximum autofocus range (if specified)
    autofocus_everytime       bool           flag indicating if autofocus should be
                                             performed at every update
    timeout                   float          number of seconds to wait for autofocus
    plot                      bool           turns live plotting on or off
    ========================= ============== ================================================

    The OFV5000X module will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    actual_area_min           int            the actual minimum autofocus range used
    actual_area_max           int            the actual maximum autofocus range used
    vx_09_time_delay          float          the decoder time delay (if used)
    vx_09_maximum_frequency   float          the decoder maximum frequency (if used)
    dx_300_calibration        float          the decoder calibration (if used)
    dx_300_calibration_units  string         the decoder units (if used)
    dx_900_calibration        float          the decoder calibration (if used)
    dx_900_calibration_units  string         the decoder units (if used)
    vx_08_calibration         float          the decoder calibration (if used)
    vx_08_calibration_units   string         the decoder units (if used)
    vx_09_calibration         float          the decoder calibration (if used)
    vx_09_calibration_units   string         the decoder units (if used)
    ========================= ============== ================================================

    This module will produce the following experimental data:

    +---------------+-------------------------+---------------------------+
    | Heading       | Type                    | Meaning                   |
    +===============+=========================+===========================+
    | signal        | uint64                  | the signal level recorded |
    |               |                         | from the vibrometer       |
    +---------------+-------------------------+---------------------------+

    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``signal`` will be recorded as ``OFV5000X-signal`` when using
        the OFV5000X vibrometer. The reason for this is because NumPy will not
        check for duplicate heading names automatically, so prepending the
        class name greatly reduces the likelihood of duplication.

    """

    def serial_port_query(self, serial_port, field_name):
        """Query if the instrument is connected to serial_port

        :param serial_port: the serial port to query
        :type serial_port: string

        :returns: whether or not serial_port is the correct port
        :rtype: bool
        """
        
        try:
            for i in range(2):
                with Serial(
                    port=serial_port,
                    baudrate=115200,
                    timeout=0.5,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS) as _serial:
                
                    message = 'GetDevInfo,Controller,0,Name\n'
                    _serial.write(message.encode())
                    response = _serial.read_until().decode('ascii', 'replace')
                if "OFV-5000X" in response:
                    break
            else:
                return False
            return True
        except (serial.SerialException, serial.SerialTimeoutException):
            return False


def _parse_frequency(frequency_string):
    """Calculate a frequency from a string.

    Takes a frequency string and parses it to a float value.

    .. doctest::

        >>> _parse_frequency('20MHz')
        20000000.0
        >>> _parse_frequency('20 MHz')
        20000000.0
        >>> _parse_frequency('5kHz')
        5000.0
        >>> _parse_frequency('16.6mhz')
        16600000.000000002
        >>> _parse_frequency('16.6 mhz')
        16600000.000000002

    :param frequency_string: string to be parsed
    :type frequency_string: str

    :returns: the frequency value
    :rtype: float

    :raises ValueError: if frequency units are not recognized
    """
    re_match = re.match(
        r'([-+]?\d*\.\d+|\d+)\s?([kmg]?Hz)',
        frequency_string,
        flags=re.IGNORECASE  # pylint: disable=no-member
    )
    if re_match is None:
        raise ValueError(
            'could not parse frequency string: ' + frequency_string)
    else:
        num_str, unit_str = re_match.groups()
    if unit_str.lower() == 'hz':
        return float(num_str)
    elif unit_str.lower() == 'khz':
        return float(num_str) * 10**3
    elif unit_str.lower() == 'mhz':
        return float(num_str) * 10**6
    elif unit_str.lower() == 'ghz':
        return float(num_str) * 10**9
    else:
        raise ValueError('could not match units of frequency: ' + unit_str)
