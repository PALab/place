"""Math commands"""
from .sr850_driver import SR850Driver

class SR850Math(SR850Driver):
    """Math commands"""
    def smth(self, width):
        """Smooth the data trace of the active display.

        This command may take some time to complete. If a scan is in progress,
        this method will pause the scan.

        :param width: the smoothing width
        :type width: str
        """
        param = ['5 points', '11 points', '17 points', '21 points', '25 points']
        self._set('SMTH {}'.format(param.index(width)))

    def copr(self, operation=None):
        """Sets or queries the type of math operation selected.

        :param operation: the math operation
        :type operation: str
        :returns: the math operation
        :rtype: str
        """
        ops = ['+', '-', '*', '/', 'sin', 'cos', 'tan', 'square root',
               'square', 'log', 'power of 10']
        if operation is not None:
            self._set('COPR {}'.format(ops.index(operation)))
        return ops[int(self._query('COPR?'))]

    def calc(self):
        """Starts the calculation selected by copr().

        This may take some time.
        """
        self._set('CALC')

    def cagt(self, type_=None):
        """Sets or queries the argument type.

        :parameter type_: the argument type
        :type type_: str
        :returns: the argument type
        :rtype: str
        """
        param = ['Trace', 'Constant']
        if type_ is not None:
            self._set('CAGT {}'.format(param.index(type_)))
        return param[int(self._query('CAGT?'))]

    def ctrc(self, trace=None):
        """Sets or queries the trace argument number.

        The selected trace must be stored.

        :param trace: the trace number
        :type trace: int
        :returns: the trace number
        :rtype: int
        """
        if trace is not None:
            self._set('CTRC {}'.format(trace))
        return int(self._query('CTRC?'))

    def carg(self, value=None):
        """Sets or queries the constant argument value.

        :param value: the constant argument value
        :type value: float
        :returns: the constant argument value
        :rtype: float
        """
        if value is not None:
            self._set('CARG {}'.format(value))
        return float(self._query('CARG?'))

    def ftyp(self, fit=None):
        """Sets or queries the type of fit.

        :param fit: the type of fit
        :type fit: str
        :returns: the type of fit
        :rtype: str
        """
        param = ['Line', 'Exponential', 'Gaussian']
        if fit is not None:
            self._set('FTYP {}'.format(param.index(fit)))
        return param[int(self._query('FTYP?'))]

    def fitt(self, start, end):
        """Starts the fitting calculation.

        The fit takes place between *start%* and *end%* and *end* must be
        larger than *start*. This fit may take some time. If a scan is in
        progress, it will be paused.

        :param start: the start point from the left side of the screen (percentage)
        :type start: int
        :param end: the end point from the left side of the screen (percentage)
        :type end: int
        """
        self._set('FITT {}, {}'.format(start, end))

    def pars(self, parameter):
        """Queries the fit parameters after a curve fit has been performed.

        If no fit has been performed or the selected parameter is unused in the
        fit, this could return invalid data.

        :param parameter: the fit parameter
        :type parameter: str
        :returns: the fit parameter value
        :rtype: float
        """
        param = ['a', 'b', 'c', 't0']
        return float(self._query('PARS {}'.format(param.index(parameter))))

    def stat(self, start, end):
        """Starts the statistics calulations.

        Only the data within the chart region defined between *start%* and
        *end%* (*end* must be larger than *start*) are analyzed. The analysis
        may take some time.

        :param start: the start point from the left side of the screen (percentage)
        :type start: int
        :param end: the end point from the left side of the screen (percentage)
        :type end: int
        """
        self._set('STAT {}, {}'.format(start, end))

    def spar(self, statistic):
        """Queries the results of the statistical calculation.

        If no analysis has been performed this will return invalid data.

        :param statistic: the statistic parameter
        :type statistic: str
        :returns: the result of the parameter
        :rtype: float
        """
        param = ['mean', 'standard deviation', 'total data', 'delta time']
        return float(self._query('SPAR {}'.format(param.index(statistic))))
