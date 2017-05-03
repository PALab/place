"""Instrument base class

This file contains the class upon which all other instruments are created. It
is essentially an interface of methods which must by defined by subclasses.
"""

class Instrument:
    """A PLACE instrucment base class"""
    def config(self, config_string):
        """Configure the instrument.

        Instruments are configured using a JSON-formatted string, which should
        contain any parameters the instrument needs. The Scan object will pass
        the JSON configuration into the instrument using this method.

        :param config_string: JSON-formatted configuration
        :type config_string: str
        """
        raise NotImplementedError

    def update(self):
        """Perform instrument updates.

        This method is called once for each action specified in the scan. For
        example, if the instrument is a stage, this is when it should change
        its position.
        """
    def cleanup(self):
        """Called by Scan when objects are no longer needed, so they have a
        chance to disconnects, shutdown, etc."""
        raise NotImplementedError
