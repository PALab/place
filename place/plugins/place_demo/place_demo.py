"""Demo instrument: a counter

This is meant as both a test and a working demo for PLACE. It can generate
plots of "dummy data", similar to the data produced by the AlazarTech module.
It is great for showing how PLACE operates without setting up any hardware.
"""
from time import sleep
import numpy as np
from place.plots import DATA_POINT_LIMIT
from place.plugins.instrument import Instrument


class PlaceDemo(Instrument):
    """Demo instrument.

    The original idea for this device was to be a programming demo for the most
    basic device conceivable -- a unit counter. However, it soon became
    apparent that this class was useful as a software test of the PLACE system
    and it is now used to test: configuration importing, data collection,
    plotting, and other subsystems in PLACE. It can also be used as a quick way
    to verify that a PLACE installation has been successful.

    ``PlaceDemo`` requires sleep time for each phase, as well as
    ``number_of_points``, and ``plot`` values. Simple metadata is recorded to
    verify the metadata code.
    """

    def __init__(self, config, plotter):
        """Initialize the counter, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict

        :param plotter: a plotting object to return plots to the web interface
        :type plotter: plots.PlacePlotter
        """
        Instrument.__init__(self, config, plotter)
        self._count = None
        self._number = None
        self._samples = None
        self._updates = None

    def config(self, metadata, total_updates):
        """Calculate basic values and record basic metadata.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        self._count = 0
        self._samples = self._config['number_of_points']
        self._updates = total_updates
        metadata['{}_samples'.format(self.__class__.__name__)] = self._samples
        sleep(self._config['config_sleep_time'])

    def update(self, update_number, progress):
        """Increment the counter.

        Additionally, this will generate a random trace, plot the trace, and
        return the trace in standard PLACE format. A sleep is performed between
        updates based on the user-provided ``sleep_time`` configuration.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :returns: the current count (1-indexed) and a dummy trace in a numpy
                  record array
        :rtype: numpy.recarray
        """
        self._count += 1
        self._number = update_number
        samples = np.array(
            [np.exp(-i) * np.sin(2*np.pi*i) for i in np.linspace(0, 4, self._samples)])
        noise1 = np.random.normal(  # pylint: disable=no-member
            0, 0.15, self._samples)
        noise2 = np.random.normal(  # pylint: disable=no-member
            0, 0.10, self._samples)
        noise3 = np.random.normal(  # pylint: disable=no-member
            0, 0.05, self._samples)
        trace1 = (samples + noise1 + 1) * 2**13
        trace2 = (samples + noise2 + 1) * 2**13
        trace3 = (samples + noise3 + 1) * 2**13
        count_field = '{}-count'.format(self.__class__.__name__)
        trace_field = '{}-trace'.format(self.__class__.__name__)
        data = np.array(
            [(self._count, trace1)],
            dtype=[(count_field, 'int16'), (trace_field, 'float64', self._samples)])
        sleep(self._config['update_sleep_time'])

        # plotting one series
        self.plotter.view1(
            'Figure 1: Plot one series',
            trace1
        )

        # plotting two series
        self.plotter.view2(
            'Figure 2: Plot two series',
            trace1,
            trace2
        )

        # plotting three series
        self.plotter.view3(
            'Figure 3: Plot three series',
            trace1,
            trace2,
            trace3
        )

        # plotting many series
        self.plotter.view(
            'Figure 4: Plot many/custom series', [
                self.plotter.dash(
                    trace1,
                    color='green',
                    shape='none',
                    label='Noisy data'
                ),
                self.plotter.line(
                    trace3,
                    color='purple',
                    shape='none',
                    label='Better data'
                )
            ]
        )

        # example of what happens if your number of points exceeds the maximum
        max_points = DATA_POINT_LIMIT
        many_samples = np.array(
            [np.exp(-i) * np.sin(2*np.pi*i) for i in np.linspace(0, 4, max_points * 2)])
        much_noise = np.random.normal(  # pylint: disable=no-member
            0, 0.05, max_points * 2)
        long_trace = (many_samples + much_noise + 1) * 2**13
        self.plotter.view1(
            'Figure 5: Plot too many points',
            long_trace
        )

        # return data to be saved in `data.npy` file
        return data

    def cleanup(self, abort=False):
        """Stop the demo and cleanup.

        :param abort: ``True`` if the experiement is being aborted, in which
                      case plotting should not occur
        :type abort: bool
        """
        sleep(self._config['cleanup_sleep_time'])
