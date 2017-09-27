"""Data transfer commands"""
from ast import literal_eval
from .sr850_driver import SR850Driver

class SR850DataTransfer(SR850Driver):
    """Data transfer commands"""
    def outp(self, channel):
        cmd = ['', 'X', 'Y', 'R', 'theta']
        return float(self._query('OUTP? {}'.format(cmd.index(channel))))

    def outr(self, trace):
        return float(self._query('OUTR? {}'.format(trace)))

    def oaux(self, aux):
        return float(self._query('OAUX? {}'.format(aux)))

    def snap(self, parameters):
        par = ['',
               'X', 'Y', 'R', 'theta',
               'Aux In 1', 'Aux In 2', 'Aux In 3', 'Aux In 4',
               'Reference Frequency',
               'Trace 1', 'Trace 2', 'Trace 3', 'Trace 4']
        cmd = 'SNAP? {}'.format(par.index(parameters[0]))
        for parameter in parameters[1:]:
            cmd += ', {}'.format(par.index(parameter))
        return literal_eval(self._query(cmd))

    def spts(self, trace):
        return int(self._query('SPTS? {}'.format(trace)))

    def trca(self, trace, start, num):
        return list(literal_eval(self._query('TRCA? {}, {}, {}'.format(trace, start, num))))

    def trcb(self):
        raise NotImplementedError('Binary transfer is '
                                  'not recommended over serial connections.')

    def trcl(self):
        raise NotImplementedError('Binary transfer is '
                                  'not recommended over serial connections.')

    def fast(self):
        raise NotImplementedError('Fast transfer is '
                                  'not available over serial connections.')

    def strd(self):
        raise NotImplementedError('Starting a fast transfer is '
                                  'not available over serial connections.')
