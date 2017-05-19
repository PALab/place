"""Instrument base class for PLACE"""

class Instrument:
    """Generic interface to an instrument."""
    def __init__(self, config):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        # instruments are updated based on priority (lowest first)
        self._config = config
        self.priority = 100

    def config(self, header=None):
        """Called once at the beginning of a scan.

        :param header: metadata for the scan
        :type header: obspy.core.trace.Stats

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def update(self, header=None, socket=None):
        """Called one or more times during a scan.

        :param header: metadata for the scan
        :type header: obspy.core.trace.Stats

        :param socket: websocket for sending plot data back to the webapp
        :type socket: websocket

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def cleanup(self):
        """Called at the end of a scan, or if there is an error along the way.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
