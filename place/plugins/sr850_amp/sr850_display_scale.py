"""Display and scale commands"""
from .sr850_driver import SR850Driver

class SR850DisplayScale(SR850Driver):
    """Display and scale commands"""
    def ascl(self):
        """Auto scale the active display.

        This is just like pressing the (AUTO SCALE) key. Only *Bar* and *Chart*
        displays are affected.
        """
        self._set('ASCL')

    def adsp(self, display=None):
        """Select the active display.

        The selected display must be presently displayed on the screen
        otherwise an error will result.

        :param display: 'Full', 'Top', or 'Bottom'
        :type display: str
        :returns: the current display
        :rtype: str
        """
        params = ['Full', 'Top', 'Bottom']
        if display is not None:
            self._set('ADSP {}'.format(params.index(display)))
        return params[int(self._query('ADSP?'))]

    def smod(self, format_=None):
        """Sets or queries the screen format.

        :param format_: 'Single' (full screen) or 'Up/Down' (dual display)
        :type format_: str
        :returns: the current format
        :rtype: str
        """
        params = ['Single', 'Up/Down']
        if format_ is not None:
            self._set('SMOD {}'.format(params.index(format_)))
        return params[int(self._query('SMOD?'))]

    def mntr(self, mode=None):
        """Sets or queries the monitor display mode.

        :param mode: 'Settings' or 'Input/Output'
        :type mode: str
        :returns: the current mode
        :rtype: str
        """
        params = ['Settings', 'Input/Output']
        if mode is not None:
            self._set('MNTR {}'.format(params.index(mode)))
        return params[int(self._query('MNTR?'))]

    def dtyp(self, display, type_=None):
        """Sets or queries the display type.

        .. warning::

            Unexpected behavior may occur if tryng to set the display type of a
            display that is not on screen.

        :param display: 'Full', 'Top', or 'Bottom'
        :type display: str
        :param type_: 'Polar', 'Blank', 'Bar', or 'Chart'
        :type type_: str
        :returns: the current type
        :rtype: str
        """
        param1 = ['Full', 'Top', 'Bottom']
        param2 = ['Polar', 'Blank', 'Bar', 'Chart']
        if type_ is not None:
            self._set('DTYP {}, {}'.format(param1.index(display), param2.index(type_)))
        return param2[int(self._query('DTYP? {}'.format(param1.index(display))))]

    def dtrc(self, display, trace=None):
        """Sets or queries the displayed trace number.

        .. warning::

            Unexpected behavior may occur if tryng to set the trace of a
            display that is not on screen.

        :param display: 'Full', 'Top', or 'Bottom'
        :type display: str
        :param trace: the trace number (1, 2, 3, or 4)
        :type trace: int
        :returns: the trace number
        :rtype: int
        """
        param = ['Full', 'Top', 'Bottom']
        if trace is not None:
            self._set('DTYP {}, {}'.format(param.index(display), trace))
        return int(self._query('DTRC? {}'.format(param.index(display))))

    def dscl(self, display, range_=None):
        """Sets or queries the display range

        .. warning::

            Unexpected behavior may occur if tryng to set the display range of
            a display that is not on screen.

        :param display: 'Full', 'Top', or 'Bottom'
        :type display: str
        :param range_: the display range (real number in units of displayed trace)
        :type range_: float
        :returns: the display range
        :rtype: float
        """
        param = ['Full', 'Top', 'Bottom']
        if range_ is not None:
            self._set('DSCL {}, {}'.format(param.index(display), range_))
        return float(self._query('DSCL? {}'.format(param.index(display))))

    def doff(self, display, center=None):
        """Sets or queries the display center value or offset

        .. warning::

            Unexpected behavior may occur if tryng to set the center of a
            display that is not on screen.

        :param display: 'Full', 'Top', or 'Bottom'
        :type display: str
        :param center: the display center (real number in units of displayed trace)
        :type center: float
        :returns: the display center
        :rtype: float
        """
        param = ['Full', 'Top', 'Bottom']
        if center is not None:
            self._set('DOFF {}, {}'.format(param.index(display), center))
        return float(self._query('DOFF? {}'.format(param.index(display))))

    def dhzs(self, display, scale=None):
        """Sets or queries the display horizontal scale.

        Valid scales:

        time/div

        * 2 mS
        * 5 mS
        * 10 mS
        * 20 mS
        * 50 mS
        * 0.1 S
        * 0.2 S
        * 0.5 S
        * 1.0 S
        * 2.0 S
        * 5.0 S
        * 10 S
        * 20 S
        * 50 S
        * 1 min
        * 100 S
        * 2 min
        * 200 S
        * 5 min
        * 500 S
        * 10 min
        * 1 kS
        * 20 min
        * 2 kS
        * 1 hour
        * 5 kS
        * 2 hour
        * 10 kS
        * 3 hour
        * 20 kS
        * 50 kS
        * 100 kS
        * 200 kS

        The minimum scale is related to the sample rate. The minumum scale is
        (1/sample rate) per division. This displays a minimum of 10 points on
        the chart. The maximum scale is also related to the sample rate. The
        scale cannot exceed that which would display the entire buffer on the
        chart at once.

        .. warning::

            Unexpected behavior may occur if tryng to set the scale of a
            display that is not on screen.

        :param display: 'Full', 'Top', or 'Bottom'
        :type display: str
        :param scale: the display scale
        :type scale: str
        :returns: the display scale
        :rtype: str
        """
        param1 = ['Full', 'Top', 'Bottom']
        param2 = [
            '2 mS', '5 mS', '10 mS', '20 mS', '50 mS', '0.1 S', '0.2 S',
            '0.5 S', '1.0 S', '2.0 S', '5.0 S', '10 S', '20 S', '50 S',
            '1 min', '100 S', '2 min', '200 S', '5 min', '500 S', '10 min',
            '1 kS', '20 min', '2 kS', '1 hour', '5 kS', '2 hour', '10 kS',
            '3 hour', '20 kS', '50 kS', '100 kS', '200 kS']
        if scale is not None:
            self._set('DHZS {}, {}'.format(param1.index(display), param2.index(scale)))
        return param2[int(self._query('DHZS? {}'.format(param1.index(display))))]

    def rbin(self, display):
        """Queries the bin number at the right edge of the chart display.

        The selected display must be a chart display.

        This method along with *cbin()* can be used to position the time window
        of the active chart display over a specific trace region.

        :param display: 'Full', 'Top', or 'Bottom'
        :type display: str
        :returns: the bin number
        :rtype: int
        """
        param = ['Full', 'Top', 'Bottom']
        return int(self._query('RBIN? {}'.format(param.index(display))))
