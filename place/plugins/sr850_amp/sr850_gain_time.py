"""Gain and time constant commands"""
from .sr850_driver import SR850Driver

class SR850GainTime(SR850Driver):
    """Gain and time constant commands"""
    def sens(self, sensitivity):
        """Sets sensitivity"""
        cmd = ["2 nV/fA", "5 nV/fA", "10 nV/fA", "20 nV/fA", "50 nV/fA",
               "100 nV/fA", "200 nV/fA", "500 nV/fA", "1 microV/pA", "2 microV/pA",
               "5 microV/pA", "10 microV/pA", "20 microV/pA", "50 microV/pA",
               "100 microV/pA", "200 microV/pA", "500 microV/pA", "1 mV/nA",
               "2 mV/nA", "5 mV/nA", "10 mV/nA", "20 mV/nA", "50 mV/nA", "100 mV/nA",
               "200 mV/nA", "500 mV/nA", "1 V/microA"]
        if sensitivity is None:
            setting = int(self._query('SENS?'))
            try:
                ret = cmd[setting]
            except IndexError:
                ret = 'unknown value: {}'.format(setting)
            return ret
        for num, val in enumerate(cmd):
            if val == sensitivity:
                self._set('SENS {}'.format(num))
                break
        else:
            raise ValueError('invalid sensitivity value: {}'.format(sensitivity))

    def rmod(self, mode=None):
        """Sets or queries reserve mode."""
        cmd = ['Max', 'Manual', 'Min']
        if mode is None:
            setting = int(self._query('RMOD?'))
            try:
                ret = cmd[setting]
            except IndexError:
                ret = 'unknown value: {}'.format(setting)
            return ret
        if mode == 0:
            return 'Max'
        elif mode == 1:
            return 'Manual'
        elif mode == 2:
            return 'Min'
        else:
            raise ValueError('invalid mode value: {}'.format(mode))

    def rsrv(self, reserve=None):
        """Sets or queries dynamic reserve.

        Sets or queries dynamic reserve to i^(th) available reserve (between 0 and 5).
        Must be in Manual reserve mode
        0 (minimum reserve for present sensitivity and time constant
        1 (next highest reserve)
        ...
        5 (always sets reserve to max.)
        Reserve increases by 10 dB for each successive value of i.
        """
        if self.rmod() != 'Manual':
            raise RuntimeError("dynamic reserve can only be used when " +
                               "the reserve mode is set to 'Manual'")
        if reserve is None:
            return int(self._query('RSRV?'))
        if 0 <= reserve <= 5:
            self._set('RSRV {}'.format(reserve))
        else:
            raise ValueError('invalid reserve value: {}'.format(reserve))

    def oflt(self, timeconst=None):
        """Sets time constant."""
        constants = ['10us', '30us', '100us', '300us', '1ms',
                     '3ms', '10ms', '30ms', '100ms', '300ms',
                     '1s', '3s', '10s', '30s', '100s', '300s',
                     '1ks', '3ks', '10ks', '30ks']
        if timeconst is None:
            return constants[int(self._query('OFLT?'))]
        self._set('OFLT {}'.format(constants.index(timeconst)))

    def ofsl(self, slope=None):
        """Sets low pass filter slope."""
        constants = ['6 dB/oct', '12 dB/oct', '18 dB/oct', '24 dB/oct']
        if slope is None:
            return constants[int(self._query('OFSL?'))]
        self._set('OFSL {}'.format(constants.index(slope)))

    def sync(self, filter_status=None):
        """Sets synchronous filter status.

        Only turned on if detection frequency < 200 Hz.

        * 0 (off)
        * 1 (synchronous filter below 200 Hz)
        """
        constants = ['off', 'synchronous filter below 200 Hz']
        if filter_status is None:
            return constants[int(self._query('SYNC?'))]
        self._set('SYNC {}'.format(constants.index(filter_status)))
