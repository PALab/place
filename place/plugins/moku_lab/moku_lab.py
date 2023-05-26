"""The PLACE module for the Moku:Lab.

Currently, only a frequency response analyzer is
implemented, but the Moku:Lab instrument has much greater
functionality than this. Further features can be added
to this module as required.

Note the MokuLab plugin requires the following information to be present
in .place.cfg:: 

    time_safety_net = enter_value_here  #(e.g. 3.0)
    ip_address = enter_value here       #(e.g. 192.168.1.20)
"""
import calendar
import time

import numpy as np

from place.config import PlaceConfig
from place.plugins.instrument import Instrument

try:
    from pymoku import Moku
    from pymoku.instruments import BodeAnalyzer
except ImportError:
    pass


# Maximum and minimum number of points per sweep.
MAX_P = 512
MIN_P = 32


class MokuLab(Instrument):
    """The MokuLab class for place. This currently only implements a frequency
    response analyser.
    
    The MokuLab plugin requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    f_start                   float          the starting frequency of the sweep
    f_end                     float          the stop frequency in the sweep
    data_points               int            the number of data points in the frequency sweep
    ch1_amp                   float          the output voltage of channel 1
    ch2_amp                   float          the output voltage of channel 2
    averaging_time            float          the amount of time to average over for each frequency (in seconds)
    settling_time             float          the amount of time to allow for settling before recording at each frequency point (seconds)
    averaging_cycles          int            the number of cycles to average over for each frequency point
    settling_cycles           int            the number of cycles to allow for settling before recording at each frequency point
    single_sweep              bool           True to perform only a single sweep
    channel                   string         the active channel. Can be "ch1", "ch2", or "both"
    plot                      string         the channel to plot
    pause                     bool           whether to pause the acquisition
    ========================= ============== ================================================

    The MokuLab module will produce the following experimental metadata:

    ============================== ============== ================================================
    Key                            Type           Meaning
    ============================== ============== ================================================
    MokuLab-predicted-update-time  float          the predicted time for one update
    ============================== ============== ================================================

    The MokuLab will produce the following experimental data:

    ======================= ================================================================ ===========================
    Heading                 Type                                                             Meaning                   
    ======================= ================================================================ ===========================
    ch1_magnitude_data      (frequency,magnitude)xN float64 where N is number of data points the output frequency and recorded magnitude (in dB) for channel 1 (if active)            
    ch1_phase_data          (frequency,phase)xN float64 where N is number of data points     the output frequency and recorded phase for channel 1 (if active)
    ch2_magnitude_data      (frequency,magnitude)xN float64 where N is number of data points the output frequency and recorded magnitude (in dB) for channel 2 (if active)            
    ch2_phase_data          (frequency,phase)xN float64 where N is number of data points     the output frequency and recorded phase for channel 2 (if active)
    ======================= ================================================================ ===========================
    
    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``ch1_magnitude_data`` will be recorded as ``MokuLab-ch1_magnitude_data``. 
        The reason for this is because NumPy will not check for duplicate heading 
        names automatically, so prepending the class name greatly reduces the 
        likelihood of duplication.

    """

    def __init__(self, config, plotter):
        """Initialize the MokuLab, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict

        :param plotter: a plotting object to return plots to the web interface
        :type plotter: plots.PlacePlotter
        """
        Instrument.__init__(self, config, plotter)
        self.total_updates = None
        self.sweeps = None
        self.moku = None
        self.bode = None
        self.time_safety_net = None

    def config(self, metadata, total_updates):
        """
        Called by PLACE at the beginning of the experiment to get everything up and running.
        """
        self.total_updates = total_updates
        name = self.__class__.__name__
        tsn_str = PlaceConfig().get_config_value(name, 'time_safety_net', '3.0')
        self.time_safety_net = float(tsn_str)
        metadata['MokuLab-predicted-update-time'] = self._predicted_sweep_time()
        self.sweeps = _calc_sweeps(
            f_start=self._config['f_start'],
            f_end=self._config['f_end'],
            n_pts=self._config['data_points']
        )

    def update(self, update_number, progress):
        """
        Called by PLACE during the experiment, update_number of times.
        """
        framedata = {
            "freq": [],
            "ch1_mag": [],
            "ch2_mag": [],
            "ch1_phase": [],
            "ch2_phase": []
        }
        for sweep in self.sweeps:
            self._set_up_moku_sweep(sweep)
            framedata = self._get_and_plot_live_data(
                progress, framedata, sweep
            )
        if self._config['data_points'] % 2 != 0:
            framedata = cut_last_point(framedata)
        self._print_statements(update_number)
        return self._save_data(framedata)

    def cleanup(self, abort=False):
        """Nothing to cleanup"""
        pass

    def _set_up_moku_sweep(self, sweep):
        ip_address = PlaceConfig().get_config_value(
            self.__class__.__name__, 'ip_address')
        ch1_amp = self._config['ch1_amp']
        ch2_amp = self._config['ch2_amp']
        self.moku = Moku(ip_address)
        self.bode = self.moku.deploy_or_connect(BodeAnalyzer)
        try:
            # or self._config['data_points'] % 2 != 0:
            self.bode.set_xmode('sweep')
            self.bode.set_output(1, ch1_amp)
            self.bode.set_output(2, ch2_amp)
            self.bode.set_frontend(
                channel=1, ac=True, atten=False, fiftyr=False)
            self.bode.set_frontend(
                channel=2, ac=True, atten=False, fiftyr=False)
        except:
            self.moku.close()
            raise
        self.bode.set_sweep(
            sweep[0] * 1000,
            sweep[-1] * 1000,
            len(sweep),
            False,
            self._config['averaging_time'],
            self._config['settling_time'],
            self._config['averaging_cycles'],
            self._config['settling_cycles'])
        self.bode.start_sweep(single=self._config['single_sweep'])

    def _get_and_plot_live_data(self, progress, framedata, sweep):
        sweep_time = self._predicted_sweep_time(pts=len(sweep))
        then = calendar.timegm(time.gmtime())
        now = then
        frame = self.bode.get_realtime_data()
        while sweep_time * self.time_safety_net > now - then:
            flag = 0
            sweepdata = {
                "freq": (np.array(frame.frequency)/1000).tolist(),
                "ch1_mag": frame.ch1.magnitude_dB,
                "ch1_phase": frame.ch1.phase,
                "ch2_mag": frame.ch2.magnitude_dB,
                "ch2_phase": frame.ch2.phase}
            sweepdata = replace_none_dictionary(sweepdata)
            if (sweep == self.sweeps[-1]
                    and (self._config['data_points'] % 2 != 0)
                    and sweepdata['ch1_mag'][-2]
                    and sweepdata['ch2_mag'][-2]
                    and sweepdata['ch1_phase'][-2]
                    and sweepdata['ch2_phase'][-2] is not np.nan):
                sweepdata = cut_last_point(sweepdata)
            self._live_progress(
                channel=1,
                progress=progress,
                framedata=merge_dictionaries(framedata, sweepdata)
            )
            self._live_progress(
                channel=2,
                progress=progress,
                framedata=merge_dictionaries(framedata, sweepdata)
            )
            for key in sweepdata:
                if key != 'freq':
                    if sweepdata[key][-1] is not np.nan:
                        flag = 1
                        break
            if flag == 1:
                break
            now = calendar.timegm(time.gmtime())
            frame = self.bode.get_realtime_data()
        framedata = merge_dictionaries(framedata, sweepdata)
        self.moku.close()
        return framedata

    def _live_progress(self, channel, progress, framedata):
        other_channel = 1 if channel == 2 else 2
        if self._config['channel'] != 'ch{}'.format(other_channel):
            raw_mag = framedata['ch{}_mag'.format(channel)]
            mag = []
            for x in raw_mag:
                if np.isnan(x):
                    break
                mag.append(x)
            raw_phase = framedata['ch{}_phase'.format(channel)]
            phase = []
            for x in raw_phase:
                if np.isnan(x):
                    break
                phase.append(x)
            mag_freq = framedata['freq'][:len(mag)]
            phase_freq = framedata['freq'][:len(phase)]
            self.plotter.view(
                'Channel {} Magnitude'.format(channel),
                [
                    self.plotter.line(
                        ydata=mag,
                        xdata=mag_freq,
                        color="green",
                        shape="none",
                        label="magnitude"
                    )
                ]
            )
            self.plotter.view(
                'Channel {} Phase'.format(channel),
                [
                    self.plotter.line(
                        ydata=phase,
                        xdata=phase_freq,
                        color="purple",
                        shape="none",
                        label="phase"
                    )
                ]
            )

    def _save_data(self, framedata):
        freq = framedata['freq']
        mag = [framedata['ch1_mag'], framedata['ch2_mag']]
        phase = [framedata['ch1_phase'], framedata['ch2_phase']]
        linedata = {
            "mag": [np.array([[freq[i], mag[0][i]] for i in range(
                min(len(freq), len(mag[0])))]),
                np.array([[freq[i], mag[1][i]] for i in range(
                    min(len(freq), len(mag[1])))])],
            "phase": [np.array([[freq[i], phase[0][i]] for i in range(
                min(len(freq), len(phase[0])))]),
                np.array([[freq[i], phase[1][i]] for i in range(
                          min(len(freq), len(phase[1])))])]
        }
        fielddata = {
            "mag": ['{}-ch1_magnitude_data'.format(self.__class__.__name__),
                    '{}-ch2_magnitude_data'.format(self.__class__.__name__)],
            "phase": ['{}-ch1_phase_data'.format(self.__class__.__name__),
                      '{}-ch2_phase_data'.format(self.__class__.__name__)]
        }
        shape = '({},2)float64'.format(self._config['data_points'])
        if self._config['channel'] == 'ch1':
            data = np.array(
                [(linedata['mag'][0], linedata['phase'][0])],
                dtype=[(fielddata['mag'][0], shape), (fielddata['phase'][0], shape)])
        if self._config['channel'] == 'ch2':
            data = np.array(
                [(linedata['mag'][1], linedata['phase'][1])],
                dtype=[(fielddata['mag'][1], shape), (fielddata['phase'][1], shape)])
        if self._config['channel'] == 'both':
            data = np.array(
                [(linedata['mag'][0], linedata['phase'][0],
                  linedata['mag'][1], linedata['phase'][1])],
                dtype=[(fielddata['mag'][0], shape), (fielddata['phase'][0], shape),
                       (fielddata['mag'][1], shape), (fielddata['phase'][1], shape)])
        return data.copy()

    def _print_statements(self, update_number):
        if update_number == self.total_updates - 2:
            print('Almost there, I have 1 more update to work through.')
            if self._config['pause'] and self._config['plot'] != 'no':
                print(
                    'Double-click the figure when you\'re ready to move on to the next update.')
                print('Cheers mate.')
        elif update_number == self.total_updates - 1:
            print("I've finished the final sweep.")
            if self._config['pause'] and self._config['plot'] != 'no':
                print('Please close the plot to wrap up your experiment.')
            print('May the odds be ever in your favor.')

        else:
            print("Don't celebrate yet,")
            print('I have {} more updates to work through.'.format(
                self.total_updates - (update_number + 1)))
            if self._config['pause'] and self._config['plot'] != 'no':
                print(
                    'I need you to double-click the figure when you\'re ready for me to continue.')
                print('Cheers mate.')

    def _predicted_sweep_time(self, pts=None):
        """
        Empirical equation for sweep time estimates.

        Note: rough estimate, lower freuqencies take longer (such as around 20kHz)
        """
        a_1 = self._config['averaging_time']
        a_2 = self._config['averaging_cycles']
        s_1 = self._config['settling_time']
        s_2 = self._config['settling_cycles']
        if pts is None:
            pts = self._config['data_points']
        return max(a_1*pts, (a_2/10000)*(pts/3.75)) + max(s_1*pts, (s_2/10000)*(pts/3.75))


def _calc_sweeps(f_start, f_end, n_pts):
    """
    Calculates the frequencies that will be sent through the core.
    Splits them into sweeps of allowed length.
    """
    points, step = np.linspace(f_start, f_end, n_pts, retstep=True)
    if n_pts % 2 != 0:
        points = np.linspace(f_start, f_end + step, n_pts + 1)
    points = points.tolist()
    sweeps = [points[x:x+MAX_P] for x in range(0, len(points), MAX_P)]
    if len(sweeps[-1]) < MIN_P:
        sweeps[-1] = sweeps[-2][-MIN_P:] + sweeps[-1]
        sweeps[-2] = sweeps[-2][:-MIN_P]
    return sweeps


def _add_to_wiggle_plot(data, freq, shift, axes):
    wiggle = data / np.amax(np.abs(data)) + shift
    axes.plot(wiggle, freq, color='black', linewidth=0.5)
    positive = [not np.isnan(x) and x > shift for x in wiggle]
    axes.fill_betweenx(freq, wiggle, shift, where=positive, color='black')


def merge_dictionaries(d_1, d_2):
    """
    Merges dictionaries so that second is integrated into first.
    Returns extended first dictionary.
    """
    d_3 = {}
    for key1, value1 in d_1.items():
        d_3[key1] = value1
        for key2, value2 in d_2.items():
            if key1 == key2:
                d_3[key1] = value1 + value2
                break
        else:
            d_3[key2] = value2
    return d_3


def replace_none_dictionary(d_1):
    """
    Replaces all None's in dictionary with nan.
    """
    no_none_d_1 = {}
    for key in d_1:
        no_none_d_1[key] = [np.nan if x is None else x for x in d_1[key]]
    return no_none_d_1


def cut_last_point(d_1):
    """
    Removes last point of final framedata that was added to avoid None for odd points.
    """
    finaldata = {}
    for key in d_1:
        finaldata[key] = d_1[key][:-1]
    return finaldata
