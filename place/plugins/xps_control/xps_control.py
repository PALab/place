"""Stage movement using the XPS-C8 controller"""
import json
from time import sleep
from itertools import count
from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from . import XPS_C8_drivers

SUCCESS = 0

class Stage(Instrument, XPS_C8_drivers.XPS):
    """Basic stage"""

    def __init__(self):
        super(Stage, self).__init__()
        self._group = None          # group name
        self._config = None         # JSON configuration data
        self._socket = None         # communication socket ID
        self._position = None       # position iterator

# PUBLIC METHODS

    def config(self, json_string):
        """setup for a scan.

        :param json_string: JSON-formatted configuration
        :type json_string: str
        """
        self._config = json.loads(json_string)
        self._position = count(self._config['start'], self._config['increment'])
        self._connect_to_server()
        self._check_controller_status()
        self._login()
        self._init_group()
        self._group_home_search()

    def update(self):
        """move the stage"""
        self._move_absolute(next(self._position))

    def cleanup(self):
        """end of scan"""
        pass

# PRIVATE METHODS

    def _connect_to_server(self):
        ip_address = PlaceConfig().get_config_value(__name__, "stage_ip_address")
        port = 5001
        timeout = 3
        self._socket = self.TCP_ConnectToServer(ip_address, port, timeout)
        if self._socket == -1:
            raise RuntimeError(__name__ + ": connection failed")

    def _check_controller_status(self):
        ret = self.ControllerStatusGet(self._socket)
        if ret[0] != SUCCESS:
            raise RuntimeError(__name__ + ": status error: "
                               + self.ErrorStringGet(self._socket, ret))

    def _login(self):
        ret = self.Login(self._socket, "Administrator", "Administrator")
        if ret[0] != SUCCESS:
            raise RuntimeError(__name__ + ": login failed: "
                               + self.ErrorStringGet(self._socket, ret))

    def _init_group(self):
        self.GroupKill(self._socket, self.group)
        ret = self.GroupInitialize(self._socket, self.group)
        if ret[0] != SUCCESS:
            raise RuntimeError(__name__ + ": group initialize failed: "
                               + self.ErrorStringGet(self._socket, ret))

    def _group_home_search(self):
        self.GroupStatusGet(self._socket, self.group)
        ret = self.GroupHomeSearch(self._socket, self.group)
        if ret[0] != SUCCESS:
            raise RuntimeError(__name__ + ": home search failed: "
                               + self.ErrorStringGet(self._socket, ret))

    def _move_absolute(self, position):
        ret = self.GroupMoveAbsolute(self._socket, self.group, [position])
        if ret != SUCCESS:
            raise RuntimeError(__name__ + "move abolute failed: "
                               + self.ErrorStringGet(self._socket, ret))
        sleep(self._config['settle_time'])

class ShortStage(Stage):
    """Short stage"""
    def __init__(self):
        super(ShortStage, self).__init__()
        self._group = 'SHORT_STAGE' # group name

class LongStage(Stage):
    """Short stage"""
    def __init__(self):
        super(LongStage, self).__init__()
        self._group = 'LONG_STAGE' # group name
