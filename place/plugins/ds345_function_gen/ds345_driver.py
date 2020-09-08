"""Driver module for Stanford Research Systems DS345 Function Generator."""

import serial

class DS345Driver:
    #pylint: disable=too-many-public-methods
    """Class for low-level access to the function generator settings."""

    def __init__(self, serial_port):
        self._serial_port = str(serial_port)

# FUNCTION OUTPUT CONTROL COMMANDS

    def aecl(self):
        """Sets the output to the ECL levels of 1 V peak-to-peak with a -1.3 V offset."""
        self._set('AECL')

    def ampl(self, amplitude=None, units='Vpp'):
        """Sets or queries the output amplitude."""
        unit_opts = {'Vpp': 'VP', 'Vrms': 'VR', 'dBm': 'DB'}
        if amplitude is None:
            if units is None:
                res = self._query('AMPL?')
            else:
                res = self._query('AMPL? {}'.format(unit_opts[units]))
            amp, unit_opt = res[:-2], res[-2:]
            try:
                unit = next(key for key, value in unit_opts.items()
                            if value == unit_opt)
            except StopIteration:
                raise RuntimeError(
                    'Could not determine unit for string {}'.format(res))
            return float(amp), unit
        self._set('AMPL {:.6f}{}'.format(amplitude, unit_opts[units]))

    def attl(self):
        """Sets the TTL output levels to 5 V peak-to-peak with a 2.5 V offset."""
        self._set('ATTL')

    def freq(self, frequency=None):
        """Sets or queries the output frequency."""
        if frequency is None:
            return float(self._query('FREQ?'))
        self._set('FREQ {:.6f}'.format(frequency))

    def fsmp(self, frequency=None):
        """Sets or queries the arbitrary waveform sampling frequency."""
        if frequency is None:
            return float(self._query('FSMP?'))
        self._set('FSMP {:.6f}'.format(frequency))

    def func(self, function_type=None):
        """Sets or queries the output frequency type."""
        types = ['SINE', 'SQUARE', 'TRIANGLE', 'RAMP', 'NOISE', 'ARBITRARY']
        if function_type is None:
            return types[int(self._query('FUNC?'))]
        self._set('FUNC {:d}'.format(types.index(function_type.upper())))

    def invt(self, output_inversion=None):
        """Sets or queries the output inversion value."""
        opts = ['off', 'on']
        if output_inversion is None:
            return opts[int(self._query('INVT?'))]
        self._set('INVT {:d}'.format(opts.index(output_inversion)))

    def offs(self, dc_offset=None):
        """Sets or queries the output's DC offset."""
        if dc_offset is None:
            return float(self._query('OFFS?'))
        self._set('OFFS {:.6f}'.format(dc_offset))

    def pclr(self):
        """Sets the waveform phase value to 0."""
        self._set('PCLR')

    def phse(self, output_phase=None):
        """Sets or queries the waveform output phase."""
        if output_phase is None:
            self._query('*ESR? 4')
            resp = self._query('PHSE?')
            if self._query('*ESR? 4') != 0:
                return 'Execution err'
            return float(resp)
        self._set('PHSE {:.6f}'.format(output_phase))

# MODULATION CONTROL COMMANDS

    def trg(self):
        """Triggers a burst or single sweep."""
        if self.tsrc() != 'SINGLE':
            raise RuntimeError("Cannot trigger a burst or single sweep when " +
                               "trigger source is not 'single'.")
        self._set('*TRG')

    def bcnt(self, count=None):
        """Sets or queries the burst count."""
        if count is None:
            return int(self._query('BCNT?'))
        if 1 <= count <= 30000:
            self._set('BCNT {:d}'.format(count))
        else:
            raise ValueError(
                'Burst count must be between 1 and 30000 (inclusive)')

    def dpth(self, depth=None):
        """Sets or queries the AM modulation depth percentage.

        If the depth is negative, the modulation is set to double sideband
        suppressed carrier modulation (DSBSC).
        """
        if depth is None:
            return int(self._query('DPTH?'))
        if -100 <= depth <= 100:
            self._set('DPTH {:d}'.format(depth))
        else:
            raise ValueError(
                'AM modulation depth percentage must be between -100 and 100.')

    def fdev(self, span=None):
        """Sets or queries the FM span."""
        if span is None:
            return float(self._query('FDEV?'))
        self._set('FDEV {:.6f}'.format(span))

    def mdwf(self, waveform=None):
        """Sets or queries the modulation waveform."""
        opts = ['SINGLE SWEEP', 'RAMP', 'TRIANGLE',
                'SINE', 'SQUARE', 'ARB', 'NONE']
        if waveform is None:
            return opts[int(self._query('MDWF?'))]
        self._set('MDWF {:d}'.format(opts.index(waveform.upper())))

    def mena(self, modulation=None):
        """Set or queries whether modulation is enabled."""
        if modulation is None:
            return int(self._query('MENA?')) == 1
        if modulation is False:
            self._set('MENA 0')
        else:
            self._set('MENA 1')

    def mksp(self):
        """Sets the sweep markers to the extremes of the sweep span."""
        self._set('MKSP')

    def mrkf(self, marker, frequency=None):
        """Sets or queries one of the sweep markers."""
        markers = ['START', 'STOP', 'CENTER', 'SPAN']
        if frequency is None:
            return float(self._query('MRKF? {:d}'.format(markers.index(marker.upper()))))
        self._set('MRKF {:d} {:.6f}'.format(
            markers.index(marker.upper()), frequency))

    def mtyp(self, modulation=None):
        """Sets or queries the modulation type."""
        types = ['LIN SWEEP', 'LOG SWEEP',
                 'INTERNAL AM', 'FM', 'PHI_M', 'BURST']
        if modulation is None:
            return types[int(self._query('MTYP?'))]
        self._set('MTYP {:d}'.format(types.index(modulation.upper())))

    def pdev(self, span=None):
        """Sets or queries the span of the phase modulation."""
        if span is None:
            return float(self._query('PDEV?'))
        self._set('PDEV {:.6f}'.format(span))

    def rate(self, rate=None):
        """Sets or queries the modulation rate."""
        if rate is None:
            return float(self._query('RATE?'))
        self._set('RATE {:.3f}'.format(rate))

    def span(self, span=None):
        """Sets or queries the sweep span."""
        if span is None:
            return float(self._query('SPAN?'))
        self._set('SPAN {:.6f}'.format(span))

    def spcf(self, frequency=None):
        """Sets or queries the sweep center frequency."""
        if frequency is None:
            return float(self._query('SPCF?'))
        self._set('SPCF {:.6f}'.format(frequency))

    def spfr(self, frequency=None):
        """Sets or queries the sweep stop frequency."""
        if frequency is None:
            return float(self._query('SPFR?'))
        self._set('SPFR {:.6f}'.format(frequency))

    def spmk(self):
        """Sets the sweep span to the sweep marker frequency."""
        self._set('SPMK')

    def stfr(self, frequency=None):
        """Sets or queries the sweep start frequency."""
        if frequency is None:
            return float(self._query('STFR?'))
        self._set('STFR {:.6f}'.format(frequency))

    def trat(self, rate=None):
        """Sets or queries the trigger rate for internally triggered single sweeps."""
        if rate is None:
            return float(self._query('TRAT?'))
        self._set('TRAT {:.6f}'.format(rate))

    def tsrc(self, source=None):
        """Sets or queries the trigger source for bursts and sweeps."""
        opts = ['SINGLE', 'INTERNAL RATE',
                '+ SLOPE EXTERNAL', '- SLOPE EXTERNAL', 'LINE']
        if source is None:
            return opts[int(self._query('TSRC?'))]
        self._set('TSRC {:d}'.format(opts.index(source.upper())))

# ARBITRARY WAVEFORM AND MODULATION COMMANDS

    def amrt(self, rate=None):
        """Sets or queries the arbitrary modulation rate divider."""
        if rate is None:
            return int(self._query('AMRT?'))
        self._set('AMRT {:d}'.format(rate))

    def amod(self, length):
        """Allow downloading arbitrary waveform and modulation patterns.

        *Not implemented*
        """
        raise NotImplementedError

    def ldwf(self, format_, data_length):
        """Allows downloading arbitrary waveforms in either point or vector format.

        *Not implemented*
        """
        raise NotImplementedError

# SETUP CONTROL COMMANDS

    def idn(self):
        """Returns the device configuration."""
        return self._query('*IDN?')

    def rcl(self, number):
        """Recalls stored settings."""
        if 0 <= number <= 9:
            self._set('*RCL {:d}'.format(number))
        else:
            raise ValueError('Setting number must be between 0 and 9.')

    def rst(self):
        """Resets the device to default configurations."""
        self._set('*RST')

    def sav(self, number):
        """Saves settings to internal storage."""
        if 0 <= number <= 9:
            self._set('*SAV {:d}'.format(number))
        else:
            raise ValueError('Setting number must be between 0 and 9.')

# STATUS REPORTING COMMANDS

    def cls(self):
        """Clears all status registers."""
        self._set('*CLS')

    def ese(self, value=None):
        """Sets or queries the standard event status byte enable register."""
        if value is None:
            return int(self._query('*ESE?'))
        self._set('*ESE {:d}'.format(value))

    def esr(self, bit=None):
        """Reads and then clears that value of the standard event status register."""
        if bit is None:
            return int(self._query('*ESR?'))
        return int(self._query('*ESR? {:d}'.format(bit)))

    def psc(self, bit=None):
        """Sets or queries the power-on status clear bit."""
        if bit is None:
            return int(self._query('*PSC?'))
        self._set('*PSC {:d}'.format(bit))

    def sre(self, value=None):
        """Sets or queries the value of the serial poll enable register."""
        if value is None:
            return int(self._query('*SRE?'))
        self._set('*SRE {:d}'.format(value))

    def stb(self, bit=None):
        """Reads the value of the serial poll byte or a specific bit."""
        if bit is None:
            return int(self._query('*STB?'))
        return int(self._query('*STB? {:d}'.format(bit)))

    def dena(self, value=None):
        """Sets or queries the DDS status enable register."""
        if value is None:
            return int(self._query('DENA?'))
        self._set('DENA {:d}'.format(value))

    def stat(self, bit=None):
        """Reads the value of the DDS status byte or a specific bit."""
        if bit is None:
            return int(self._query('STAT?'))
        return int(self._query('STAT? {:d}'.format(bit)))

# HARDWARE TEST AND CALIBRATION COMMANDS

    def cal(self):
        """Initiates the device calibration routines.

        *Not implemented*
        """
        raise NotImplementedError

    def tst(self):
        """Runs the internal self-tests.

        *Not implemented*
        """
        raise NotImplementedError

    def atd(self, range_=None):
        """Sets or queries the output attenuators.

        *Not implemented*
        """
        raise NotImplementedError

    def fcl(self):
        """Recalls the factory calibration bytes.

        *Not implemented*
        """
        raise NotImplementedError

    def mdc(self, mimic_dac):
        """Sets the mimic DAC to the given value.

        *Not Implemented*
        """
        raise NotImplementedError

    def wrd(self, word, value=None):
        """Set or queries the value of a calibration word.

        *Not implemented*
        """
        raise NotImplementedError

# HELPER METHODS

    def _set(self, cmd):
        """Sets a value on the function generator.

        :param cmd: the command to send over the serial port
        :type cmd: str
        """
        with serial.Serial(self._serial_port,
                           baudrate=9600,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_TWO,
                           timeout=2) as connection:
            connection.write(bytes(cmd + '\n', 'ascii'))

    def _query(self, cmd):
        """Request a value from the function generator.

        :param cmd: the command to send over the serial port
        :type cmd: str

        :returns: the response on the serial connection
        :rtype: str
        """
        with serial.Serial(self._serial_port,
                           baudrate=9600,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_TWO,
                           timeout=2) as connection:
            connection.write(bytes(cmd + '\n', 'ascii'))
            resp = connection.readline().decode('ascii').strip()
        return resp
