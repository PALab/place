"""Front panel controls and auto functions"""
from .sr850_driver import SR850Driver

class SR850FrontPanelAuto(SR850Driver):
    """Front panel controls and auto functions"""
    def strt(self):
        self._set('STRT')

    def paus(self):
        self._set('PAUS')

    def rest(self):
        self._set('REST')

    def atrc(self, display=None):
        cmd = ['Top', 'Bottom']
        if display is not None:
            self._set('ATRC {}'.format(cmd.index(display)))
        return cmd[int(self._query('ATRC?'))]

    def ascl(self):
        self._set('ASCL')

    def agan(self):
        self._set('AGAN')

    def arsv(self):
        self._set('ARSV')

    def aphs(self):
        self._set('APHS')

    def aoff(self, channel):
        cmd = ['', 'X', 'Y', 'R']
        self._set('AOFF {}'.format(cmd.index(channel)))

    def cmax(self):
        self._set('CMAX')
