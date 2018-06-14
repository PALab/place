"""Instrument base class for PLACE"""
# pylint: disable=no-self-use, unused-argument
class Instrument:
    """Generic interface to an instrument.

    Any instrument that works with PLACE should use this as a base class. In
    face, PLACE will not execute instruments that do not use this as a base
    class.
    """
    def __init__(self, config):
        """Constructor

        Saves the config data and sets a default priority. Subclasses can
        certainly repeat this or override it, but it is done here anyway.

        Instrument priority is used by PLACE to determine the order of updates.
        Lower values of priorty are updated before higher ones. If this seems
        backwards to you, use the phrase "this is my number one priority" to
        help you remember.

        :param config: configuration data (from JSON)
        :type config: dict
        """
        self._config = config
        self.priority = 100

    def config(self, metadata, total_updates):
        """Configure the instrument.

        Called once at the beginning of an experiment. Instruments can expect
        to receive specific data relative to the experiment.

        :param metadata: PLACE maintains metadata for each experiment in a
                         dictionary object. During the configuration phase,
                         this dictionary is passed to each instrument through
                         this function so that relevant instrument data can be
                         recorded into it. Instruments should record
                         information that is relevant to the entire experiment,
                         but is also specific to the instrument. For example,
                         if an instrument is using one of many filters during
                         this experiment, it would be appropriate to record the
                         name of the filter into the experiment metadata. PLACE
                         will write all the metadata collected from the
                         instruments into a single file for each experiment.
        :type metadata: dict

        :param total_updates: This value will always be used to inform each
                              instrument of the number of updates (or steps)
                              that will be perfomed during this experiment.
                              Instruments should use this value to determine
                              when to perform specific tasks during the
                              experiment.  For example, some instruments may
                              want to perform a task at the midpoint of an
                              experiment and can therefore use this value to
                              determine which update will represent the
                              midpoint.
        :type total_updates: int

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def update(self, update_number):
        """Update the instrument for this step of the experiment.

        Called one or more times during an experiment. During this method, the
        instrument should collect data or configure itself to support other
        instruments during this step. For example, oscilloscopes will usually
        take a reading, stages will usually move, vibrometers will focus, etc.

        At the end of the update phase, the instrument may return two things.
        The first return item is the data to be saved into the data file and
        the second return item is a list of data points to be live plotted in
        the web interface. Both return values are optional.

        :param update_number: The count of the current update. This will start at 0.
        :type update_number: int

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def plot(self, update_number, data):
        """Return plot data for display in the web app.

        This method is called after each update phase. During this phase the
        instrument should generate and return plot data for use in the web app.
        These plots are displayed in the web app while the experiment is
        running.

        Specifically, instruments can return multiple plots with multiple
        series on each plot.

        Because this data will be sent over the network, it will be sent as a
        JSON string. Also because this data will be sent over the network, it
        is important to downsample large plots to a reasonable size.

        When implemented, instruments should return a Python list of dictionary
        objects with specific fields. Here is an example::

            my_plots = [{
                'title': 'My great experiment',
                'xaxis': 'time (or something)',
                'yaxis': 'level (I think)',
                'series': [{'name': 'old results',
                            'xdata': numpy.array([1, 2, 3, 4, 5],
                            'ydata': numpy.array([0, 0, 1, 0, 1]},
                           {'name': 'newer (better) results',
                            'xdata': numpy.array([1, 2, 3, 4, 5],
                            'ydata': numpy.array([1, 3, 2, 2, 4]},
                          ],
            },
                # other plots #
            ]

        As can be seen, all the fields are strings except for the xdata and
        ydata fields. These should always be NumPy arrays. PLACE will convert
        your arrays to a list of float values before sending out the JSON.

        This method is optional and will return None if not implemented.

        :param update_number: The count of the current update. This will start at 0.
        :type update_number: int

        :param data: The data array for this update.
        :type data: numpy.ndarray
        """
        return None

    def cleanup(self, abort=False):
        """Called at the end of an experiment, or if there is an error along the way.

        When this is called, the instrument should stop any activities and
        cleanup resources.

        If the abort parameter is set, this indicates that the experiment is
        being abandoned, perhaps due to a safety concern, such as a problem
        with one of the instruments. In this case, halting all real world
        activity should be prioritized, and tasks regarding plotting, software
        resources or data integrity can be skipped.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
