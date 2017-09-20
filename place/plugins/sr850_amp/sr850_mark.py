"""Mark commands"""
from .sr850_driver import SR850Driver

class SR850Mark(SR850Driver):
    """Mark commands"""
    def mark(self):
        """Place a mark in the data buffer at the next sample.

        This is the same as pressing the MARK key. This command has an effect
        only when a scan is in progress.
        """
        self._set('MARK')

    def cnxt(self):
        """docstring goes here"""
        pass

    def cprv(self):
        """docstring goes here"""
        pass

    def mdel(self):
        """docstring goes here"""
        pass

    def mact(self):
        """docstring goes here"""
        pass

    def mbin(self):
        """docstring goes here"""
        pass

    def mtxt(self):
        """docstring goes here"""
        pass
