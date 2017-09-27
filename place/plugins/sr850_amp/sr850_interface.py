"""Interface commands"""
from .sr850_driver import SR850Driver

class SR850Interface(SR850Driver):
    """Interface commands"""
    def rst(self):
        self._set('*RST')

    def idn(self):
        return self._query('*IDN?')

    def locl(self, state=None):
        cmd = ['Local', 'Remote', 'Local Lockout']
        if state is not None:
            self._set('LOCL {}'.format(cmd.index(state)))
        return cmd[int(self._query('LOCL?'))]

    def ovrm(self, override=None):
        cmd = ['No', 'Yes']
        if override is not None:
            self._set('OVRM {}'.format(cmd.index(override)))
        return cmd[int(self._query('OVRM?'))]

    def trig(self):
        self._set('TRIG')
