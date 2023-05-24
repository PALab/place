"""Driver for accessing the features of the SR560 pre-amp"""
from time import sleep
import serial

class SR560Driver:
    """Class for lower level access to the pre-amp settings"""
    def __init__(self, serial_port):
        self._serial_port = serial_port
        self._set('LALL') # make pre-amp listen

    def set_blanking(self, blanked):
        """Operates amplifier blanking"""
        cmd = {
            'not blanked': 'BLINK 0',
            'blanked': 'BLINK 1'
            }
        try:
            self._set(cmd[blanked])
        except KeyError:
            raise RuntimeError('Invalid blanking value: {}'.format(blanked))

    def set_coupling(self, coupling):
        """Sets input coupling"""
        cmd = {
            'ground': 'CPLG0',
            'DC': 'CPLG1',
            'AC': 'CPLG2'
            }
        try:
            self._set(cmd[coupling])
        except KeyError:
            raise RuntimeError('Invalid coupling value: {}'.format(coupling))

    def set_reserve(self, dynamic_reserve):
        """Sets dynamic reserve"""
        cmd = {
            'low noise': 'DYNR 0',
            'high DR': 'DYNR 1',
            'calibration gains': 'DYNR 2'
            }
        try:
            self._set(cmd[dynamic_reserve])
        except KeyError:
            raise RuntimeError('Invalid dynamic reserve value: {}'.format(dynamic_reserve))

    def set_filter_mode(self, filter_mode):
        """Sets filter mode"""
        cmd = {
            'bypass': 'FLTM 0',
            '6 dB low pass': 'FLTM 1',
            '12 dB low pass': 'FLTM 2',
            '6 dB high pass': 'FLTM 3',
            '12 dB high pass': 'FLTM 4',
            'bandpass': 'FLTM 5'
            }
        try:
            self._set(cmd[filter_mode])
        except KeyError:
            raise RuntimeError('Invalid filter mode value: {}'.format(filter_mode))

    def set_gain(self, gain):
        """Sets the gain"""
        cmd = {
            '1': 'GAIN 0',
            '2': 'GAIN 1',
            '5': 'GAIN 2',
            '10': 'GAIN 3',
            '20': 'GAIN 4',
            '50': 'GAIN 5',
            '100': 'GAIN 6',
            '200': 'GAIN 7',
            '500': 'GAIN 8',
            '1 k': 'GAIN 9',
            '2 k': 'GAIN 10',
            '5 k': 'GAIN 11',
            '10 k': 'GAIN 12',
            '20 k': 'GAIN 13',
            '50 k': 'GAIN 14'
            }
        try:
            self._set(cmd[gain])
        except KeyError:
            raise RuntimeError('Invalid gain value: {}'.format(gain))

    def set_highpass_filter(self, highpass_filter):
        """Sets highpass filter frequency"""
        cmd = {
            '0.03 Hz': 'HFRQ0',
            '0.1 Hz': 'HFRQ1',
            '0.3 Hz': 'HFRQ2',
            '1 Hz': 'HFRQ3',
            '3 Hz': 'HFRQ4',
            '10 Hz': 'HFRQ5',
            '30 Hz': 'HFRQ6',
            '100 Hz': 'HFRQ7',
            '300 Hz': 'HFRQ8',
            '1 kHz': 'HFRQ9',
            '3 kHz': 'HFRQ10',
            '10 kHz': 'HFRQ11'
            }
        try:
            self._set(cmd[highpass_filter])
        except KeyError:
            raise RuntimeError('Invalid highpass filter value: {}'.format(highpass_filter))

    def set_lowpass_filter(self, lowpass_filter):
        """Sets the lowpass filter frequency"""
        cmd = {
            '0.03 Hz': 'LFRQ 0',
            '0.1 Hz': 'LFRQ 1',
            '0.3 Hz': 'LFRQ 2',
            '1 Hz': 'LFRQ 3',
            '3 Hz': 'LFRQ 4',
            '10 Hz': 'LFRQ 5',
            '30 Hz': 'LFRQ 6',
            '100 Hz': 'LFRQ 7',
            '300 Hz': 'LFRQ 8',
            '1 kHz': 'LFRQ 9',
            '3 kHz': 'LFRQ 10',
            '10 kHz': 'LFRQ 11',
            '30 kHz': 'LFRQ 12',
            '100 kHz': 'LFRQ 13',
            '300 kHz': 'LFRQ 14',
            '1 MHz': 'LFRQ 15'
            }
        try:
            self._set(cmd[lowpass_filter])
        except KeyError:
            raise RuntimeError('Invalid lowpass filter value: {}'.format(lowpass_filter))

    def set_signal_invert_sense(self, signal_invert_sense):
        """Sets the signal invert sense"""
        cmd = {
            'non-inverted': 'INVT 0',
            'inverted': 'INVT 1'
            }
        try:
            self._set(cmd[signal_invert_sense])
        except KeyError:
            raise RuntimeError(
                'Invalid signal invert sense value: {}'.format(signal_invert_sense))

    def set_input_source(self, input_source):
        """Sets the input source"""
        cmd = {
            'A': 'SRCE 0',
            'A-B': 'SRCE 1',
            'B': 'SRCE 2'
            }
        try:
            self._set(cmd[input_source])
        except KeyError:
            raise RuntimeError('Invalid input soruce value: {}'.format(input_source))

    def set_vernier_gain_status(self, vernier_gain_status):
        """Sets the vernier gain status"""
        cmd = {
            "calibrated gain": 'UCAL 0',
            'vernier gain': 'UCAL 1'
            }
        try:
            self._set(cmd[vernier_gain_status])
        except KeyError:
            raise RuntimeError(
                'Invalid vernier gain status value: {}'.format(vernier_gain_status))

    def set_vernier_gain(self, vernier_gain):
        """Sets to vernier gain"""
        self._set('UCGN {}'.format(vernier_gain))

    def set_defaults(self):
        """Set all default settings"""
        self._set('*RST')

    def _set(self, cmd):
        """Sets a value on the pre-amp

        :param cmd: the command to send to the pre-amp
        :type cmd: str
        """
        with serial.Serial(self._serial_port,
                           baudrate=9600,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_TWO,
                           timeout=0.5) as connection:
            connection.write((cmd + '\r\n').encode('ascii'))
            sleep(0.1)
