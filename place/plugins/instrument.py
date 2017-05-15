"""Instrument base class for PLACE"""

class Instrument:
    """Generic interface to an instrument."""
    def __init__(self):
        # instruments are updated based on priority (lowest first)
        self.priority = 100

    def config(self, header, json_string):
        """Called once at the beginning of a scan.

        :param header: metadata for the scan
        :type header: obspy.core.trace.Stats

        :param json_string: a JSON-formatted configuration string
        :type json_string: str

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def update(self, header):
        """Called one or more times during a scan.

        :param header: metadata for the scan
        :type header: obspy.core.trace.Stats

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def cleanup(self):
        """Called at the end of a scan, or if there is an error along the way.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
