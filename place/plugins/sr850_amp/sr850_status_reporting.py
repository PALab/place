"""Status reporting commands"""
from .sr850_driver import SR850Driver

class SR850StatusReporting(SR850Driver):
    """Status reporting commands"""
    def cls(self):
        """Clears all status registers.

        The status enable registers are *not* cleared.
        """
        self._set('*CLS')

    def ese(self, register=None):
        """Sets or queries the standard event enable register.

        Valid values for the register are 0-255.

        :param register: the value the register should be set to
        :type register: int
        :returns: the value of the register
        :rtype: int
        """
        if register is not None:
            self._set('*ESE {}'.format(register))
        return int(self._query('*ESE?'))

    def ese_bit(self, bit, value=None):
        """Sets or queries bits from the standard event enable register.

        Valid bits are 0-7 and they can be set to either 0 or 1.

        :param bit: the bit to change
        :type bit: int
        :param value: the value for the bit
        :type value: int
        :returns: the value of the bit (0 or 1)
        :rtype: int
        """
        if value is not None:
            self._set('*ESE {}, {}'.format(bit, value))
        return int(self._query('*ESE? {}'.format(bit)))

    def esr(self, bit=None):
        if bit is not None:
            return int(self._query('*ESR {}'.format(bit)))
        return int(self._query('*ESR?'))

    def sre(self, register=None):
        """Sets or queries the serial poll enable register.

        Valid values for the register are 0-255.

        :param register: the value the register should be set to
        :type register: int
        :returns: the value of the register
        :rtype: int
        """
        if register is not None:
            self._set('*SRE {}'.format(register))
        return int(self._query('*SRE?'))

    def sre_bit(self, bit, value=None):
        """Sets or queries bits from the serial poll enable register.

        Valid bits are 0-7 and they can be set to either 0 or 1.

        :param bit: the bit to change
        :type bit: int
        :param value: the value for the bit
        :type value: int
        :returns: the value of the bit (0 or 1)
        :rtype: int
        """
        if value is not None:
            self._set('*SRE {}, {}'.format(bit, value))
        return int(self._query('*SRE? {}'.format(bit)))

    def stb(self, bit=None):
        if bit is not None:
            return int(self._query('*STB {}'.format(bit)))
        return int(self._query('*STB?'))

    def psc(self, value=None):
        if value is not None:
            self._set('*PSC {}'.format(value))
        return int(self._query('*PSC?'))

    def erre(self, bit=None, value=None):
        if bit is None:
            if value is not None:
                self._set('ERRE {}'.format(value))
            return int(self._query('ERRE?'))
        if value is not None:
            self._set('ERRE {}, {}'.format(bit, value))
        return int(self._query('ERRE? {}'.format(bit)))

    def errs(self, bit=None):
        if bit is not None:
            return int(self._query('*ERRS? {}'.format(bit)))
        return int(self._query('#ERRS?'))

    def liae(self, bit=None, value=None):
        if bit is None:
            if value is not None:
                self._set('LIAE {}'.format(value))
            return int(self._query('LIAE?'))
        if value is not None:
            self._set('LIAE {}, {}'.format(bit, value))
        return int(self._query('LIAE? {}'.format(bit)))

    def lias(self, bit=None):
        if bit is not None:
            return int(self._query('*LIAS? {}'.format(bit)))
        return int(self._query('*LIAS?'))
