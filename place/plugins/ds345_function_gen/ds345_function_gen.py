"""Stanford Research Systems DS345 Function Generator"""
import time

from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from .ds345_driver import DS345Driver


class DS345(Instrument):
    """PLACE module for reading data from the DS345 function generator.

    Activating the function generator module will produce the following
    experimental metadata:

    =========================== ============== ==============================================
    Key                         Type           Meaning
    =========================== ============== ==============================================
    DS345_stop_freq             float          Sweep stop freqency.
    DS345_start_freq            float          Sweep start frequency.
    DS345_sweep_duration        float          The duration of each sweep.
    =========================== ============== ==============================================
    """

    def __init__(self, config, plotter):
        """Constructor"""
        Instrument.__init__(self, config, plotter)
        self.vary_amplitude = False
        self.current_amplitude = 5.0
        self.amplitude_increment = 0.0

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

        name = self.__class__.__name__
        serial_port = PlaceConfig().get_config_value(name, "port")
        self.function_gen = DS345Driver(serial_port)

        self.vary_amplitude = self._config["vary_amplitude"] 
        
        if self._config["mode"] == "freq_sweep":
            self.function_gen.func(function_type="SINE")
            self.function_gen.stfr(frequency=self._config["start_freq"])
            self.function_gen.spfr(frequency=self._config["stop_freq"])
            self.function_gen.offs(dc_offset=0.0)
            self.function_gen.ampl(amplitude=self._config["start_amplitude"])
            self.function_gen.rate(rate=1./self._config["sweep_duration"])
            self.function_gen.tsrc(source="SINGLE")
            self.function_gen.mtyp(modulation="LIN SWEEP")
            self.function_gen.mdwf(waveform="SINGLE SWEEP")
            self.function_gen.mena(modulation=True)
            time.sleep(3)    #Future comms seem to fail without a pause

            metadata['DS345_start_freq'] = self._config["start_freq"]
            metadata['DS345_stop_freq'] = self._config["stop_freq"]
            metadata['DS345_sweep_duration'] = self._config["sweep_duration"]

            if total_updates > 1:
                self.amplitude_increment = (self._config["stop_amplitude"] - self._config["start_amplitude"]) / (total_updates - 1)
            self.current_amplitude = self._config["start_amplitude"]

        self._read_settings()

    def update(self, update_number, progress):
        """Perform updates to the pre-amp during an experiment.

        All settings are set during the config phase, so this method does not
        currently do anything.

        :param update_number: the current update count
        :type update_number: int

        :param progress: A blank dictionary that is sent to your Elm module
        :type progress: dict
        """

        if self.vary_amplitude and update_number > 0:
            self.current_amplitude += self.amplitude_increment
            self.function_gen.ampl(amplitude=self.current_amplitude)

        if self._config["mode"] == "freq_sweep":
            print("triggering ds345:",time.time())
            self.function_gen.trg()  
            
            if self._config["wait_for_sweep"]:
                time.sleep(self._config["sweep_duration"] + 1)


    def cleanup(self, abort=False):
        """Cleanup the pre-amp.

        Nothing to cleanup.

        :param abort: indicates the experiment is being aborted rather than
                      having finished normally
        :type abort: bool
        """
        self.function_gen.ampl(amplitude=0.0)  #Set the amplitude to 0


    def _read_settings(self):
        """Read the settings from the DS345 and put them into the config"""

        settings_from_instrument = {}
        settings_from_instrument['output_amplitude'] = self.function_gen.ampl(units=None)[0]
        settings_from_instrument['output_frequency'] = self.function_gen.freq()
        settings_from_instrument['sampling_frequency'] = self.function_gen.fsmp()
        settings_from_instrument['output_function'] = self.function_gen.func()
        settings_from_instrument['inversion_status'] = self.function_gen.invt()
        settings_from_instrument['DC_offset'] = self.function_gen.offs()
        settings_from_instrument['modulation_waveform'] = self.function_gen.mdwf()
        settings_from_instrument['burst_count'] = self.function_gen.bcnt()
        settings_from_instrument['modulation_depth'] = self.function_gen.dpth()
        settings_from_instrument['span'] = self.function_gen.fdev()
        settings_from_instrument['modulation_enabled'] = self.function_gen.mena()
        settings_from_instrument['mark_freq_start'] = self.function_gen.mrkf('START')
        settings_from_instrument['mark_freq_stop'] = self.function_gen.mrkf('STOP')
        settings_from_instrument['mark_freq_center'] = self.function_gen.mrkf('CENTER')
        settings_from_instrument['mark_freq_span'] = self.function_gen.mrkf('SPAN')
        settings_from_instrument['modulation_type'] = self.function_gen.mtyp()
        settings_from_instrument['phase_mod_span'] = self.function_gen.pdev()
        settings_from_instrument['modulation_rate'] = self.function_gen.rate()
        settings_from_instrument['sweep_span'] = self.function_gen.span()
        settings_from_instrument['sweep_center'] = self.function_gen.spcf()
        settings_from_instrument['sweep_stop'] = self.function_gen.spfr()
        settings_from_instrument['sweep_start'] = self.function_gen.stfr()
        settings_from_instrument['trigger_rate'] = self.function_gen.trat()
        settings_from_instrument['trigger_source'] = self.function_gen.tsrc()
        settings_from_instrument['divider'] = self.function_gen.amrt()
        if (settings_from_instrument['modulation_type'] not in ['LIN SWEEP', 'LOG SWEEP', 'FM', 'PHI_M']
                and settings_from_instrument['output_function'] not in ['NOISE', 'ARBITRARY']):
            settings_from_instrument['output_phase'] = self.function_gen.phse()

        self._config["settings_from_instrument"] = settings_from_instrument
