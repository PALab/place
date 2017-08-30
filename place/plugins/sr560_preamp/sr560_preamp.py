"""Stanford Research Systems SR560 Pre-Amp"""
from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from .sr560_driver import SR560Driver

class SR560PreAmp(Instrument):
    """PLACE module for controlling the SRS SR560 pre-amplifier."""
    def config(self, metadata, total_updates):
        """Configure the pre-amp.

        The pre-amp is entirely configured at the beginning of the scan. Due to
        the small number of configuration options, this module requires values
        be specified for all the options and no defaults are assumed.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this
                              experiment
        :type total_updates: int
        """
        serial_port = PlaceConfig().get_config_value(self.__class__.__name__,
                                                     'serial_port', '/dev/ttys0')
        preamp = SR560Driver(serial_port)
        preamp.set_defaults()
        preamp.set_blanking(self._config['blanking'])
        preamp.set_coupling(self._config['coupling'])
        preamp.set_reserve(self._config['reserve'])
        preamp.set_filter_mode(self._config['filter_mode'])
        preamp.set_gain(self._config['gain'])
        preamp.set_highpass_filter(self._config['highpass_filter'])
        preamp.set_lowpass_filter(self._config['lowpass_filter'])
        preamp.set_signal_invert_sense(self._config['signal_invert_sense'])
        preamp.set_input_source(self._config['input_source'])
        preamp.set_vernier_gain_status(self._config['vernier_gain_status'])
        preamp.set_vernier_gain(self._config['vernier_gain'])

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
