"""Mirror movement using the New Focus picomotors."""
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

        self._controller = PMot()
        self._controller.connect(self._ip_address, self._port)

        # set to high velocity
        self._controller.set_va(PX, 1700)
        self._controller.set_va(PY, 1700)
        # set current position to zero
        self._controller.set_dh(PX, 0)
        self._controller.set_dh(PY, 0)
        #set units to encoder counts for closed-loop
        self._controller.set_sn(PX, 1)
        self._controller.set_sn(PY, 1)
        # set following error threshold
        self._controller.set_fe(PX, 200)
        self._controller.set_fe(PY, 200)
        # set closed-loop update interval to 0.1
        self._controller.set_cl(PX, 0.1)
        self._controller.set_cl(PY, 0.1)
        # enable closed-loop setting
        self._controller.set_mm(PX, 1)
        self._controller.set_mm(PY, 1)
        # save settings to non-volatile memory
        self._controller.set_sm()

    def update(self, update_number, plot_socket=None):
        """Move the mirror.

        :param update_number: the current update count
        :type update_number: int

        :param plot_socket: connection to the webapp plot frame
        :type plot_socket: websocket
        """

    def cleanup(self, abort=False):
        """Stop picomotor and end scan.

        :param abort: indicates the scan has been stopped rather than having
                      finished normally
        :type abort: bool
        """
        pass
