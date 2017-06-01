"""Mirror movement using the New Focus picomotors."""

from socket import socket
from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from .pmot import PMot

PX = 2
PY = 1

class Picomotor(Instrument):
    """The picomotor class."""

    def __init__(self, config):
        """Initialize the controller, without configuring.

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self._ip_address = None
        self._port = None
        self._controller = None

    def config(self, metadata, total_updates):
        """Configure the picomotors for a scan.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this scan
        :type total_updates: int
        """
        self._ip_address = PlaceConfig().get_config_value(
            __name__,
            "picomotor_ip_address"
            )
        self._port = PlaceConfig().get_config_value(
            __name__,
            "picomotor_port"
            )

        self._controller = PMot(self._ip_address, self._port)

        # set to high velocity
        pmot.set_VA(PX, 1700)
        pmot.set_VA(PY, 1700)
        # set current position to zero
        pmot.set_DH(PX, 0)
        pmot.set_DH(PY, 0)
        #set units to encoder counts for closed-loop
        pmot.set_SN(PX, 1)
        pmot.set_SN(PY, 1)
        # set following error threshold
        pmot.set_FE(PX, 200)
        pmot.set_FE(PY, 200)
        # set closed-loop update interval to 0.1
        pmot.set_CL(PX, 0.1)
        pmot.set_CL(PY, 0.1)
        # enable closed-loop setting
        pmot.set_MM(PX, 1)
        pmot.set_MM(PY, 1)
        # save settings to non-volatile memory
        pmot.set_SM()

    def update(self, metadata, update_number, socket=None):
        """Move the stage.

        The class uses an iterator to keep track of the position of the stage.
        So, all we need to do is call next() on it, and it will return the next
        position.

        We will then move the stage and ask the controller to return to us the
        actual position the stage settled at. We will save this position into
        the header.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param update_number: the current update count
        :type update_number: int

        :param socket: connection to the webapp plot frame
        :type socket: websocket
        """
        # Move the stage to the next position.
        self._move_stage()

        # Use this position key to reference our position in the metadata
        # header. Note that this wouldn't work if there were multiple stages
        # with the same name.
        position_key = self._group + '_position'

        # Get the current position and save it in the header.
        metadata[position_key] = self._get_position()

    def cleanup(self, abort=False):
        """Stop picomotor and end scan.

        :param abort: indicates the scan has been stopped rather than having
                      finished normally
        :type abort: bool
        """
        self._close_controller_connection()

# PRIVATE METHODS

    def _connect_controller(self):
        """Establish connection with picomotor controller.

        :raises IOError: if there is no response from the server
        """
        self._controller = socket()
        self._controller.connect(self._ip_address, self._port)
        for _ in range(300):
            data = self._controller.recv(2048)
            if data:
                break
        else:
            raise IOError('no response from picomotor server')
