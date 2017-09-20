"""Trace and scan commands"""
# pylint: disable=too-many-arguments
from ast import literal_eval
from .sr850_driver import SR850Driver

class SR850TraceScan(SR850Driver):
    """Trace and scan commands"""
    def trcd(self, trace_number, j_value=None, k_value=None, l_value=None, store=None):
        """Sets or queries the trace definitions.

        The valid strings for *j*, *k*, and *l* are as shown here:

        j,k,l

        * 1
        * X
        * Y
        * R
        * theta
        * Xn
        * Yn
        * Rn
        * Al1
        * Al2
        * Al3
        * Al4
        * F

        l only

        * X^2
        * Y^2
        * R^2
        * theta^2
        * Xn^2
        * Yn^2
        * Rn^2
        * Al1^2
        * Al2^2
        * Al3^2
        * Al4^2
        * F^2

        For example, for following command defines trace 1 as X*Y/R and stores
        trace 1:

        .. code-block:: python

            SR850TraceScan().trcd(1, 'X', 'Y', 'R', store=True)

        The following command is used to query the current settings for trace 1:

        .. code-block:: python

            j, k, l, stored = SR850TraceScan().trcd(1)

        In this example, *j*, *k*, and *l* will be string values and *stored*
        with be a boolean value.

        :param trace_number: selects the trace number (1, 2, 3, or 4) and is required
        :type trace_number: int
        :param j_value: defines the trace as quantity *j* times quantity *k*
                        divided by quantity *l*
        :type j_value: str
        :param k_value: defines the trace as quantity *j* times quantity *k*
                        divided by quantity *l*
        :type k_value: str
        :param l_value: defines the trace as quantity *j* times quantity *k*
                        divided by quantity *l*
        :type l_value: str
        :param store: trace is stored or not stored
        :type store: bool
        :returns: Nothing or current settings
        :rtype: (str, str, str, bool) or None
        :raises ValueError: if provided values are found to be invalid
        """
        params = [
            '1', 'X', 'Y', 'R', 'theta', 'Xn', 'Yn', 'Rn', 'Al1', 'Al2', 'Al3',
            'Al4', 'F', 'X^2', 'Y^2', 'R^2', 'theta^2', 'Xn^2', 'Yn^2', 'Rn^2',
            'Al1^2', 'Al2^2', 'Al3^2', 'Al4^2', 'F^2']
        if (trace_number != 1 or
                trace_number != 2 or
                trace_number != 3 or
                trace_number != 4):
            raise ValueError('trace number must be 1, 2, 3, or 4')
        curr_j, curr_k, curr_l, curr_store = literal_eval(
            self._query('TRCD? {}'.format(trace_number)))
        if j_value is None and k_value is None and l_value is None and store is None:
            return params[curr_j], params[curr_k], params[curr_l], curr_store == 1
        j_set = params.index(j_value)
        if j_set > 12:
            raise ValueError('j_value is {}, which is invalid'.format(j_value))
        k_set = params.index(k_value)
        if k_set > 12:
            raise ValueError('k_value is {}, which is invalid'.format(k_value))
        l_set = params.index(l_value)
        if store:
            store_set = 1
        else:
            store_set = 0
        self._set('TRCD {}, {}, {}, {}, {}'.format(
            trace_number, j_set, k_set, l_set, store_set))

    def srat(self, sample_rate=None):
        """Sets or queries the scan sample rate.

        Sample rates

        * 62.5 mHz
        * 125 mHz
        * 250 mHz
        * 500 mHz
        * 1 Hz
        * 2 Hz
        * 4 Hz
        * 8 Hz
        * 16 Hz
        * 32 Hz
        * 64 Hz
        * 128 Hz
        * 256 Hz
        * 512 Hz
        * Trigger

        :param sample_rate: the scan sample rate
        :type sample_rate: str
        :returns: Nothing or current setting
        :rtype: str or None
        """
        param = [
            '62.5 mHz',
            '125 mHz',
            '250 mHz',
            '500 mHz',
            '1 Hz',
            '2 Hz',
            '4 Hz',
            '8 Hz',
            '16 Hz',
            '32 Hz',
            '64 Hz',
            '128 Hz',
            '256 Hz',
            '512 Hz',
            'Trigger']
        if sample_rate is None:
            return param[int(self._query('SRAT?'))]
        self._set('SRAT {}'.format(param.index(sample_rate)))

    def slen(self, length=None):
        """Sets scan length.

        Set to closest allowed time given sample rate and stored number of
        traces. Max is buffer size / sample rate. Min is 1.0 sec.

        This method does not validate the input data, but will query the device
        settings and return them in case validating the setting is desired by
        the user.

        :param length: the scan length
        :type length: float
        :returns: the scan length returned from the device
        :rtype: float
        """
        if length is not None:
            self._set('SLEN {}'.format(length))
        return float(self._query('SLEN?'))

    def send(self, mode=None):
        """Sets or queries the scan mode.

        :param mode: the scan mode (either '1 shot' or 'loop')
        :type mode: str
        :returns: the current scan mode or nothing
        :rtype: str or None
        """
        mode_param = ['1 shot', 'loop']
        if mode is None:
            return mode_param[int(self._query('SEND?'))]
        self._set('SEND {}'.format(mode_param.index(mode)))

    def trig(self):
        """Software trigger command."""
        self._set('TRIG')
