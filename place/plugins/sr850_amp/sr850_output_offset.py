"""Output and offset commands"""
from ast import literal_eval
from .sr850_driver import SR850Driver

class SR850OutputOffset(SR850Driver):
    """Output and offset commands"""
    def fout(self, channel_str, quantity_str=None):
        """Sets front panel output sources."""
        cmd = {
            'channel 1': {
                'X': (1, 0),
                'R': (1, 1),
                'theta': (1, 2),
                'Trace 1': (1, 3),
                'Trace 2': (1, 4),
                'Trace 3': (1, 5),
                'Trace 4': (1, 6)},
            'channel 2': {
                'Y': (2, 0),
                'R': (2, 1),
                'theta': (2, 2),
                'Trace 1': (2, 3),
                'Trace 2': (2, 4),
                'Trace 3': (2, 5),
                'Trace 4': (2, 6)}
            }
        if quantity_str is None:
            channel_num, _ = cmd[channel_str]['R']
            return literal_eval(self._query('FOUT? {}'.format(channel_num)))
        channel_num, quantity_num = cmd[channel_str][quantity_str]
        self._set('FOUT {}, {}'.format(channel_num, quantity_num))

    def oexp(self, output, offset=None, expand=None):
        """Sets output offset and expand.

        If *offset* and *expand* parameters are both `None`, then this method
        returns the current offset and expand for the given *output*.

        Otherwise, this method will set the parameters based on the arguments provided.

        :param output: the output to be set or queried ('X', 'Y', or 'R')
        :type output: str
        :param offset: the offset in percent (-105.00 <= *offset* <= 105.00)
        :type offset: float
        :param expand: the expand value (1 <= *expand* <= 256)
        :type expand: int
        :returns: the current offset and expand values for the output, or
                  `None` if *offset* or *expand* are not `None`
        :rtype: (float, int) or `None`
        :raises ValueError: if a given argument is invalid
        """
        if output != 'X' and output != 'Y' and output != 'R':
            raise ValueError(
                "'output' parameter value must be 'X', 'Y', or 'R': " +
                "see SR850 programming manual"
                )
        param1 = {'X': 1, 'Y': 2, 'R': 3}
        cur_offset, cur_expand = literal_eval(self._query('OEXP? {}'.format(param1[output])))
        if offset is None and expand is None:
            return cur_offset, cur_expand
        if offset is None:
            offset = cur_offset
        elif not -105.00 <= offset <= 105.00:
            raise ValueError(("'offset' is {}: must satisfy -105.00 <= offset <= " +
                              "105.00: see SR850 programming manual").format(offset))
        if expand is None:
            expand = cur_expand
        elif not (isinstance(expand, int) and 1 <= expand <= 256):
            raise ValueError(("'expand' is {}: must be an integer and satisfy 1 " +
                              "<= expand <= 256: see SR850 programming " +
                              "manual").format(offset))
        self._set('OEXP {}, {}, {}'.format(output, offset, expand))

    def aoff(self, output):
        """Automatically sets X, Y, or R offset to zero.

        Equivalent to pressing the Auto softkey in the Offset & Expand menu
        box. *This method does not allow query.*

        :param output: the output to be set or queried ('X', 'Y', or 'R')
        :type output: str
        :raises ValueError: if a given argument is invalid
        """
        if output != 'X' and output != 'Y' and output != 'R':
            raise ValueError(
                "'output' parameter value must be 'X', 'Y', or 'R': " +
                "see SR850 programming manual"
                )
        param1 = {'X': 1, 'Y': 2, 'R': 3}
        self._set('AOFF {}'.format(param1[output]))
