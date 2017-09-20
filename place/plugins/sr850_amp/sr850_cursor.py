"""Cursor commands"""
from ast import literal_eval
from .sr850_driver import SR850Driver

class SR850Cursor(SR850Driver):
    """Cursor commands"""
    def csek(self, mode=None):
        """Sets or queries the cursor seek mode.

        Seek mode can either be 'Max', 'Min', or 'Mean'. Each display has it's
        own cursor seek mode. Use the `atrc()` or `smod()` methods to select
        the desired display. Only chart displays have a cursor.

        :param mode: the seek mode to use
        :type mode: str
        :returns: the current seek mode
        :rtype: str
        """
        params = ['Max', 'Min', 'Mean']
        if mode is not None:
            self._set('CSEK {}'.format(params.index(mode)))
        return params[int(self._query('CSEK?'))]

    def cwid(self, width=None):
        """Sets or queries the cursor width of the active display.

        Cursor width can either be 'Off', 'Narrow', 'Wide', or 'Spot'. Each
        display has its own cursor width. Use the `atrc()` or `smod()` methods
        to select the desired display. Only chart displays have a cursor.

        :param width: the cursor width to use
        :type width: str
        :returns: the current cursor width
        :rtype: str
        """
        params = ['Off', 'Narrow', 'Wide', 'Spot']
        if width is not None:
            self._set('CWID {}'.format(params.index(width)))
        return params[int(self._query('CWID?'))]

    def cdiv(self, divisions=None):
        """Sets or queries the vertical divisions of the active display.

        Vertical divisions can be 0, 8, or 10. Each display has its own
        vertical divisions mode. Use the `atrc()` or `smod()` methods to select
        the desired display. This only affects chart displays.

        :param divisions: the vertical divisions to use
        :type divisions: int
        :returns: the current vertical divisions for the active display.
        :rtype: int
        """
        params = [8, 10, 0]
        if divisions is not None:
            self._set('CDIV {}'.format(params.index(divisions)))
        return params[int(self._query('CDIV?'))]

    def clnk(self, mode=None):
        """Sets or queries the cursor control mode.

        Control mode can be 'Linked' or 'Separated'. Only chart displays have a
        cursor.

        :param mode: the cursor control mode to use
        :type mode: str
        :returns: the current cursor control mode
        :rtype: str
        """
        params = ['Linked', 'Separated']
        if mode is not None:
            self._set('CLNK {}'.format(params.index(mode)))
        return params[int(self._query('CLNK?'))]

    def cdsp(self, mode=None):
        """Sets or queries the cursor readout mode of the active display.

        The readout mode can be 'Delay', 'Bin', 'Fsweep', or 'Time'. Only chart
        displays have a cursor.

        :param mode: the cursor readout mode to use
        :type mode: str
        :returns: the current readout mode
        :rtype: str
        """
        params = ['Delay', 'Bin', 'Fsweep', 'Time']
        if mode is not None:
            self._set('CDSP {}'.format(params.index(mode)))
        return params[int(self._query('CDSP?'))]

    def cmax(self):
        """Move cursor to max or min of data.

        This is just like pressing the CURSOR MAX/MIN key. Only effective if
        the active display is a chart display.
        """
        self._set('CMAX')

    def curs(self, display):
        """Queries the cursor position of the display.

        Display can be 'Full', 'Top', or 'Bottom'. The selected display must be
        a chart display.The returned values are those diaplyed in the cursor
        readout above the selected chart display.

        :param display: the display to use
        :type display: str
        :returns: the horizontal and vertical position
        :rtype: (float, float)
        """
        params = ['Full', 'Top', 'Bottom']
        return literal_eval(self._set('CURS? {}'.format(params.index(display))))

    def cbin(self, position=None):
        """Sets or queries the cursor bin position of the active chart display.

        The active display must be a chart display.

        Remember that this method references the center of the cursor region.

        :param position: the bin position to which the cursor should be moved
        :type position: int
        :returns: the current bin posiiton
        :rtype: int
        """
        if position is not None:
            self._set('CBIN {}'.format(position))
        return int(self._query('CBIN?'))
