"""Input and filter commands for the SR850 lock-in amplifier"""
from .sr850_driver import SR850Driver

class SR850InputFilter(SR850Driver):
    """Input and filter commands for the SR850 lock-in amplifier"""
    def isrc(self, source=None):
        """Sets input configuration.

        :param source: "A", "A-B", or "I"
        :type source: str or None

        :returns: if source is None, returns the current setting
        :rtype: str or None

        :raises ValueError: if source value is invalid
        """
        if source is None:
            setting = int(self._query('ISRC?'))
            if setting == 0:
                return 'A'
            if setting == 1:
                return 'A-B'
            if setting == 2:
                return 'I'
            return 'unknown value: {}'.format(setting)
        if source == 'A':
            self._set('ISRC 0')
        elif source == 'A-B':
            self._set('ISRC 1')
        elif source == 'I':
            self._set('ISRC 2')
        else:
            raise ValueError('invalid source value: {}'.format(source))

    def igan(self, gain=None):
        """Sets conversion gain of current input.

        Only relavent if input configured to measure current.

        :param gain: "1 Mohm", or "100 Mohm"
        :type gain: str or None

        :returns: if gain is None, returns the current setting
        :rtype: str or None

        :raises ValueError: if gain value is invalid
        """
        if gain is None:
            setting = int(self._query('IGAN?'))
            if setting == 0:
                return '1 Mohm'
            if setting == 1:
                return '100 Mohm'
            return 'unknown value: {}'.format(setting)
        if gain == '1 Mohm':
            self._set('IGAN 0')
        elif gain == '100 Mohm':
            self._set('IGAN 1')
        else:
            raise ValueError('invalid gain value: {}'.format(gain))

    def ignd(self, grounding=None):
        """Sets shield grounding.

        :param grounding: "Float", or "Ground"
        :type grounding: str or None

        :returns: if grounding is None, returns the current setting
        :rtype: str or None

        :raises ValueError: if grounding value is invalid
        """
        if grounding is None:
            setting = int(self._query('IGND?'))
            if setting == 0:
                return 'Float'
            if setting == 1:
                return 'Ground'
            return 'unknown value: {}'.format(setting)
        if grounding == 'Float':
            self._set('IGND 0')
        elif grounding == 'Ground':
            self._set('IGND 1')
        else:
            raise ValueError('invalid grounding value: {}'.format(grounding))

    def icpl(self, coupling=None):
        """Sets input coupling.

        :param coupling: "AC", or "DC"
        :type coupling: str or None

        :returns: if coupling is None, returns the current setting
        :rtype: str or None

        :raises ValueError: if coupling value is invalid
        """
        if coupling is None:
            setting = int(self._query('ICPL?'))
            if setting == 0:
                return 'AC'
            if setting == 1:
                return 'DC'
            return 'unknown value: {}'.format(setting)
        if coupling == 'AC':
            self._set('ICPL 0')
        elif coupling == 'DC':
            self._set('ICPL 1')
        else:
            raise ValueError('invalid coupling value: {}'.format(coupling))

    def ilin(self, filters=None):
        """Sets input line notch filter.

        :param filters: "Out or no filters", "Line notch in", "2x Line notch
                        in", or "Both notch filters in"
        :type filters: str or None

        :returns: if filters is None, returns the current setting
        :rtype: str or None

        :raises ValueError: if filters value is invalid
        """
        if filters is None:
            setting = int(self._query('ILIN?'))
            if setting == 0:
                return 'Out or no filters'
            if setting == 1:
                return 'Line notch in'
            if setting == 1:
                return '2x Line notch in'
            if setting == 1:
                return 'Both notch filters in'
            return 'unknown value: {}'.format(setting)
        if filters == 'Out or no filters':
            self._set('ILIN 0')
        elif filters == 'Line notch in':
            self._set('ILIN 1')
        elif filters == '2x Line notch in':
            self._set('ILIN 2')
        elif filters == 'Both notch filters in':
            self._set('ILIN 3')
        else:
            raise ValueError('invalid filters value: {}'.format(filters))
