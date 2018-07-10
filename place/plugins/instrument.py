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

        The elm_module_name is used to send progress back to the web
        application. Therefore, your Elm frontend should always include this
        field.

        :param config: configuration data (from JSON)
        :type config: dict
        """
        self._config = config
        self.priority = 100
        self.elm_module_name = ''

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

    def update(self, update_number, progress):
        """Update the instrument for this step of the experiment.

        Called one or more times during an experiment. During this method, the
        instrument should collect data or configure itself to support other
        instruments during this step. For example, oscilloscopes will usually
        take a reading, stages will usually move, vibrometers will focus, etc.

        At the end of the update phase, the instrument may return the data to
        be saved into the data file. Returning data is optional.

        :param update_number: The count of the current update. This will start at 0.
        :type update_number: int

        :param progress: A blank dictionary that is sent to your Elm module
        :type progress: dict

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

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
