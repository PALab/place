"""Stanford Research Systems SR560 Pre-Amp

Note this plugin requires the following information to be present
in .place.cfg:: 

    serial_port = enter_value_here  #(e.g. /dev/ttyUSB0)
"""
from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from .sr560_driver import SR560Driver

class SR560PreAmp(Instrument):
    """PLACE module for controlling the SRS SR560 pre-amplifier.

    This module allows PLACE to set configuration options on the preamp at the
    start of an experiment. Currently, the module does not provide automation
    during an experiment. this module is a *convenience only* module designed
    to assist in recording the preamp setting used in an experiment.

    It should also be noted that the preamp is configured only as a listening
    serial port, meaning that the instrument settings cannot be read back from
    the instrument. Therefore, in an automated experiment, PLACE has no way to
    verify that the desired settings are being registered by the instrument.
    Users are advised to adequately test the communication with the instrument
    before leaving PLACE to perform a large experiment.

    .. note::
        A serial_search function is not available for this instrument
        as it is listen-only and cannot send back a response to
        indicate that it is connected.

    The SR560PreAmp plugin requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    blanking                  string         set blanking on or off. Either "blanked" or "not blanked"
    coupling                  string         the coupling type. Either "ground", "DC", or "AC"
    reserve                   string         the dynamic reserve type. One of "low noise", "high DR", or "calibration gains"
    filter_mode               string         the filter mode. See driver for options.
    gain                      string         the analog gain/amplification. See driver for options.
    highpass_filter           string         the highpass filter cutoff. See driver for options.
    lowpass_filter            string         the lowpass filter cutoff. See driver for options.
    signal_invert_sense       string         the inversion sense of the signal. Either "non-inverted" or "inverted"
    input_source              string         the input source channel. One of "A", "B", or "A-B"
    vernier_gain_status       string         the vernier gain status. Either "calibrated gain" or "vernier gain"
    vernier_gain              int            the vernier gain value as a percentage
    ========================= ============== ================================================

    The SR560PreAmp plugin will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    SR560_preamp_gain         int            the analog gain of the pre-amp
    ========================= ============== ================================================

    The MFLILockIn currently does not produce any experimental data.
    """

    def config(self, metadata, total_updates):
        """Configure the pre-amp.

        The pre-amp is entirely configured at the beginning of the experiment.
        Due to the small number of configuration options, this module requires
        values be specified for all the options and no defaults are assumed.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this
                              experiment
        :type total_updates: int
        """
        serial_port = PlaceConfig().get_config_value(self.__class__.__name__, 'serial_port')
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

        gain = self._config['gain']
        if gain[-1] == 'k':
            gain = int(gain[:-2])*1000
        else:
            gain = int(gain)
        metadata["SR560_preamp_gain"] = gain

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
