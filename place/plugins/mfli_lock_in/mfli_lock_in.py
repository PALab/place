"""PLACE driver for the Zurich Instruments Lock-In
amplifier.

This module interfaces with the MFLI via the data server, most
easily accessed via the corresponding MFLI Python wrapper.

Note the MFLi requires the following information to be present
in .place.cfg: device_name (e.g. dev4050) and device_ip 
(e.g. 192.168.1.20)
"""
import time
import numpy as np

from place.config import PlaceConfig
from place.plugins.instrument import Instrument

from .mfli_driver import MFLIDriver


class MFLILockIn(Instrument):
    """The Zurich Instruments MFLI Lock-in class

    The MFLILockIn module requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    mode                      string         the mode that the instrument was being used in
    sigin_imp                 string         the input impedance of the signal input
    sigin_range               string         the input range for the signal (voltage) input
    ext_ref_channel           string         the channel to use for the external reference
    ext_ref_mode              string         the automode for the external reference
    demod_phaseshfit          float          the phaseshift for the demodulator
    demod_filter_en           bool           enables or disables the demod filter
    timeconstant              float          the timeconstant for the demod filter (in s)
    sampling_rate             float          the sampling rate for data acquisition (in Hz)
    acquisition_time          float          the duration of the acquisition (in s)
    trigger_source            string         the channel for the trigger
    trigger_type              string         the type of trigger (i.e. rising or falling)
    trigger_level             float          the level of the trigger (in V)
    trig_level_auto_range     bool           enables or disables automatic setting of the trigger level
    plot                      bool           turns live plotting on or off
    ========================= ============== ================================================

    The MFLILockIn module will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    mfli_actual_sampling_rate float          the actual sampling rate of the data in Hz
    ========================= ============== ================================================

    The MFLILockIn will produce the following experimental data:

    +---------------+-------------------------+---------------------------+
    | Heading       | Type                    | Meaning                   |
    +===============+=========================+===========================+
    | trace         | uint64                  | the data level recorded   |
    |               |                         | from the MFLI Lock In     |
    +---------------+-------------------------+---------------------------+

    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``trace`` will be recorded as ``MFLILockIn-trace`` when using
        the MFLI lock-in. The reason for this is because NumPy will not
        check for duplicate heading names automatically, so prepending the
        class name greatly reduces the likelihood of duplication.

    """

    def __init__(self, config, plotter):
        """Constructor"""

        Instrument.__init__(self, config, plotter)
        self.mfli = None 
        self.actual_sampling_rate = None

    def config(self, metadata, total_updates):
        """Configure the mfli.

        :param metadata: experiment metadata
        :type metadata: dict

        :param total_updates: number of updates for the experiment
        :type total_updates: int
        """

        name = self.__class__.__name__
        self.mfli = MFLIDriver( PlaceConfig().get_config_value(name, "device_name"), 
                                PlaceConfig().get_config_value(name, "device_ip"),
                                port=8004)
        self.total_updates = total_updates

        if self._config["mode"] == "lockin_amp":
            self._config_sigin()
            self._config_extref()
            self._config_demod()
            self._config_acquisition()

            metadata["mfli_actual_sampling_rate"] = self.actual_sampling_rate
            
            self.mfli.start_acquisition(wait=False)

        
    def update(self, update_number, progress):
        """Update the MFLI.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param progress: a dictionary of values passed back to your Elm app
        :type progress: dict

        :returns: an array containing the recorded data. The shape of the
            array is Nx2xJ where N is the number of channels recorded and
            J is the number of samples in each acquisition. There are two
            arrays for each channel, the first containing the time values
            and the second containing the data values.
        :rtype: numpy.array dtype='uint64'
        """

        data = self.mfli.get_data(wait_for_finished=True)

        print(data.shape)

        type_str = '{}float'.format(data.shape)
        field = '{}-trace'.format(self.__class__.__name__)
        reshaped_data = np.zeros((1,), dtype=[(field, type_str)])

        print('reshaped field:', reshaped_data[field].shape)

        for channel in range(data.shape[0]):
            reshaped_data[field][0][channel][0] = data[channel][0]
            reshaped_data[field][0][channel][1] = data[channel][1]

        print('reshaped:', reshaped_data.shape)

        if self._config['plot']:
            self._draw_plot(reshaped_data, field)

        if update_number < self.total_updates - 1:
            self.mfli.start_acquisition(wait=False)
            

        return reshaped_data

    def cleanup(self, abort=False):
        """Free resources and cleanup.

        Display the final plot, unless aborted or plotting is disabled.

        :param abort: indicates that the experiment is being aborted and is unfinished
        :type abort: bool
        """

        self.mfli.disconnect()

    ### Private methods ###    

    def _config_sigin(self):
        """Configure the signal input"""

        sigin_params = ["on"]
        sigin_values = [1]

        sigin_params.append("imp50")
        if self._config["sigin_imp"] == "50_ohm":
            sigin_values.append(1)
        else:
            sigin_values.append(0)

        sigin_config_ranges = ["auto","3_mv","10_mv","30_mv","100_mv","300_mv","1_v","3_v"]
        sigin_range_index = sigin_config_ranges.index(self._config["sigin_range"]) 
        if sigin_range_index == 0:
            sigin_params.append('autorange')       
            sigin_values.append(1)
        else:
            sigin_range_values = ["_",0.003,0.01,0.03,0.1,0.3,1.,3.]
            sigin_params.append('range')       
            sigin_values.append(sigin_range_values[sigin_range_index])

        self.mfli.configure_voltage_input(sigin_params, sigin_values)


    def _config_extref(self):
        """Configure the external reference"""

        ext_ref_params = ["enable"]
        ext_ref_values = [1]

        ext_ref_params.append("automode")
        if self._config["ext_ref_mode"] == "auto":
            ext_ref_values.append(4)
        elif self._config["ext_ref_mode"] == "low_bw":
            ext_ref_values.append(2)
        elif self._config["ext_ref_mode"] == "high_bw":
            ext_ref_values.append(3)

        self.mfli.configure_reference(ext_ref_params, ext_ref_values, demod_index=0)
        
        if self._config["ext_ref_channel"] == "auxin_1":
            ext_channel = 8
        elif self._config["ext_ref_channel"] == "auxin_2":
            ext_channel = 9
        self.mfli.configure_demod(["adcselect"], [ext_channel], demod_index=1)


    def _config_demod(self):
        """Configure the demodulator"""

        demod_params = ["enable", "adcselect","order"]
        demod_values = [1, 0, 3]
        
        demod_params.append("phaseshift")
        demod_values.append(float(self._config["demod_phaseshfit"]))

        demod_params.append("rate")
        demod_values.append(float(self._config["sampling_rate"]))
        
        if self._config["demod_filter_en"]:
            demod_params.append("bypass")
            demod_values.append(0)
            demod_params.append("timeconstant")
            demod_values.append(self._config["timeconstant"])
        else:
            demod_params.append("bypass")
            demod_values.append(1)

        if self._config["trigger_source"] == "trigin_1":
            if self._config["trigger_type"] == "pos_edge":
                trig_val = 1
            else:
                trig_val = 2
            demod_params.append("trigger")
            demod_values.append(trig_val)
        elif self._config["trigger_source"] == "trigin_2":
            if self._config["trigger_type"] == "pos_edge":
                trig_val = 4
            else:
                trig_val = 8
            demod_params.append("trigger")
            demod_values.append(trig_val)

        self.mfli.configure_demod(demod_params, demod_values, demod_index=0)
        self.actual_sampling_rate = self.mfli.get_demod_parameter("rate", demod_index=0)
        self._config["sampling_rate"] = self.actual_sampling_rate

    def _config_acquisition(self):
        """Configure the data acquisition"""

        if self._config["trig_level_auto_range"]:
            trig_level = "auto"
        else:
            trig_level = float(self._config["trigger_level"])
        
        if self._config["trigger_type"] == "pos_edge":
            trig_edge = "rising"
        else:
            trig_edge = "falling"

        self.mfli.configure_acquisition(["demod_r"], [0], mode='exact', 
                            sampling_rate=self.actual_sampling_rate,
                            duration=float(self._config["acquisition_time"]), count=1, 
                            trig_source=self._config["trigger_source"], trig_type='edge', 
                            trig_edge=trig_edge, trig_level=trig_level, endless=False)


    def _draw_plot(self, data, header):
        """Draw a plot"""

        trace_data = data[header][0]        
        print(trace_data.shape)

        for i in range(trace_data.shape[0]):
            xdata = trace_data[i][0]
            ydata = trace_data[i][1]
            print(xdata.shape, ydata.shape)
            title = "MFLI Channel {} Data".format(i)
            
            self.plotter.view(
                title,
                [
                    self.plotter.line(
                        ydata,
                        xdata=xdata,
                        color='blue',
                        shape='none',
                        label="Channel "+str(i)
                    )
                ]
            )
            