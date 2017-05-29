"""Instrument base class for PLACE"""
import asyncio

class Instrument:
    """Generic interface to an instrument."""
    def __init__(self, config):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        # instruments are updated based on priority (lowest first)
        self._config = config
        self.priority = 100

    def config(self, metadata, updates, directory):
        """Configure the instrument.

        Called once at the beginning of a scan. Instruments can expect to
        receive specific data relative to the scan. Note that none of tha
        arguments are optional and will always be provided.

        :param metadata: PLACE maintains metadata for each scan in a dictionary
                         object. During the configuration phase, this
                         dictionary is passed to each instrument through this
                         function so that relevant instrument data can be
                         recorded into it. Instruments should record
                         information that is relevant to the entire scan, but
                         is also specific to the instrument. For example, if an
                         instrument is using one of many filters during this
                         scan, it would be appropriate to record the filter
                         into the scan metadata.
        :type metadata: dict

        :param updates: This value will always be used to inform each
                        instrument of the number of updates (or steps) that
                        will be perfomed during this scan. Instruments should
                        use this value to determine when to perform specific
                        tasks during the scan. For example, some instruments
                        may want to perform a task at the midpoint of a scan
                        and can therefore use this value to determine which
                        update will represent the midpoint.
        :type updates: int

        :param directory: Many instruments need to record their data to disk.
                          This argument specifies where the instrument is free
                          to save data.
        :type directory: str

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def update(self, metadata, update_number, socket=None):
        """Update the instrument for this step of the experiment.

        Called one or more times during a scan. During this method, the
        instrument should record data or configure itself to support the data
        acquisition of this step. For example, oscilloscopes will usually take
        a reading, stages will usually move, vibrometers will focus, etc.

        :param metadata: As in :py:meth: config, this parameter will contain
                         the dictionary of metadata for the scan. However,
                         during the update phase, instruments should record
                         metadata relative to the current step (update) of the
                         scan, rather than data applicable to the entire scan.
                         In fact, any scan data should have already been
                         recorded into the metadata during the configuration
                         phase and will therefore already exist in the
                         dictionary. Additionally, note that the metadata will
                         contain information from instruments with a higher
                         priority than the current instrument becasue thsoe
                         instruments will have already processed their update
                         step for this round. That being said, PLACE will begin
                         each round of instrument updates with new metadata, so
                         data placed into the metadata during one update phase
                         will no persist to the next update phase.
        :type metadata: dict

        :param update_number: This will be the current update number (starting
                              with 1) of the experiment. Instruments could
                              certainly count the number of updates themselves,
                              but this is provided as a convenience.
        :type update_number: int

        :param socket: This is a socket for communicating back to the web
                       interface and is a way of providing feedback to the
                       user, typically in the form of a data plot.
        :type socket: websocket

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def cleanup(self, abort=False):
        """Called at the end of a scan, or if there is an error along the way.

        When this is called, the instrument should stop any activities and
        cleanup resources. This function, like :py:meth update, can return a
        plot, which may be displayed to the user.

        If the abort parameter is set, this indicates that the scan is being
        abandoned, perhaps due to a safety concern, such as a problem with one
        of the instruments. In this case, halting all real world activity
        should be prioritized, and tasks regarding plotting, software resources
        or data integrity can be skipped.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

def send_data_thread(socket, out):
    """A thread to send data back through the websocket

    :param socket: the socket connecting the webapp
    :type socket: websocket

    :param out: the data to send
    :type out: str
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(socket.send(out))
    loop.close()
