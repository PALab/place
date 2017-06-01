"""Stage movement using the XPS-C8 controller.

This file contains additional commenting and documentation to assist future
development of PLACE plugins.
"""
# import sleep() to pause breifly after
# stage movement
from time import sleep

# import count() to create an iterator
# for stage movement
from itertools import count

# we need NumPy to store data for our instrument
import numpy as np

# all PLACE plugins should be a subclass of
# Instrument, so import the Instrument class
from place.plugins.instrument import Instrument

# import PlaceConfig to access the PLACE
# config file: ~/.place.cfg
from place.config import PlaceConfig

# Finally, import the driver for this instrument.
# This is the only relative import used.
from . import XPS_C8_drivers

# Many of our driver calls return 0 for success.
# This constant with an underscore improves readability
# in the code, but hints that Python should not
# export it to other modules.
_SUCCESS = 0



### THE STAGE CLASS ###

class Stage(Instrument):
    """The base class for all movement stages.

    This class provides access to the XPS controller that controls the movement
    of stages. Movement that is specific to a subset of stages should be
    written into the subclasses.
    """

    def __init__(self, config):
        """Initialize the instrument, without configuring.

        Typically, PLACE instruments should be configured only when the
        config() method is called. However, we pass the JSON config data into
        the object at this stage and save it. This is handled by the Instrument
        init method. Class variables should be set to trivial values in this
        method as a form of documentation. Additionally, minimal resource
        gathering is appropriate here, if needed. For example, this
        initialization method creates the XPS object needed to access the
        controller.

        By following this design pattern, it creates a contrast between
        instruments which have been initialized vs. instruments which have been
        configured, which is a subtle but important difference.

        :param config: configuration data (from JSON)
        :type config: dict
        """
        # Always call the initializer of the base class first.
        Instrument.__init__(self, config)

        # Create the controller object and variable to save the ID number of
        # the socket used to communicate with it.
        self._controller = XPS_C8_drivers.XPS()
        self._socket = None

        # The stages will have a start position and will move incrementally at
        # each update. Since our desired position can be sent to them as an
        # absolute position, a Python iterator perfectly covers this need. We
        # will store the position iterator here.
        self._position = None

        # Each stage is given a group name. These are often used to access
        # specific types of stages. Therefore, this value must be assigned by
        # the subclasses.
        self._group = None

        # All of our data is saved into a NumPy record array and returned to
        # PLACE during cleanup.
        self._data = None

        # Note that all our class variables start with an underscore. This is
        # used to indicate that these values are of no concern to anything
        # outside this file. You will see this on many of the class methods as
        # well. From PLACE's point of view, this is exactly what it wants. It
        # doesn't want to have to worry about a long list of variables. It
        # simply needs to access config(), update(), cleanup(), and maybe a few
        # other values. If you find yourself frequently needing create public
        # variables or methods when you are writing your plugin, you may need
        # to rethink the design - or possibly make a modification to PLACE
        # itself.



### PUBLIC METHODS ###

# These are the methods that are accessed by PLACE.

    def config(self, metadata, total_updates):
        """Configure the stage for a scan.

        For a movement stage, configuring means setting up all the internal
        values. It does not mean that we move to the first position. No actual
        movement should happen until the update() method is called.

        At this time, all we need to do is initialize all our class variables
        and connect to the XPS controller.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this scan
        :type total_updates: int
        """
        # From here, we call a host of private methods. This is another way of
        # documenting the code. It succinctly lists the steps performed to
        # configure the XPS controller without making the reader wade through
        # the implementation. Being class methods, they have access to all the
        # class variables, meaning we don't need to send in any parameters or
        # get any returns.
        self._create_position_iterator()
        self._connect_to_server()
        self._check_controller_status()
        self._login()
        self._init_group()
        self._group_home_search()

        # Here, we will create the array of data for this instrument that will
        # be sent back to PLACE. Stages currently only collect position data.
        self._data = np.recarray(
            (total_updates,),
            dtype=[('update', int), ('position', float)])

    def update(self, update_number, socket=None):
        """Move the stage.

        We will then move the stage and ask the controller to return to us the
        actual position the stage settled at. We will save this position into
        the header.

        :param update_number: the current update count
        :type update_number: int

        :param socket: connection to the webapp plot frame
        :type socket: websocket
        """
        # Move the stage to the next position.
        self._move_stage()

        # Get the current position and save it in our data array.
        self._data[update_number] = (update_number, float(self._get_position()))

    def cleanup(self, abort=False):
        """Stop stage movement and end scan.

        For us, this simply means closing the connection to the XPS controller.

        :param abort: indicates the scan has been stopped rather than having
                      finished normally
        :type abort: bool
        """
        self._close_controller_connection()

# PRIVATE METHODS

    def _create_position_iterator(self):
        self._position = count(self._config['start'], self._config['increment'])

    def _connect_to_server(self):
        ip_address = PlaceConfig().get_config_value(__name__, "stage_ip_address")
        port = 5001
        timeout = 3
        self._socket = self._controller.TCP_ConnectToServer(ip_address, port, timeout)
        if self._socket == -1:
            raise RuntimeError(__name__ + ": connection failed")

    def _check_controller_status(self):
        ret = self._controller.ControllerStatusGet(self._socket)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": status error: " + err_list[1])

    def _login(self):
        ret = self._controller.Login(self._socket, "Administrator", "Administrator")
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": login failed: " + err_list[1])

    def _init_group(self):
        self._controller.GroupKill(self._socket, self._group)
        ret = self._controller.GroupInitialize(self._socket, self._group)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": group initialize failed: " + err_list[1])

    def _group_home_search(self):
        self._controller.GroupStatusGet(self._socket, self._group)
        ret = self._controller.GroupHomeSearch(self._socket, self._group)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": home search failed: " + err_list[1])

    def _move_stage(self):
        position = next(self._position)
        ret = self._controller.GroupMoveAbsolute(self._socket, self._group, [position])
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[0])
            raise RuntimeError(__name__ + ": move abolute failed: " + err_list[1])
        sleep(5)

    def _get_position(self):
        ret = self._controller.GroupPositionCurrentGet(self._socket, self._group, 1)
        if ret[0] != _SUCCESS:
            raise RuntimeError(__name__ + ": get position failed: " + ret[2])
        return ret[1]

    def _close_controller_connection(self):
        self._controller.TCP_CloseSocket(self._socket)

class ShortStage(Stage):
    """Short stage"""
    def __init__(self, config):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Stage.__init__(self, config)
        self._group = 'SHORT_STAGE' # group name

class LongStage(Stage):
    """Short stage"""
    def __init__(self, config):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Stage.__init__(self, config)
        self._group = 'LONG_STAGE' # group name

class RotationalStage(Stage):
    """Rotational stage"""
    def __init__(self, config):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Stage.__init__(self, config)
        self._group = 'ROT_STAGE'
