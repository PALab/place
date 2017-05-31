"""Instrument base class for PLACE"""
import asyncio

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

        Called once at the beginning of a scan. Instruments can expect to
        receive specific data relative to the scan.

        :param metadata: PLACE maintains metadata for each scan in a dictionary
                         object. During the configuration phase, this
                         dictionary is passed to each instrument through this
                         function so that relevant instrument data can be
                         recorded into it. Instruments should record
                         information that is relevant to the entire scan, but
                         is also specific to the instrument. For example, if an
                         instrument is using one of many filters during this
                         scan, it would be appropriate to record the name of
                         the filter into the scan metadata. PLACE will write
                         all the metadata collected from the instruments into a
                         single file for each scan.
        :type metadata: dict

        :param total_updates: This value will always be used to inform each
                              instrument of the number of updates (or steps)
                              that will be perfomed during this scan.
                              Instruments should use this value to determine
                              when to perform specific tasks during the scan.
                              For example, some instruments may want to perform
                              a task at the midpoint of a scan and can
                              therefore use this value to determine which
                              update will represent the midpoint.
        :type total_updates: int

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    def update(self, update_number, socket=None):
        """Update the instrument for this step of the experiment.

        Called one or more times during a scan. During this method, the
        instrument should collect data or configure itself to support other
        instruments during this step. For example, oscilloscopes will usually
        take a reading, stages will usually move, vibrometers will focus, etc.

        :param update_number: The count of the current update. This will start at 0.
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
        cleanup resources.

        Any measurements taken by instruments should be put into a NumPy record
        array with shape N x M (where N is the number of updates) and returned
        to PLACE.

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
