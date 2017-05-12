"""Instrument base class for PLACE"""

class Instrument:
    """Generic interface to an instrument."""

    def config(self, json_string):
        """Called once at the beginning of a scan.

        :param json_string: a JSON-formatted configuration string
        :type json_string: str

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def update(self):
        """Called one or more times during a scan.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def cleanup(self):
        """Called at the end of a scan, or if there is an error along the way.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
