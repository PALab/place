"""Demo instrument: a counter

This is meant as both a test and a working demo for PLACE.
"""
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
from place.plugins.instrument import Instrument

class Counter(Instrument):
    """A unit counter"""
    def __init__(self, config):
        """Initialize the counter, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self._count = None
        self._number = None
        self._samples = None
        self._updates = None
        self._directory = None

    def config(self, metadata, total_updates):
        """Configure the counter

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        self._count = 0
        self._samples = 2**7
        self._updates = total_updates
        metadata['counter_samples'] = self._samples
        metadata['counter_sleep_time'] = self._config['sleep_time']
        if self._config['plot']:
            plt.close('all')
            plt.ion()

    def update(self, update_number, socket=None):
        """Update the counter

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param socket: connection to the webapp plot frame (not used)
        :type socket: websocket

        :returns: the data records for this instrument
        :rtype: numpy.array
        """
        self._count += 1
        self._number = update_number
        samples = np.array(
            [np.exp(-i) * np.sin(2*np.pi*i) for i in np.arange(self._samples) * 0.05])
        noise = np.random.normal(0, 0.2, self._samples)
        trace = samples + noise
        data = np.array(
            [(self._count, trace)],
            dtype=[('count', 'int16'), ('trace', 'float64', self._samples)])
        if self._config['plot']:
            self._wiggle_plot(trace)
        sleep(self._config['sleep_time'])
        return data

    def cleanup(self, abort=False):
        """Stop the counter and return data.

        :param abort: flag indicating if the scan is being aborted
        :type abort: bool
        """
        if abort is False and self._config['plot']:
            plt.ioff()
            plt.show()

    def _wiggle_plot(self, trace):
        """Plot the data as a wiggle plot.

        :param trace: the data to plot
        :type trace: numpy.array

        Plots to socket using mpld3, if available, otherwise uses standard
        matplotlib backend.
        """
        plt.subplot(211)
        plt.cla()
        plt.plot(trace)
        plt.xlim((0, self._samples))
        plt.xlabel('Sample Number')
        plt.ylim((-1, 1))
        plt.title('Update {}'.format(self._number))
        plt.pause(0.05)

        plt.subplot(212)
        axes = plt.gca()
        times = np.arange(0, self._samples)
        trace += self._count - 1
        axes.fill_betweenx(
            times,
            trace,
            self._count - 1,
            where=trace > self._count - 1,
            color='black')
        plt.xlim((0, self._updates))
        plt.xlabel('Update Number')
        plt.ylim((self._samples, 0))
        plt.ylabel('Sample Number')
        plt.pause(0.05)
