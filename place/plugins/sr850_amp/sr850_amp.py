"""Stanford Research Systems SR850 DSP Lock-In Amplifier"""
from place.plugins.instrument import Instrument
from place.config import PlaceConfig

class SR850(Instrument):
    """PLACE module for controlling the SRS SR850 lock-in amplifier."""
    def config(self, metadata, total_updates):
        """Configure the amplifier.

        Typically, the amplifier will be configured at the beginning of an
        experiment, so the majority of the activity will happen in this method.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this
                              experiment
        :type total_updates: int
        """
        serial_port = PlaceConfig().get_config_value(self.__class__.__name__,
                                                     'serial_port', '/dev/ttys0')
        metadata['sr850_settings'] = {
            'serial_port': serial_port,
            }

    def update(self, update_number):
        """Perform updates to the amplifier during an experiment.

        All settings are set during the config phase, so this method does not
        currently do anything.

        :param update_number: the current update count
        :type update_number: int
        """
        pass

    def cleanup(self, abort=False):
        """Cleanup the amplifier.

        Nothing to cleanup.

        :param abort: indicates the experiment is being aborted rather than
                      having finished normally
        :type abort: bool
        """
        pass
