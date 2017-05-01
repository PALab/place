"""Instrument base class

This file contains the class upon which all other instruments are created. It
is essentially an interface of methods which must by defined by subclasses.
"""

class Instrument:
    """A PLACE instrucment base class"""
    def cleanup(self):
        """Called by Scan when objects are no longer needed, so they have a
        chance to disconnects, shutdown, etc."""
        raise NotImplementedError
