"""The PLACE module for the Moku:Lab"""
import calendar
import time
from warnings import warn
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib import cm
from place.plugins.instrument import Instrument
from place.config import PlaceConfig

try:
    from pymoku import Moku
    from pymoku.instruments import BodeAnalyzer
except ImportError:
    pass

MIN_P = 32
MAX_P = 512

def predictedsweeptime(a1, a2, s1, s2, n):
    """
    Empirical equation for sweep time estimateself.

    Note: rough estimate, lower freuqencies take longer (such as around 20kHz)
    """

    return max(a1*n, (a2/10000)*(n/3.75)) + max(s1*n, (s2/10000)*(n/3.75))

class MokuLab(Instrument):
    """The MokuLab class for place"""
    def __init__(self, config):
        """Initialize the MokuLab, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self.total_updates = None
        self.ip_address = None
        #self.cs = None
        #self.my_cm = None
        self.time_safety_net = None
        self.sweeps = None
        self._chx_axes = [{},{}]
        self.m = None
        self.i = None


    def config(self, metadata, total_updates):

        self.total_updates = total_updates

        self.ip_address = PlaceConfig().get_config_value(self.__class__.__name__, 'ip_address')
        #self.cs = PlaceConfig().get_config_value(self.__class__.__name__, 'colour scheme')
        #self.my_cm = getattr(cm,self.cs)
        self.time_safety_net = float(PlaceConfig().get_config_value(self.__class__.__name__, 'time_safety_net','3.0'))

        wholepst = predictedsweeptime(
            self._config['averaging_time'],
            self._config['averaging_cycles'],
            self._config['settling_time'],
            self._config['settling_cycles'],
            self._config['data_points'])

        points = np.linspace(self._config['f_start'],self._config['f_end'],self._config['data_points'])
        points = points.tolist()

        sweeps = [points[x:x+MAX_P] for x in range(0,len(points),MAX_P)]

        if len(sweeps[-1]) < MIN_P:
            sweeps[-1] = sweeps[-2][-MIN_P:] + sweeps[-1]
            sweeps[-2] = sweeps[-2][:-MIN_P]

        self.sweeps = sweeps

        safe_wholepst = wholepst * self.time_safety_net
        #print('Each {} update is predicted to take {:.2f} seconds'.format(
            #self.__class__.__name__, wholepst))
        #print('PLACE {} will wait for {:.2f} seconds'.format(
            #self.__class__.__name__, safe_wholepst))

        metadata['MokuLab-predicted-sweep-time'] = wholepst
        metadata['MokuLab-safe-predicted-sweep-time'] = safe_wholepst

        if self._config['plot']:
            if self._config['channel'] != 'ch2':
                ch1_fig, self._chx_axes[0] = plt.subplots(2, 2)
                ch1_fig.canvas.set_window_title(self.__class__.__name__ + '-Channel 1')

                self._plot_fig((self._chx_axes[0])[0][0],(self._chx_axes[0])[1][0],'Magnitude (dB)',1)

            if self._config['channel'] != 'ch1':
                ch2_fig, (self._chx_axes[1]) = plt.subplots(2, 2)
                ch2_fig.canvas.set_window_title(self.__class__.__name__ + '-Channel 2')

                self._plot_fig((self._chx_axes[1])[0][1],(self._chx_axes[1])[1][1],'Phase (Cycles)',2)

            plt.ion()
            plt.show()

    def update(self, update_number):

        ch1_amp = self._config['ch1_amp']
        ch2_amp = self._config['ch2_amp']

        if self._config['plot']:
            ax00 = (self._chx_axes[0])[0][0]
            ax01 = (self._chx_axes[0])[0][1]

            if self._config['channel'] != 'ch2':
                ch1_mag_line, = ax00.plot([])
                ch1_phase_line, = ax01.plot([])

            if self._config['channel'] != 'ch1':
                ch2_mag_line, = ax00.plot([])
                ch2_phase_line, = ax01.plot([])

        total_freq = []
        total_ch1_mag = []
        total_ch2_mag = []
        total_ch1_phase = []
        total_ch2_phase = []

        for sweep in self.sweeps:
            #print("I'm sweeping through the frequency range {} to {},".format(
                #sweep[0],sweep[-1]))
            #print("using {} data points.".format(len(sweep)))

            # Connect to your Moku by its device name
            # Alternatively, use Moku.get_by_serial('#####') or Moku('192.168.###.###')
            self.m = Moku(self.ip_address)

            # See whether there's already a Bode Analyzer running. If there is, take
            # control of it; if not, deploy a new Bode Analyzer instrument
            self.i = self.m.deploy_or_connect(BodeAnalyzer)

            try:
                # Many PCs struggle to plot magnitude and phase for
                # both channels at the default 10fps, turn it down so
                # it remains smooth, albeit slow. Turn the output to
                # 'sweep' mode so we can see the in-progress sweep (set
                # to 'fullframe' or leave blank if if you only want to
                # get completed traces, e.g. for analysis rather than
                # viewing)
                self.i.set_framerate(5)
                if self._config['plotting_type'] == 'live':
                    self.i.set_xmode('sweep')
                else:
                    self.i.set_xmode('fullframe')


                # Set the output sweep amplitudes
                self.i.set_output(1, ch1_amp)
                self.i.set_output(2, ch2_amp)

                self.i.set_frontend(channel=1, ac=True, atten=False, fiftyr=True)
                self.i.set_frontend(channel=2, ac=True)

            except:
                self.m.close()
                raise

            pst = predictedsweeptime(self._config['averaging_time'],
                                     self._config['averaging_cycles'],
                                     self._config['settling_time'],
                                     self._config['settling_cycles'],
                                     len(sweep))

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

            then = calendar.timegm(time.gmtime())
            now = 0
            frame = self.i.get_realtime_data()
            while now - then < pst*self.time_safety_net:

                curr_ch1_mag = [np.nan if x is None else x for x in frame.ch1.magnitude_dB]
                curr_ch1_phase = [np.nan if x is None else x for x in frame.ch1.phase]

                curr_ch2_mag = [np.nan if x is None else x for x in frame.ch2.magnitude_dB]
                curr_ch2_phase = [np.nan if x is None else x for x in frame.ch2.phase]

                if self._config['plot'] and self._config['plotting_type'] == 'live':
                    if self._config['channel'] != 'ch2':

                        ch1_mag_line.set_ydata(total_ch1_mag + curr_ch1_mag)
                        ch1_mag_line.set_xdata(
                            total_freq + (np.array(frame.frequency)/1000).tolist())

                        ch1_phase_line.set_ydata(total_ch1_phase + curr_ch1_phase)
                        ch1_phase_line.set_xdata(
                            total_freq + (np.array(frame.frequency)/1000).tolist())

                        ax00.set_xlim(self._config['f_start'], self._config['f_end'])
                        ax00.relim()
                        ax00.autoscale_view()

                        ax01.set_xlim(self._config['f_start'], self._config['f_end'])
                        ax01.relim()
                        ax01.autoscale_view()

                        plt.draw()
                        plt.pause(0.001)

                    if self._config['channel'] != 'ch1':

                        ch2_mag_line.set_ydata(total_ch2_mag + curr_ch2_mag)
                        ch2_mag_line.set_xdata(
                            total_freq + (np.array(frame.frequency)/1000).tolist())

                        ch2_phase_line.set_ydata(total_ch2_phase + curr_ch2_phase)
                        ch2_phase_line.set_xdata(
                            total_freq + (np.array(frame.frequency)/1000).tolist())

                        ax00.set_xlim(
                            self._config['f_start'],
                            self._config['f_end'])
                        ax00.relim()
                        ax00.autoscale_view()

                        ax01.set_xlim(
                            self._config['f_start'],
                            self._config['f_end'])
                        ax01.relim()
                        ax01.autoscale_view()

                        plt.draw()
                        plt.pause(0.001)

                if curr_ch1_mag[-1] is not np.nan:
                    break

                now = calendar.timegm(time.gmtime())

                frame = self.i.get_realtime_data()

            total_ch1_mag.extend(curr_ch1_mag)
            total_ch1_phase.extend(curr_ch1_phase)
            total_ch2_mag.extend(frame.ch2.magnitude_dB)
            total_ch2_phase.extend(frame.ch2.phase)
            total_freq.extend((np.array(frame.frequency)/1000).tolist())

            #print('This is the {} sweep data'.format(sweep))
            #print(total_ch1_mag)

            self.m.close()

        x = total_freq
        m1 = total_ch1_mag
        p1 = total_ch1_phase
        m2 = total_ch2_mag
        p2 = total_ch2_phase

        magnitude_dB_ch1 = np.array(
            [[x[i],m1[i]] for i in range(min(len(x), len(m1)))])
        magnitude_dB_ch2 = np.array(
            [[x[i],m2[i]] for i in range(min(len(x), len(m2)))])

        phase_ch1 = np.array(
            [[x[i],p1[i]] for i in range(min(len(x), len(p1)))])
        phase_ch2 = np.array(
            [[x[i],p2[i]] for i in range(min(len(x), len(p2)))])

        magnitude_dB_ch1_field = '{}-magnitude_dB_ch1'.format(self.__class__.__name__)
        phase_ch1_field = '{}-phase_ch1'.format(self.__class__.__name__)

        magnitude_dB_ch2_field = '{}-magnitude_dB_ch2'.format(self.__class__.__name__)
        phase_ch2_field = '{}-phase_ch2'.format(self.__class__.__name__)

        shape = '({},2)float64'.format(self._config['data_points'])

        data = np.array(
            [(magnitude_dB_ch1, phase_ch1, magnitude_dB_ch2, phase_ch2)],
            dtype=[(magnitude_dB_ch1_field, shape), (phase_ch1_field, shape),
                   (magnitude_dB_ch2_field, shape), (phase_ch2_field, shape)])

        framedata = {"frequency_kHz": np.array(total_freq).copy(),
                     "magnitude_dB_ch1": np.array(total_ch1_mag).copy(),
                     "phase_ch1": np.array(total_ch1_phase).copy(),  "magnitude_dB_ch2": np.array(total_ch2_mag).copy(),
                     "phase_ch2": np.array(total_ch2_phase).copy()}

        if self._config['plot']:
            self._wiggle_plot(
                update_number,
                framedata
            )

        if update_number == self.total_updates - 2:
            print('Almost there, I have {} more update to work through.'.format(
                self.total_updates - (update_number + 1)))
            if self._config['pause']:
                print('Go ahead and close the figure would you?')
                print('Cheers mate.')
        elif update_number == self.total_updates - 1:
            print('I\'ve finished the final sweep.')
            if self._config['pause']:
                print('Please close the plot to wrap up your experiment.')
            print('May the odds be ever in your favor.')

        else:
            print('Don\'t celebrate yet,')
            print('I have {} more updates to work through.'.format(
                self.total_updates - (update_number + 1)))
            if self._config['pause']:
                print('I need you to close the figure so I can continue,')
                print('cheers mate.')

        if self._config['plot']:
            if self._config['pause']:
                plt.ioff()
                plt.show() # pause
                plt.ion()
            else:
                plt.draw()
                plt.pause(0.001)

        return data.copy()

    def cleanup(self, abort=False):
        if abort is False and self._config['plot']:
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()

    def _plot_fig(self,curr_plot,wiggle_plot,measured,x):
        """
        Setting up figures and subplots.
        curr_plot: self._chx_axes[0][]
        wiggle_plot: self._chx_axes[1][]
        measured (y label of top plot): 'Magnitude (dB)' or 'Phase (Cycles)'
        x (Channel number): 1 or 2
        """

        f_start = self._config['f_start']
        f_end = self._config['f_end']

        ax0 = curr_plot
        ax1 = wiggle_plot

        ax0.set_xlabel('Frequency (kHz)')
        ax0.set_ylabel(measured)
        ax0.set_title('Channel {} Frequency Spectrum {} - {} kHz'.format(x,f_start, f_end))

        ax1.set_xlim((-1, self.total_updates))
        ax1.set_xlabel('Update Number')
        ax1.set_ylim(f_start, f_end)
        ax1.set_ylabel('Frequency (kHz)')
        ax1.set_title('Channel {} Frequency Sectra {} - {} kHz'.format(x,f_start, f_end))

    def _wiggle_plot(self, number, framedata):
        """Plot the data as a wiggle plot.

        :param number: the update number
        :type number: int

        :param frequency_kH: the frequency to plot along axis
        :type frequency_kH: numpy.array

        :param magnitude_dB: the magnitude to plot
        :type magnitude_dB: numpy.array

        :param phase: the phase to plot
        :type phase: numpy.array

        Plots using standard matplotlib backend.
        """

        frequency_kHz=framedata["frequency_kHz"]
        magnitude_dB_ch1=framedata["magnitude_dB_ch1"]
        phase_ch1=framedata["phase_ch1"]
        magnitude_dB_ch2=framedata["magnitude_dB_ch2"]
        phase_ch2=framedata["phase_ch2"]

        def plot_final_update(_chx_axes, mp):
            """
            Plots subplots when figure only shown at the end of updates.
            _chx_axes: self._chx_axes[][]
            mp: magnitude_dB_chx or phase_chx

            """
            ax = _chx_axes

            ax.plot(frequency_kHz, mp) #color = self.my_cm(number))
            ax.set_xlim(self._config['f_start'], self._config['f_end'])
            ax.relim()
            ax.autoscale_view()

            plt.draw()
            plt.pause(0.001)

        def plot_wiggles(_chx_axes,measurement):
            """
            Plots wiggle plots.
            _chx_axes: self._chx_axes[][]
            measurement: avg_mag_chx or phase_chx
            """
            ax = _chx_axes

            data = measurement / np.amax(np.abs(measurement)) + number
            ax.plot(data, frequency_kHz, color='black', linewidth=0.5)
            ax.fill_betweenx(
                frequency_kHz,
                data,
                number,
                where=[False if np.isnan(x) else x > number for x in data],
                color='black')
            plt.draw()
            plt.pause(0.001)

        if self._config['plotting_type'] == 'update':

            if self._config['channel'] != 'ch2':
                plot_final_update((self._chx_axes[0])[0][0],magnitude_dB_ch1)
                plot_final_update((self._chx_axes[0])[0][1],phase_ch1)

            if self._config['channel'] != 'ch1':
                plot_final_update((self._chx_axes[1])[0][0],magnitude_dB_ch2)
                plot_final_update((self._chx_axes[1])[0][1],phase_ch2)

            if self._config['pause']:
                plt.ioff()
                plt.show() # pause
                plt.ion()
            else:
                plt.draw()
                plt.pause(0.001)

        if self._config['channel'] != 'ch2':
            try:
                avg_mag_ch1 = magnitude_dB_ch1 - np.average(magnitude_dB_ch1)
            except TypeError:
                warn("Detected a 'None' value in the data - attempting to remove...")
                print(magnitude_dB_ch1)
                if magnitude_dB_ch1[-1] is None or phase_ch1[-1] is None:
                    frequency_kHz = frequency_kHz[:-1]
                    magnitude_dB_ch1 = magnitude_dB_ch1[:-1]
                    phase_ch1 = phase_ch1[:-1]
                avg_mag_ch1 = magnitude_dB_ch1 - np.average(magnitude_dB_ch1)

            plot_wiggles((self._chx_axes[0])[1][0],avg_mag_ch1)
            plot_wiggles((self._chx_axes[0])[1][1],phase_ch1)

        if self._config['channel'] != 'ch1':
            try:
                avg_mag_ch2 = magnitude_dB_ch2 - np.average(magnitude_dB_ch2)
            except TypeError:
                warn("Detected a 'None' value in the data - attempting to remove...")
                print(magnitude_dB_ch2)
                if magnitude_dB_ch2[-1] is None or phase_ch2[-1] is None:
                    frequency_kHz = frequency_kHz[:-1]
                    magnitude_dB_ch2 = magnitude_dB_ch2[:-1]
                    phase_ch2 = phase_ch2[:-1]
                avg_mag_ch2 = magnitude_dB_ch2 - np.average(magnitude_dB_ch2)

            plot_wiggles((self._chx_axes[1])[1][0],avg_mag_ch2)
            plot_wiggles((self._chx_axes[1])[1][1],phase_ch2)
