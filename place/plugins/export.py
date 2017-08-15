"""Exporting base class for PLACE"""
class Export: # pylint: disable=too-few-public-methods
    """Interface for exporting data generated in PLACE into another format.

    This class is a base class for converting the NumPy structured array
    produced by PLACE into another format. This allows more flexibility for
    labs to make PLACE work the way they want.
    """
    def __init__(self, config):
        """Constructor

        Stores the JSON config data submitted for the experiment into a class
        dictionary. Subclasses can certainly repeat this or override it, but it
        is done here anyway.

        :param config: configuration data (from JSON)
        :type config: dict
        """
        self._config = config

    def export(self, path):
        """Convert and export the NumPy data into a custom format.

        This function is provided with the path to the experiment directory. It
        will need to open the data files on its own and perform the
        transformation on its own. This function should open all files as
        read-only and not make any changes to existing files. Only new files
        should be created and modified.

        This function is called during the cleanup phase and is only called if
        the *abort* flag has not been set.

        :param path: the path with the experimental data, config data, etc.
        :type path: str

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
