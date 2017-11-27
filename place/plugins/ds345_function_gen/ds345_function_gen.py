"""Stanford Research Systems DS345 Function Generator"""
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
    DS345-output_amplitude      float          The output amplitude (in Vpp).
    DS345-output_frequency      float          The output frequency (1 micro-Hz resolution).
    DS345-sampling_frequency    float          The arbitrary wavesform sampling frequency.
    DS345-output_function       str            The function type.
    DS345-inversion_status      str            Inversion status (on/off).
    DS345-DC_offset             float          The current value of the DC offset.
    DS345-output_phase          float          The waveform output phase.
    DS345-burst_count           int            The current burst count.
    DS345-modulation_depth      int            The current modulation depth.
    DS345-span                  float          The current span.
    DS345-modulation_waveform   str            The current modulation waveform.
    DS345-modulation_enabled    bool           Whether modulation is enabled.
    DS345-mark_freq_start       float          The current sweep marker start frequency.
    DS345-mark_freq_stop        float          The current sweep marker stop frequency.
    DS345-mark_freq_center      float          The current sweep marker center frequency.
    DS345-mark_freq_span        float          The current sweep marker span frequency.
    DS345-modulation_type       str            The current modulation type.
    DS345-phase_mod_span        float          The current phase shift.
    DS345-modulation_rate       float          The current modulation rate.
    DS345-sweep_span            float          The current sweep span.
    DS345-sweep_center          float          The current sweep center frequency.
    DS345-sweep_stop            float          The current sweep stop freqency.
    DS345-sweep_start           float          The current sweep start frequency.
    DS345-trigger_rate          float          The current trigger rate.
    DS345-trigger_source        str            The current trigger source.
    DS345-divider               int            The current arbitrary modulation rate
                                               divider.
    =========================== ============== ==============================================
    """

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
        function_gen = DS345Driver(serial_port)
        metadata['DS345-output_amplitude'] = function_gen.ampl()[0]
        metadata['DS345-output_frequency'] = function_gen.freq()
        metadata['DS345-sampling_frequency'] = function_gen.fsmp()
        metadata['DS345-output_function'] = function_gen.func()
        metadata['DS345-inversion_status'] = function_gen.invt()
        metadata['DS345-DC_offset'] = function_gen.offs()
        metadata['DS345-output_phase'] = function_gen.phse()
        metadata['DS345-burst_count'] = function_gen.bcnt()
        metadata['DS345-modulation_depth'] = function_gen.dpth()
        metadata['DS345-span'] = function_gen.fdev()
        metadata['DS345-modulation_waveform'] = function_gen.mdwf()
        metadata['DS345-modulation_enabled'] = function_gen.mena()
        metadata['DS345-mark_freq_start'] = function_gen.mrkf('START')
        metadata['DS345-mark_freq_stop'] = function_gen.mrkf('STOP')
        metadata['DS345-mark_freq_center'] = function_gen.mrkf('CENTER')
        metadata['DS345-mark_freq_span'] = function_gen.mrkf('SPAN')
        metadata['DS345-modulation_type'] = function_gen.mtyp()
        metadata['DS345-phase_mod_span'] = function_gen.pdev()
        metadata['DS345-modulation_rate'] = function_gen.rate()
        metadata['DS345-sweep_span'] = function_gen.span()
        metadata['DS345-sweep_center'] = function_gen.spcf()
        metadata['DS345-sweep_stop'] = function_gen.spfr()
        metadata['DS345-sweep_start'] = function_gen.stfr()
        metadata['DS345-trigger_rate'] = function_gen.trat()
        metadata['DS345-trigger_source'] = function_gen.tsrc()
        metadata['DS345-divider'] = function_gen.amrt()

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
