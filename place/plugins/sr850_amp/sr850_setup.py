"""Setup commands"""
from .sr850_driver import SR850Driver

class SR850Setup(SR850Driver):
    """Setup commands"""
    def outx(self, output):
        """Sets the output interface.

        .. note::

            The outx() method should be called before any query commands to
            direct the responses to the interface in use.

        :param output: the interface to which data should be sent
        :type output: str
        :returns: the interface currently being used
        :rtype: str
        """
        cmd = ['RS232', 'GPIB']
        self._set('OUTX {}'.format(cmd.index(output)))
        return cmd[int(self._query('OUTX?'))]

    def ovrm(self, override=None):
        cmd = ['No', 'Yes']
        if override is not None:
            self._set('OVRM {}'.format(cmd.index(override)))
        return cmd[int(self._query('OVRM?'))]

    def kclk(self, click=None):
        cmd = ['Off', 'On']
        if click is not None:
            self._set('KCLK {}'.format(cmd.index(click)))
        return cmd[int(self._query('KCLK?'))]

    def alrm(self, alarm=None):
        cmd = ['Off', 'On']
        if alarm is not None:
            self._set('ALRM {}'.format(cmd.index(alarm)))
        return cmd[int(self._query('ALRM?'))]

    def thrs(self, hour=None):
        """Set or query the hours setting of the clock.

        :param hour: the hour
        :type hour: int
        :returns: the hour
        :rtype: int
        """
        if hour is not None:
            self._set('THRS {}'.format(hour))
        return int(self._query('THRS?'))

    def tmin(self, minute=None):
        """Set or query the minutes setting of the clock.

        :param minute: the minute
        :type minute: int
        :returns: the minute
        :rtype: int
        """
        if minute is not None:
            self._set('TMIN {}'.format(minute))
        return int(self._query('TMIN?'))

    def tsec(self, second=None):
        """Set or query the seconds setting of the clock.

        :param second: the second
        :type second: int
        :returns: the second
        :rtype: int
        """
        if second is not None:
            self._set('TSEC {}'.format(second))
        return int(self._query('TSEC?'))

    def dmth(self, month=None):
        """Set or query the month setting of the clock.

        :param month: the month
        :type month: int
        :returns: the month
        :rtype: int
        """
        if month is not None:
            self._set('DMTH {}'.format(month))
        return int(self._query('DMTH?'))

    def dday(self, day=None):
        """Set or query the day setting of the clock.

        :param day: the day
        :type day: int
        :returns: the day
        :rtype: int
        """
        if day is not None:
            self._set('DDAY {}'.format(day))
        return int(self._query('DDAY?'))

    def dyrs(self, year=None):
        """Set or query the year setting of the clock.

        :param year: the year
        :type year: int
        :returns: the year
        :rtype: int
        """
        if year is not None:
            self._set('DYRS {}'.format(year))
        return int(self._query('DYRS?'))

    def pltm(self, mode=None):
        """Set or query the plotter mode.

        :param mode: the plotter mode interface
        :type mode: str
        :returns: the plotter mode interface
        :rtype: str
        """
        cmd = ['RS232', 'GPIB']
        if mode is not None:
            self._set('PLTM {}'.format(mode))
        return cmd[int(self._query('PLTM?'))]

    def pltb(self, baud_rate=None):
        """Set or query the RS232 plotter baud rate.

        :param baud_rate: the communication baud rate
        :type baud_rate: int
        :returns: the communication baud rate
        :rtype: int
        """
        param = [300, 1200, 2400, 4800, 9600]
        if baud_rate is not None:
            self._set('PLTB {}'.format(param.index(baud_rate)))
        return param[int(self._query('PLTB?'))]

    def plta(self):
        """Not implemented"""
        raise NotImplementedError('GPIB is not supported')

    def plts(self, speed=None):
        """Sets or queries the plot speed.

        :param speed: the plot speed
        :type speed: str
        :returns: the plot speed
        :rtype: str
        """
        param = ['fast', 'slow']
        if speed is not None:
            self._set('PLTS {}'.format(param.index(speed)))
        return param[int(self._query('PLTS?'))]

    def pntr(self, pen=None):
        """Sets or queries the trace pen number.

        :param pen: the trace pen number
        :type pen: int
        :returns: the trace pen number
        :rtype: int
        """
        if pen is not None:
            self._set('PNTR {}'.format(pen))
        return int(self._query('PNTR?'))

    def pngd(self, pen=None):
        """Sets or queries the grid pen number.

        :param pen: the grid pen number
        :type pen: int
        :returns: the grid pen number
        :rtype: int
        """
        if pen is not None:
            self._set('PNGD {}'.format(pen))
        return int(self._query('PNGD?'))

    def pnal(self, pen=None):
        """Sets or queries the alphanumeric pen number.

        :param pen: the alphanumeric pen number
        :type pen: int
        :returns: the alphanumeric pen number
        :rtype: int
        """
        if pen is not None:
            self._set('PNAL {}'.format(pen))
        return int(self._query('PNAL?'))

    def pncr(self, pen=None):
        """Sets or queries the cursor pen number.

        :param pen: the cursor pen number
        :type pen: int
        :returns: the cursor pen number
        :rtype: int
        """
        if pen is not None:
            self._set('PNCR {}'.format(pen))
        return int(self._query('PNCR?'))

    def prnt(self, printer=None):
        """Sets or queries the printer type.

        :param printer: printer type
        :type printer: str
        :returns: printer type
        :rtype: str
        """
        param = ['EPSON', 'HP', 'File']
        if printer is not None:
            self._set('PRNT {}'.format(param.index(printer)))
        return param[int(self._query('PRNT?'))]
