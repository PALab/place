"""Stanford Research Systems DS345 Function Generator"""
from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from .ds345_driver import DS345Driver

class DS345(Instrument):
    """PLACE module for reading data from the DS345 function generator."""
    def config(self, metadata, total_updates):
        """PLACE module for reading data from the DS345 function generator.

        Currently, this module is only designed to record the settings on the
        function generator.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this
                              experiment
        :type total_updates: int
        """
        serial_port = PlaceConfig().get_config_value(self.__class__.__name__,
                                                     'serial_port', '/dev/ttys0')
        name = self.__class__.__name__
        function_gen = DS345Driver(serial_port)


    def update(self, update_number):
        """Perform updates to the pre-amp during an experiment.

        All settings are set during the config phase, so this method does not
        currently do anything.

        :param update_number: the current update count
        :type update_number: int
        """
        pass

    def cleanup(self, abort=False):
        """Cleanup the pre-amp.

        Nothing to cleanup.

        :param abort: indicates the experiment is being aborted rather than
                      having finished normally
        :type abort: bool
        """
        pass
