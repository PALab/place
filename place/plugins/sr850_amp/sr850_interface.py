"""Interface commands"""
from .sr850_driver import SR850Driver

class SR850Interface(SR850Driver):
    """Interface commands"""
    def rst(self):
        """docstring goes here"""
        pass

    def idn(self):
        """docstring goes here"""
        pass

    def locl(self):
        """docstring goes here"""
        pass

    def ovrm(self):
        """docstring goes here"""
        pass

    def trig(self):
        """docstring goes here"""
        pass
