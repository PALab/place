"""Demo instrument: a counter

This is meant as both a test and a working demo for PLACE. It can generate
plots of "dummy data", similar to the data produced by the AlazarTech module.
It is great for showing how PLACE operates without setting up any hardware.
"""
from time import sleep
import matplotlib.pyplot as plt
import numpy as np
from place.plugins.instrument import Instrument

class Counter(Instrument):
    """Demo instrument.

    The original idea for this device was to be a programming demo for the most
    basic device conceivable -- a unit counter. However, it soon became
    apparent that this class was useful as a software test of the PLACE system
    and it is now used to test: configuration importing, data collection,
    plotting, and other subsystems in PLACE. It can also be used as a quick way
    to verify that a PLACE installation has been successful.

    A demo can be executed on the command line with the following code::

        place_scan '
        {
            "updates": 10,
            "directory": "/tmp/place_tmp",
            "comments": "",
            "modules": [
                {
                    "module_name": "counter",
                    "class_name": "Counter",
                    "priority": 10,
                    "config": {
                        "sleep_time": 1,
                        "plot": true
                    }
                }
            ]
        }'

    ``Counter`` requires only ``sleep_time`` and ``plot`` values. Simple
    metadata is recorded to verify the metadata code.
    """
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
        """Calculate basic values and record basic metadata.

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
            plt.figure(self.__class__.__name__)
            plt.clf()
            plt.ion()

    def update(self, update_number):
        """Increment the counter.

        Additionally, this will generate a random trace, plot the trace, and
        return the trace in standard PLACE format. A sleep is performed between
        updates based on the user-provided ``sleep_time`` configuration.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :returns: the current count (1-indexed) and a dummy trace
        :rtype: dtype=[('count', 'int16'), ('trace', 'float64', self._samples)])
        """
        self._count += 1
        self._number = update_number
        samples = np.array(
            [np.exp(-i) * np.sin(2*np.pi*i) for i in np.arange(self._samples) * 0.05])
        noise = np.random.normal(0, 0.15, self._samples)
        trace = (samples + noise + 1) * 2**13
        data = np.array(
            [(self._count, trace)],
            dtype=[('count', 'int16'), ('trace', 'float64', self._samples)])
        if self._config['plot']:
            plt.figure(self.__class__.__name__)
            self._wiggle_plot(trace)
        sleep(self._config['sleep_time'])
        return data

    def cleanup(self, abort=False):
        """Stop the counter and cleanup.

        Refreshes the final plot and leave it up until the user closes it.

        :param abort: ``True`` if the experiement is being aborted, in which
                      case plotting should not occur
        :type abort: bool
        """
        if abort is False and self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()

    def _wiggle_plot(self, trace):
        """Plot the data as a wiggle plot.

        :param trace: the data to plot
        :type trace: numpy.array

        Plots using standard matplotlib backend.
        """
        plt.subplot(211)
        plt.cla()
        plt.plot(trace)
        plt.xlim((0, self._samples))
        plt.xlabel('Sample Number')
        plt.ylim((0, 2**14))
        plt.title('Update {}'.format(self._number))
        plt.pause(0.05)

        plt.subplot(212)
        axes = plt.gca()
        times = np.arange(0, self._samples)
        data = trace / 2**13 + self._number - 1
        axes.plot(data, times, color='black', linewidth=0.5)
        axes.fill_betweenx(
            times,
            data,
            self._number,
            where=data > self._number,
            color='black')
        plt.xlim((-1, self._updates))
        plt.xlabel('Update Number')
        plt.ylim((self._samples, 0))
        plt.ylabel('Sample Number')
        plt.pause(0.05)
