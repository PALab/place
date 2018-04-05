import calendar
import time
from place.plugins.instrument import Instrument
from place.config import PlaceConfig

try:
    from pymoku import Moku
    from pymoku.instruments import BodeAnalyzer
except ImportError:
    pass

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

MIN_P = 32
MAX_P = 512

def predictedsweeptime(a1,a2,s1,s2,n):
    return max(a1*n, (a2/10000)*(n/3.75)) + max(s1*n, (s2/10000)*(n/3.75))

class MokuLab(Instrument):

    def config(self, metadata, total_updates):

        self.total_updates = total_updates

        self.name = self.__class__.__name__
        ip_address = PlaceConfig().get_config_value(self.name, 'ip_address')
        self.cs = PlaceConfig().get_config_value(self.name, 'colour scheme')
        self.my_cm = getattr(cm,self.cs)
        self.time_safety_net = float(PlaceConfig().get_config_value(self.name, 'time_safety_net'))

        f_start = self._config['f_start']
        f_end = self._config['f_end']
        data_points = self._config['data_points']
        ch1_amp = self._config['ch1_amp']
        ch2_amp = self._config['ch2_amp']
        averaging_time = self._config['averaging_time']
        settling_time = self._config['settling_time']
        averaging_cycles = self._config['averaging_cycles']
        settling_cycles = self._config['settling_cycles']

        wholepst = predictedsweeptime(averaging_time,
             averaging_cycles,
             settling_time,
             settling_cycles,
             data_points)

        points, step = np.linspace(f_start,f_end,data_points,retstep=True)
        points = points.tolist()

        sweeps = [points[x:x+MAX_P] for x in range(0,len(points),MAX_P)]

        if len(sweeps[-1]) < MIN_P:
            sweeps[-1] = sweeps[-2][-MIN_P:] + sweeps[-1]
            sweeps[-2] = sweeps[-2][:-MIN_P]

        self.sweeps = sweeps

        self.safe_wholepst = wholepst * self.time_safety_net
        print('Each {} update is predicted to take {:.2f} seconds'.format(
            self.__class__.__name__, wholepst))
        print('PLACE {} will wait for {:.2f} seconds'.format(
            self.__class__.__name__, self.safe_wholepst))

        metadata['MokuLab-predicted-sweep-time'] = wholepst
        metadata['MokuLab-safe-predicted-sweep-time'] = self.safe_wholepst

        # Connect to your Moku by its device name
        # Alternatively, use Moku.get_by_serial('#####') or Moku('192.168.###.###')
        self.m = Moku(ip_address)

        # See whether there's already a Bode Analyzer running. If there is, take
        # control of it; if not, deploy a new Bode Analyzer instrument
        self.i = self.m.deploy_or_connect(BodeAnalyzer)

        try:
            # Many PCs struggle to plot magnitude and phase for
            # both channels at the default 10fps, turn it down so
            # it remains smooth, albeit slow. Turn the output to
            # 'sweep' mode so we can see the in-progress sweep (set
            # to 'full_frame' or leave blank if if you only want to
            # get completed traces, e.g. for analysis rather than
            # viewing)
            self.i.set_framerate(5)
            self.i.set_xmode('sweep')

            # Set the output sweep amplitudes
            self.i.set_output(1, ch1_amp)
            self.i.set_output(2, ch2_amp)

            self.i.set_frontend(channel=1, ac=True, atten=False, fiftyr=True)
            self.i.set_frontend(channel=2, ac=True)

        except:
            self.m.close()
            raise

        if self._config['plot']:
            if self._config['channel'] != 'ch2':
                plt.figure(self.name + '-Channel 1')
                plt.clf()
            if self._config['channel'] != 'ch1':
                plt.figure(self.name + '-Channel 2')
                plt.clf()
            plt.ion()

    def update(self, update_number):
        if self._config['plot']:
            if self._config['channel'] != 'ch2':
                plt.figure(self.name + '-Channel 1')

                plt.subplot(221)
                axes = plt.gca()
                ch1_mag_line, = plt.plot([])
                axes.set_xlabel('Frequency (kHz)')
                axes.set_ylabel('Magnitude (dB)')
                axes.set_title('Channel 1 Frequency Spectrum {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))

                plt.subplot(222)
                axes = plt.gca()
                ch1_phase_line, = plt.plot([])
                axes.set_xlabel('Frequency (kHz)')
                axes.set_ylabel('Phase (Cycles)')
                axes.set_title('Channel 1 Phase Spectrum {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))

            if self._config['channel'] != 'ch1':
                plt.figure(self.name + '-Channel 2')

                plt.subplot(221)
                axes = plt.gca()
                ch2_mag_line, = plt.plot([])
                axes.set_xlabel('Frequency (kHz)')
                axes.set_ylabel('Magnitude (dB)')
                axes.set_title('Channel 2 Frequency Spectrum {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))

                plt.subplot(222)
                axes = plt.gca()
                ch2_phase_line, = plt.plot([])
                axes.set_xlabel('Frequency (kHz)')
                axes.set_ylabel('Phase (Cycles)')
                axes.set_title('Channel 2 Phase Spectrum {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))

        total_freq = []
        total_ch1_mag = []
        total_ch2_mag = []
        total_ch1_phase = []
        total_ch2_phase = []

        for sweep in self.sweeps:
            print("I'm sweeping through the frequency range {} to {},".format(sweep[0],sweep[-1]))
            print("using {} data points.".format(len(sweep)))

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
            while now - then < pst*self.time_safety_net:
                frame = self.i.get_realtime_data()

                now = calendar.timegm(time.gmtime())

                if self._config['plot'] and self._config['plotting_type'] == 'live':
                    if self._config['channel'] != 'ch2':
                        plt.figure(self.name + '-Channel 1')
                        ch1_mag_line.set_ydata(total_ch1_mag + frame.ch1.magnitude_dB)
                        ch1_mag_line.set_xdata(total_freq + (np.array(frame.frequency)/1000).tolist())
                        ch1_phase_line.set_ydata(total_ch1_phase + frame.ch1.phase)
                        ch1_phase_line.set_xdata(total_freq + (np.array(frame.frequency)/1000).tolist())

                        plt.subplot(221)
                        axes = plt.gca()
                        #axes.clear()
                        #axes.plot(total_freq + (np.array(frame.frequency)/1000).tolist(),total_ch1_mag + frame.ch1.magnitude_dB, color = self.my_cm(update_number))
                        axes.set_xlim(
                            self._config['f_start'],
                            self._config['f_end'])
                        axes.relim()
                        axes.autoscale_view()

                        plt.subplot(222)
                        axes = plt.gca()
                        axes.set_xlim(
                            self._config['f_start'],
                            self._config['f_end'])
                        axes.relim()
                        axes.autoscale_view()
                        plt.pause(0.001)

                    if self._config['channel'] != 'ch1':
                        plt.figure(self.name + '-Channel 2')
                        ch2_mag_line.set_ydata(total_ch2_mag + frame.ch2.magnitude_dB)
                        ch2_mag_line.set_xdata(total_freq + (np.array(frame.frequency)/1000).tolist())
                        ch2_phase_line.set_ydata(total_ch2_phase + frame.ch2.phase)
                        ch2_phase_line.set_xdata(total_freq + (np.array(frame.frequency)/1000).tolist())

                        plt.subplot(221)
                        axes = plt.gca()
                        axes.set_xlim(
                            self._config['f_start'],
                            self._config['f_end'])
                        axes.relim()
                        axes.autoscale_view()

                        plt.subplot(222)
                        axes = plt.gca()
                        axes.set_xlim(
                            self._config['f_start'],
                            self._config['f_end'])
                        axes.relim()
                        axes.autoscale_view()
                        plt.pause(0.001)

            total_ch1_mag.extend(frame.ch1.magnitude_dB)
            total_ch1_phase.extend(frame.ch1.phase)
            total_ch2_mag.extend(frame.ch2.magnitude_dB)
            total_ch2_phase.extend(frame.ch2.phase)
            total_freq.extend((np.array(frame.frequency)/1000).tolist())


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



        if self._config['plot']:
            self._wiggle_plot(
                update_number,
                np.array(total_freq),
                np.array(total_ch1_mag),
                np.array(total_ch1_phase),
                np.array(total_ch2_mag),
                np.array(total_ch2_phase)
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

        if self._config['pause']:
            plt.ioff()
            plt.show() # pause
            plt.ion()
        else:
            plt.pause(0.001)

        return data.copy()

    def cleanup(self, abort=False):
        if abort is False and self._config['plot']:
            if self._config['channel'] != 'ch2':
                plt.figure(self.name + '-Channel 1')
            else:
                plt.figure(self.name + '-Channel 2')
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()
        self.m.close()

    def _wiggle_plot(self, number, frequency_kHz, magnitude_dB_ch1, phase_ch1, magnitude_dB_ch2, phase_ch2):
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
        if self._config['plotting_type'] == 'update':
            if self._config['channel'] != 'ch2':
                plt.figure(self.name + '-Channel 1')

                plt.subplot(221)
                axes = plt.gca()
                axes.plot(frequency_kHz, magnitude_dB_ch1, color = self.my_cm(number))
                axes.set_xlim(
                    self._config['f_start'],
                    self._config['f_end'])
                axes.relim()
                axes.autoscale_view()

                plt.subplot(222)
                axes = plt.gca()
                axes.plot(frequency_kHz, phase_ch1)
                axes.set_xlim(
                    self._config['f_start'],
                    self._config['f_end'])
                axes.relim()
                axes.autoscale_view()
                plt.pause(0.001)

            if self._config['channel'] != 'ch1':
                plt.figure(self.name + '-Channel 2')

                plt.subplot(221)
                axes = plt.gca()
                axes.plot(frequency_kHz, magnitude_dB_ch2)
                axes.set_xlim(
                    self._config['f_start'],
                    self._config['f_end'])
                axes.relim()
                axes.autoscale_view()

                plt.subplot(222)
                axes = plt.gca()
                axes.plot(frequency_kHz, phase_ch2)
                axes.set_xlim(
                    self._config['f_start'],
                    self._config['f_end'])
                axes.relim()
                axes.autoscale_view()
                plt.pause(0.001)

            if self._config['pause']:
                plt.ioff()
                plt.show() # pause
                plt.ion()
            else:
                plt.pause(0.001)

        if self._config['channel'] != 'ch2':
            plt.figure(self.name + '-Channel 1')

            plt.subplot(223)
            axes = plt.gca()
            avg_mag_ch1 = magnitude_dB_ch1 - np.average(magnitude_dB_ch1)
            data_ch1 = avg_mag_ch1 / np.amax(np.abs(avg_mag_ch1)) + number
            axes.plot(data_ch1, frequency_kHz, color='black', linewidth=0.5)
            axes.fill_betweenx(
                frequency_kHz,
                data_ch1,
                number,
                where=data_ch1 > number,
                color='black')
            plt.xlim((-1, self.total_updates))
            plt.xlabel('Update Number')
            plt.ylim(self._config['f_start'], self._config['f_end'])
            plt.ylabel('Frequency (kHz)')
            plt.title('Channel 1 Frequency Sectra {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))
            plt.pause(0.001)

            plt.subplot(224)
            axes = plt.gca()
            data_ch1 = phase_ch1 / np.amax(np.abs(phase_ch1)) + number
            axes.plot(data_ch1, frequency_kHz, color='black', linewidth=0.5)
            axes.fill_betweenx(
                frequency_kHz,
                data_ch1,
                number,
                where=data_ch1 > number,
                color='black')
            plt.xlim((-1, self.total_updates))
            plt.xlabel('Update Number')
            plt.ylim(self._config['f_start'], self._config['f_end'])
            plt.ylabel('Frequency (kHz)')
            plt.title('Channel 1 Phase Spectra {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))
            plt.pause(0.001)

        if self._config['channel'] != 'ch1':
            plt.figure(self.name + '-Channel 2')

            plt.subplot(223)
            axes = plt.gca()
            avg_mag_ch2 = magnitude_dB_ch2 - np.average(magnitude_dB_ch2)
            data_ch2 = avg_mag_ch2 / np.amax(np.abs(avg_mag_ch2)) + number
            axes.plot(data_ch2, frequency_kHz, color='black', linewidth=0.5)
            axes.fill_betweenx(
                frequency_kHz,
                data_ch2,
                number,
                where=data_ch2 > number,
                color='black')
            plt.xlim((-1, self.total_updates))
            plt.xlabel('Update Number')
            plt.ylim(self._config['f_start'], self._config['f_end'])
            plt.ylabel('Frequency (kHz)')
            plt.title('Channel 2 Frequency Spectra {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))
            plt.pause(0.001)

            plt.subplot(224)
            axes = plt.gca()
            data_ch2 = phase_ch2 / np.amax(np.abs(phase_ch2)) + number
            axes.plot(data_ch2, frequency_kHz, color='black', linewidth=0.5)
            axes.fill_betweenx(
                frequency_kHz,
                data_ch2,
                number,
                where=data_ch2 > number,
                color='black')
            plt.xlim((-1, self.total_updates))
            plt.xlabel('Update Number')
            plt.ylim(self._config['f_start'], self._config['f_end'])
            plt.ylabel('Frequency (kHz)')
            plt.title('Channel 2 Phase Spectra {} - {} kHz'.format(self._config['f_start'],self._config['f_end']))
            plt.pause(0.001)
