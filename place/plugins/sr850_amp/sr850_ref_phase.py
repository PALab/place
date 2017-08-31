"""Reference and phase commands for the SR850 lock-in amplifier"""
from .sr850_driver import SR850Driver

class SR850ReferenceAndPhaseCmds(SR850Driver):
    """Reference and phase commands"""
    def phas(self, shift=None):
        """Set or query the reference phase shift.

        :param shift: phase (real number of degrees) rounded to 0.001 deg,
                      between -360 and 719.999 (will be wrapped around at +/-
                      180 deg.
        :type shift: float or None

        :returns: if shift is None, then returns the current shift value
        :rtype: float or None
        """
        if shift is None:
            return float(self._query('PHAS?'))
        self._set('PHAS {:.3F}'.format(shift))

    def fmod(self, source=None):
        """Queries and returns reference source.

        :param source: the reference source: "internal", "internal sweep",
                       or "external"
        :type source: str or None

        :returns: if source is None, then returns the current source
        :rtype: str or None

        :raises ValueError: if source value is invalid
        """
        if source is None:
            setting = int(self._query('FMOD?'))
            if setting == 0:
                return 'internal'
            if setting == 1:
                return 'internal sweep'
            if setting == 2:
                return 'external'
            return 'unknown value: {}'.format(setting)
        if source == "internal":
            self._set('FMOD 0')
        elif source == "internal sweep":
            self._set('FMOD 1')
        elif source == "external":
            self._set('FMOD 2')
        else:
            raise ValueError('invalid value for source: {}'.format(source))

    def freq(self, frequency=None):
        """Sets the frequency of the internal oscillator.

        Only allowed when reference source is internal.

        :param frequency: frequency in Hz. Rounded to 5 digits or 0.0001
                          (whichever is greater). Range 0.001 to 102000. If
                          harmonic number > 1, range harmonic number*f <= 102
                          kHz.
        :type frequency: float or None

        :returns: if frequency is None, then returns the current frequency
        :rtype: float or None
        """
        if frequency is None:
            return float(self._query('FREQ?'))
        self._set('FREQ {:.5F}'.format(frequency))

    def swpt(self, sweep=None):
        """Sets the type of frequency sweep.

        Must be in internal sweep mode.

        :param sweep: "linear" or "logarithmic"
        :type sweep: str or None

        :returns: if sweep is None, returns the current sweep
        :rtype: str or None

        :raises ValueError: if sweep value is invalid
        """
        if sweep is None:
            setting = self._query('SWPT?')
            if setting == 0:
                return 'linear'
            if setting == 1:
                return 'logarithmic'
            return 'unknown value: {}'.format(setting)
        if sweep == 'linear':
            self._set('SWPT 0')
        elif sweep == 'logarithmic':
            self._set('SWPT 1')
        else:
            raise ValueError('invalid value for sweep: {}'.format(sweep))

    def sllm(self, start=None):
        """Sets the starting frequency of internal frequency sweep.

        :param start: frequency in Hz (rounded to 5 digits or 0.0001 Hz,
                      whichever is greater. Range 0.001 to 102000 Hz. If
                      harmonic number > 1, range harmonic number*f <= 102 kHz.
        :type start: float or None

        :returns: if start is None, returns the current starting frequency
        :rtype: float or None
        """
        if start is None:
            return float(self._query('SLLM?'))
        self._set('SLLM {:.5F}'.format(start))

    def sulm(self, stop=None):
        """Sets the stop frequency of internal frequency sweep.

        :param stop: frequency in Hz (rounded to 5 digits or 0.0001 Hz,
                     whichever is greater. Range 0.001 to 102000 Hz. If
                     harmonic number > 1, range harmonic number*f <= 102 kHz.
        :type stop: float or None

        :returns: if stop is None, returns the current stop frequency
        :rtype: float or None
        """
        if stop is None:
            return float(self._query('SULM?'))
        self._set('SULM {:.5F}'.format(stop))

    def rslp(self, slope=None):
        """Sets reference slope when using external reference mode.

        At frequencyies < 1 Hz, a TTL reference must be used.

        :param slope: "sine zero crossing", "TTL rising edge", or "TTL falling
                      edge"
        :type slope: str or None

        :returns: if slope is None, returns the current slope
        :rtype: str or None

        :raises ValueError: if the slope value is invalid
        """
        if slope is None:
            setting = self._query('RSLP?')
            if setting == 0:
                return 'sine zero crossing'
            if setting == 1:
                return 'TTL rising edge'
            if setting == 2:
                return 'TTL falling edge'
            return 'unknown value: {}'.format(setting)
        if slope == 'sine zero crossing':
            self._set('RSLP 0')
        elif slope == 'TTL rising edge':
            self._set('RSLP 1')
        elif slope == 'TTL falling edge':
            self._set('RSLP 2')
        else:
            raise ValueError('invalid value for slope: {}'.format(slope))

    def harm(self, harmonic=None):
        """Sets the detection harmonic.

        :param harmonic: an integer from 1 to 32767. Sets the lock-in to
                         detect at the i^(th) harmonic of the reference
                         frequency. Range i*freq < 102 kHz. If detection
                         frequency > 102 kHz, harmonic number will be set to
                         largest value in this range.
        :type harmonic: int or None

        :returns: if harmonic is None, returns the current setting
        :rtype: int or None
        """
        if harmonic is None:
            return int(self._query('HARM?'))
        self._set('HARM {}'.format(harmonic))

    def slvl(self, amplitude=None):
        """Sets the amplitude of sine output.

        :param amplitude: a voltage (Volts). Range 0.004 to 5.000, will be
                          rounded to 0.002V.
        :type amplitude: float or None

        :returns: if amplitude is None, returns the current setting
        :rtype: float or None
        """
        if amplitude is None:
            return float(self._query('SLVL?'))
        self._set('SLVL {:.5F}'.format(amplitude))
