"""The PLACE module for the Moku:Lab"""
import calendar
import time
#from warnings import warn
import numpy as np
import matplotlib.pyplot as plt
from place.plugins.instrument import Instrument
from place.config import PlaceConfig

try:
    from pymoku import Moku
    from pymoku.instruments import BodeAnalyzer
except ImportError:
    pass

#Maximum and minimum number of points per sweep.
MAX_P = 512
MIN_P = 32


class MokuLab(Instrument):
    """The MokuLab class for place"""


    def __init__(self, config):
        """
        Initialize the MokuLab, without configuring.
        :param config: configuration data (as a parsed JSON object)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self.total_updates = None
        self.sweeps = None
        self.ax_ = [[], []]
        self.moku = None
        self.i = None
        self.time_safety_net = None
        self.lines = None


    def config(self, metadata, total_updates):
        """
        Called by PLACE at the beginning of the experiment to get everything up and running.
        """
        self.total_updates = total_updates
        self.time_safety_net = float(PlaceConfig().get_config_value(
            self.__class__.__name__,
            'time_safety_net',
            '3.0'))
        predicted_update_time = predicted_sweep_time(
            self._config['averaging_time'],
            self._config['averaging_cycles'],
            self._config['settling_time'],
            self._config['settling_cycles'],
            self._config['data_points'])
        self._set_sweep_frequencies()
        if self._config['plot'] != 'no':
            if self._config['channel'] != 'ch2':
                self._set_blank_figures(1)
            if self._config['channel'] != 'ch1':
                self._set_blank_figures(2)
            plt.ion()
            #plt.show()
        metadata['MokuLab-predicted-update-time'] = predicted_update_time


    def update(self, update_number):
        """
        Called by PLACE during the experiment, update_number of times.
        """
        framedata = {
            "freq": [],
            "ch1_mag": [],
            "ch2_mag": [],
            "ch1_phase": [],
            "ch2_phase": []}
        if self._config['plot'] != 'no':
            if self._config['channel'] != 'ch2':
                self.ax_[0][0].lines.clear()
                self.ax_[0][1].lines.clear()
            if self._config['channel'] != 'ch1':
                self.ax_[1][0].lines.clear()
                self.ax_[1][1].lines.clear()
            self.lines = (self._create_empty_lines(1)), (self._create_empty_lines(2))
        if self._config['plot'] == 'live':
            for sweep in self.sweeps:
                self._set_up_moku_sweep(sweep)
                framedata = self._get_and_plot_live_data(framedata, sweep)
            data = self._save_data(framedata)
        else:
            for sweep in self.sweeps:
                self._set_up_moku_sweep(sweep)
                framedata = self._get_data(framedata)
            if self._config['data_points'] % 2 != 0:
                framedata = cut_last_point(framedata)
            data = self._save_data(framedata)
        if self._config['plot'] != 'no':
            self._plot_data(1, framedata)
            self._plot_data(2, framedata)
            self._create_wiggles(1, framedata, update_number)
            self._create_wiggles(2, framedata, update_number)
        self._print_statements(update_number)
        if self._config['plot'] != 'no' and self._config['pause']:
            plt.ioff()
            if update_number == self.total_updates - 1:
                plt.show()
            else:
                plt.ginput(n=2, timeout=300, show_clicks='False')
            plt.ion()
        return data

    def plot(self, update_number, data):
        """Return plot data for plotting in the web app.

        :param update_number: The count of the current update. This will start at 0.
        :type update_number: int

        :param data: The data array for this update.
        :type data: numpy.recarray

        :returns: The plot data as a list of dictionaries
        :rtype: [dict]
        """
        #if not self._config['plot']:
        #    return None
        start = self._config['f_start']
        end = self._config['f_end']
        xlabel = 'Frequency (kHz)'
        ylabel = 'Magnitude (dB)'
        title = 'Channel 1 Frequency Spectrum {} - {} kHz'.format(start, end)
        field = '{}-ch1_magnitude_data'.format(self.__class__.__name__)
        xdata, ydata = data[0][field].T
        return [{
            'title': title,
            'xaxis': xlabel,
            'yaxis': ylabel,
            'series': [
                {
                    'name': 'trace',
                    'xdata': xdata,
                    'ydata': ydata,
                },
            ],
        }]


    def cleanup(self, abort=False):
        """
        Called by PLACE at the end of the experimentself.
        Signal to the instrument that the experiment has ended.
        """
        if abort is False and self._config['plot'] != 'no':
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()


    def _set_sweep_frequencies(self):
        """
        Calculates the frequencies that will be sent through the core.
        Splits them into sweeps of allowed length.
        """
        f_start = self._config['f_start']
        f_end = self._config['f_end']
        n_pts = self._config['data_points']
        points, step = np.linspace(f_start, f_end, n_pts, retstep=True)
        if n_pts % 2 != 0:
            points = np.linspace(f_start, f_end + step, n_pts + 1)
        points = points.tolist()
        sweeps = [points[x:x+MAX_P] for x in range(0, len(points), MAX_P)]
        if len(sweeps[-1]) < MIN_P:
            sweeps[-1] = sweeps[-2][-MIN_P:] + sweeps[-1]
            sweeps[-2] = sweeps[-2][:-MIN_P]
        self.sweeps = sweeps


    def _set_blank_figures(self, ch_):
        start = self._config['f_start']
        end = self._config['f_end']
        ch_fig, self.ax_[ch_-1] = plt.subplots(2, 2)
        ch_fig.canvas.set_window_title(self.__class__.__name__ + '-Channel {}'.format(ch_))
        self.ax_[ch_-1] = self.ax_[ch_-1].flatten()
        self.ax_[ch_-1][0].set_xlim((start, end))
        self.ax_[ch_-1][0].set_xlabel('Frequency (kHz)')
        self.ax_[ch_-1][0].set_ylabel('Magnitude (dB)')
        self.ax_[ch_-1][0].set_title('Channel {} Frequency Spectrum {} - {} kHz'.format(ch_, start, end))

        self.ax_[ch_-1][2].set_xlim((-1, self.total_updates))
        self.ax_[ch_-1][2].set_xlabel('Update Number')
        self.ax_[ch_-1][2].set_ylim(start, end)
        self.ax_[ch_-1][2].set_ylabel('Frequency (kHz)')
        self.ax_[ch_-1][2].set_title('Channel {} Frequency Sectra {} - {} kHz'.format(ch_, start, end))

        self.ax_[ch_-1][1].set_xlim((start, end))
        self.ax_[ch_-1][1].set_xlabel('Frequency (kHz)')
        self.ax_[ch_-1][1].set_ylabel('Phase (Cycles)')
        self.ax_[ch_-1][1].set_title('Channel {} Frequency Spectrum {} - {} kHz'.format(ch_, start, end))

        self.ax_[ch_-1][3].set_xlim((-1, self.total_updates))
        self.ax_[ch_-1][3].set_xlabel('Update Number')
        self.ax_[ch_-1][3].set_ylim(start, end)
        self.ax_[ch_-1][3].set_ylabel('Frequency (kHz)')
        self.ax_[ch_-1][3].set_title('Channel {} Frequency Sectra {} - {} kHz'.format(ch_, start, end))


    def _set_up_moku_sweep(self, sweep):
        ip_address = PlaceConfig().get_config_value(self.__class__.__name__, 'ip_address')
        ch1_amp = self._config['ch1_amp']
        ch2_amp = self._config['ch2_amp']
        self.moku = Moku(ip_address)
        self.i = self.moku.deploy_or_connect(BodeAnalyzer)
        try:
            if self._config['plot'] == 'live': #or self._config['data_points'] % 2 != 0:
                self.i.set_xmode('sweep')
            else:
                self.i.set_xmode('fullframe')
            self.i.set_output(1, ch1_amp)
            self.i.set_output(2, ch2_amp)
            self.i.set_frontend(channel=1, ac=True, atten=False, fiftyr=False)
            self.i.set_frontend(channel=2, ac=True, atten=False, fiftyr=False)
        except:
            self.moku.close()
            raise
        self.i.set_sweep(
            sweep[0] * 1000,
            sweep[-1] * 1000,
            len(sweep),
            False,
            self._config['averaging_time'],
            self._config['settling_time'],
            self._config['averaging_cycles'],
            self._config['settling_cycles'])
        self.i.start_sweep(single=self._config['single_sweep'])


    def _get_data(self, framedata):
        frame = self.i.get_data()
        sweepdata = {
            "freq": (np.array(frame.frequency)/1000).tolist(),
            "ch1_mag": frame.ch1.magnitude_dB,
            "ch1_phase": frame.ch1.phase,
            "ch2_mag": frame.ch2.magnitude_dB,
            "ch2_phase": frame.ch2.phase}
        framedata = merge_dictionaries(framedata, sweepdata)
        framedata = replace_none_dictionary(framedata)
        self.moku.close()
        return framedata


    def _get_and_plot_live_data(self, framedata, sweep):
        pst = predicted_sweep_time(
            self._config['averaging_time'],
            self._config['averaging_cycles'],
            self._config['settling_time'],
            self._config['settling_cycles'],
            len(sweep))
        then = calendar.timegm(time.gmtime())
        now = then
        frame = self.i.get_realtime_data()
        while pst*self.time_safety_net > now - then:
            flag = 0
            sweepdata = {
                "freq": (np.array(frame.frequency)/1000).tolist(),
                "ch1_mag": frame.ch1.magnitude_dB,
                "ch1_phase": frame.ch1.phase,
                "ch2_mag": frame.ch2.magnitude_dB,
                "ch2_phase": frame.ch2.phase}
            sweepdata = replace_none_dictionary(sweepdata)
            if sweep == self.sweeps[-1] and self._config['data_points'] % 2 != 0:
                if sweepdata['ch1_mag'][-2] and sweepdata['ch2_mag'][-2] and sweepdata['ch1_phase'][-2] and sweepdata['ch2_phase'][-2] is not np.nan:
                    sweepdata = cut_last_point(sweepdata)
            self._plot_data(1, merge_dictionaries(framedata, sweepdata))
            self._plot_data(2, merge_dictionaries(framedata, sweepdata))
            for key in sweepdata:
                if key != 'freq':
                    if sweepdata[key][-1] is not np.nan:
                        flag = 1
                        break
            if flag == 1:
                break
            now = calendar.timegm(time.gmtime())
            frame = self.i.get_realtime_data()
        framedata = merge_dictionaries(framedata, sweepdata)
        self.moku.close()
        return framedata


    def _create_empty_lines(self, channel):
        other_channel = 3 - channel
        if self._config['channel'] != 'ch{}'.format(other_channel):
            mag_line, = self.ax_[channel-1][0].plot([], '#4a98e8')
            phase_line, = self.ax_[channel-1][1].plot([], '#952222')
            return mag_line, phase_line
        return None, None


    def _plot_data(self, channel, framedata):
        other_channel = 3 - channel
        if self._config['channel'] != 'ch{}'.format(other_channel):
            self.lines[channel-1][0].set_ydata(framedata['ch{}_mag'.format(channel)])
            self.lines[channel-1][0].set_xdata(framedata['freq'])
            self.lines[channel-1][1].set_ydata(framedata['ch{}_phase'.format(channel)])
            self.lines[channel-1][1].set_xdata(framedata['freq'])
            self.ax_[channel-1][0].relim()
            self.ax_[channel-1][0].autoscale_view(scalex = 'False')
            plt.sca(self.ax_[channel-1][0])
            plt.draw()
            self.ax_[channel-1][1].relim()
            self.ax_[channel-1][1].autoscale_view(scalex = 'False')
            plt.sca(self.ax_[channel-1][1])
            plt.draw()
            plt.pause(0.001)


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
                [(linedata['mag'][0], linedata['phase'][0], linedata['mag'][1], linedata['phase'][1])],
                dtype=[(fielddata['mag'][0], shape), (fielddata['phase'][0], shape),
                       (fielddata['mag'][1], shape), (fielddata['phase'][1], shape)])
        return data.copy()


    def _create_wiggles(self, channel, framedata, update_number):
        """
        Plot the data as a wiggle plot.
        Plots using standard matplotlib backend.
        """
        other_channel = 3 - channel
        freq = framedata['freq']
        mag = framedata['ch{}_mag'.format(channel)]
        avg_mag = mag - np.average(mag)
        phase = framedata['ch{}_phase'.format(channel)]
        if self._config['channel'] != 'ch{}'.format(other_channel):
            data_mag = avg_mag / np.amax(np.abs(avg_mag)) + update_number
            self.ax_[channel - 1][2].plot(data_mag, freq, color='black', linewidth=0.5)
            self.ax_[channel - 1][2].fill_betweenx(
                freq,
                data_mag,
                update_number,
                where=[False if np.isnan(x) else x > update_number for x in data_mag],
                color='black')
            plt.sca(self.ax_[channel - 1][2])
            plt.draw()
            data_phase = phase / np.amax(np.abs(phase)) + update_number
            self.ax_[channel - 1][3].plot(data_phase, freq, color='black', linewidth=0.5)
            self.ax_[channel - 1][3].fill_betweenx(
                freq,
                data_phase,
                update_number,
                where=[False if np.isnan(x) else x > update_number for x in data_phase],
                color='black')
            plt.sca(self.ax_[channel - 1][3])
            plt.draw()
            plt.pause(0.001)
            #try:
                #avg_mag = mag - np.average(mag)
            #except TypeError:
                #warn("Detected a 'None' value in the data - attempting to remove...")
                #print(mag)
                #if mag[-1] is None or phase[-1] is None:
                    #freq = freq[:-1]
                    #mag = mag[:-1]
                    #phase = phase[:-1]
                #avg_mag = mag - np.average(mag)
            #self._plot_wiggle(framedata, channel, freq, update_number)
            #self._plot_wiggle(framedata, channel, freq, update_number)


    def _print_statements(self, update_number):
        if update_number == self.total_updates - 2:
            print('Almost there, I have 1 more update to work through.')
            if self._config['pause'] and self._config['plot'] != 'no':
                print('Double-click the figure when you\'re ready to move on to the next update.')
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
                print('I need you to double-click the figure when you\'re ready for me to continue.')
                print('Cheers mate.')


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


def predicted_sweep_time(a_1, a_2, s_1, s_2, pts):
    """
    Empirical equation for sweep time estimates.

    Note: rough estimate, lower freuqencies take longer (such as around 20kHz)
    """
    return max(a_1*pts, (a_2/10000)*(pts/3.75)) + max(s_1*pts, (s_2/10000)*(pts/3.75))


def cut_last_point(d_1):
    """
    Removes last point of final framedata that was added to avoid None for odd points.
    """
    finaldata = {}
    for key in d_1:
        finaldata[key] = d_1[key][:-1]
    return finaldata
