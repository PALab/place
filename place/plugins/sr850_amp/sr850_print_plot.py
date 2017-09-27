"""Print and plot commands"""
from .sr850_driver import SR850Driver

class SR850PrintPlot(SR850Driver):
    """Print and plot commands"""
    def prsc(self):
        self._set('PRSC')

    def pall(self):
        self._set('PALL')

    def ptrc(self):
        self._set('PTRC')

    def pcur(self):
        self._set('PCUR')
