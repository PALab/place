"""Stage movement using the XPS-C8 controller."""
from time import sleep
from itertools import count, repeat
import numpy as np
from place.plugins.instrument import Instrument
from place.config import PlaceConfig, PlaceConfigError
from . import XPS_C8_drivers

_SUCCESS = 0


class Stage(Instrument):
    """The base class for all movement stages.

    This class provides access to the XPS controller that controls the movement
    of stages. Movement that is specific to a subset of stages should be
    written into the subclasses.

    The XPS Controller module requires the following configuration data
    (accessible as self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    mode                      string         the stages can either operate in 'incremental'
                                             mode, where they move a set amount at each
                                             update; or 'continuous' mode, where they move
                                             throughout the experiment (or until they reach
                                             their limit)
    velocity                  float          the target velocity for movement
    acceleration              float          the acceleration allowed to achieve velocity
    wait                      float          the amount of time to wait after stage movement
                                             (allows the sample to settle)
    start                     float          start position of stage
    increment                 float          the step distance for the stage (can also be
                                             calculated by PLACE using the 'end' value)
    end                       float          end position of the stage (can also be
                                             calculated by PLACE using the 'increment'
                                             value)
    ========================= ============== ================================================
    """

    def __init__(self, config, plotter):
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

        :param plotter: a plotting object to return plots to the web interface
        :type plotter: plots.PlacePlotter
        """
        Instrument.__init__(self, config, plotter)

        self._controller = XPS_C8_drivers.XPS()
        self._socket = None
        self._position = None
        self._group = None
        self._positioner = None

    def config(self, metadata, total_updates):
        """Configure the stage for an experiment.

        For a movement stage, configuring means setting up all the internal
        values. It does not mean that we move to the first position. No actual
        movement should happen until the update() method is called.

        At this time, all we need to do is initialize all our class variables
        and connect to the XPS controller.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this experiment
        :type total_updates: int
        """
        if self._config['mode'] == 'incremental':
            self._create_position_iterator(total_updates)
        self._connect_to_server()
        self._check_controller_status()
        self._login()
        self._init_group()
        self._group_home_search()
        self._set_sgamma()
        self._move_stage(position=self._config['start'])
        if self._config['mode'] == 'continuous':
            self._enable_jogging()
        sleep(self._config['wait'])

    def update(self, update_number, progress):
        """Move the stage.

        In incremental mode, this will then move the stage and ask the
        controller to return to us the actual position the stage settled at. We
        will save this position into the NumPy data.

        In continuous mode, this will start the motion on the first update. On
        each update, the current position will be saved, however, as the stage
        will be in motion, this will not reflect the position at which other
        PLACE events occured.

        :param update_number: the current update count
        :type update_number: int

        :returns: the position data for this update of this instrument
        :rtype: numpy.array
        """
        if self._config['mode'] == 'incremental':
            # Move the stage to the next position.
            self._move_stage()
        elif self._config['mode'] == 'continuous' and update_number == 0:
            # Turn on stage jogging.
            self._jog_stage()
        sleep(self._config['wait'])

        # Get the current position and save it in our data array.
        field = '{}-position'.format(self.__class__.__name__)
        data = np.array(
            [(float(self._get_position()),)],
            dtype=[(field, 'float64')])

        # return the data from this instrument for this update
        return data

    def cleanup(self, abort=False):
        """Stop stage movement and end the experiment.

        For us, this simply means closing the connection to the XPS controller.

        :param abort: indicates the experiment has been stopped rather than
                      having finished normally
        :type abort: bool
        """
        if self._config['mode'] == 'continuous':
            self._move_abort()
        self._close_controller_connection()

# PRIVATE METHODS

    def _create_position_iterator(self, updates):
        if updates == 1:
            self._position = repeat(self._config['start'])
            return
        try:
            self._position = count(
                self._config['start'], self._config['increment'])
        except KeyError:
            increment = (self._config['end'] -
                         self._config['start']) / (updates - 1)
            self._position = count(self._config['start'], increment)

    def _connect_to_server(self):
        ip_address = PlaceConfig().get_config_value('XPS', "ip_address")
        port = 5001
        timeout = 3
        self._socket = self._controller.TCP_ConnectToServer(
            ip_address, port, timeout)
        if self._socket == -1:
            raise RuntimeError(__name__ + ": connection failed")

    def _check_controller_status(self):
        ret = self._controller.ControllerStatusGet(self._socket)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": status error: " + err_list[1])

    def _login(self):
        ret = self._controller.Login(
            self._socket, "Administrator", "Administrator")
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": login failed: " + err_list[1])

    def _init_group(self):
        self._controller.GroupKill(self._socket, self._group)
        ret = self._controller.GroupInitialize(self._socket, self._group)
        if ret[0] != _SUCCESS:
            self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": group initialize failed: perhaps "
                               + "you need to update the group name in ~/.place.cfg")

    def _set_sgamma(self):
        ret = self._controller.PositionerSGammaParametersSet(
            self._socket,
            self._positioner,
            self._config['velocity'],
            self._config['acceleration'],
            0.04, 0.04)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(__name__ + ": set SGamma failed: " + err_list[1] +
                               ": perhaps the velocity or acceleration value is out of range?")

    def _group_home_search(self):
        self._controller.GroupStatusGet(self._socket, self._group)
        ret = self._controller.GroupHomeSearch(self._socket, self._group)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(
                __name__ + ": home search failed: " + err_list[1])

    def _enable_jogging(self):
        ret = self._controller.GroupJogModeEnable(self._socket, self._group)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(
                __name__ + ": enable jogging failed: " + err_list[1])

    def _disable_jogging(self):
        ret = self._controller.GroupJogModeDisable(self._socket, self._group)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(
                __name__ + ": disable jogging failed: " + err_list[1])

    def _move_stage(self, position=None):
        if position is None:
            position = next(self._position)
        ret = self._controller.GroupMoveAbsolute(
            self._socket, self._group, [position])
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[0])
            raise RuntimeError(
                __name__ + ": move absolute failed: " + err_list[1])

    def _jog_stage(self):
        ret = self._controller.GroupJogParametersSet(
            self._socket,
            self._group,
            self._config['velocity'],
            self._config['acceleration'])
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[0])
            raise RuntimeError(
                __name__ + ": move abolute failed: " + err_list[1])

    def _move_abort(self):
        ret = self._controller.GroupMoveAbort(self._socket, self._group)
        if ret[0] != _SUCCESS:
            err_list = self._controller.ErrorStringGet(self._socket, ret[1])
            raise RuntimeError(
                __name__ + ": abort movement failed: " + err_list[1])

    def _get_position(self):
        ret = self._controller.GroupPositionCurrentGet(
            self._socket, self._group, 1)
        if ret[0] != _SUCCESS:
            raise RuntimeError(__name__ + ": get position failed: " + ret[2])
        return ret[1]

    def _close_controller_connection(self):
        self._controller.TCP_CloseSocket(self._socket)


class ShortStage(Stage):
    """Short stage"""

    def __init__(self, config, plotter):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Stage.__init__(self, config, plotter)
        try:
            self._group = PlaceConfig().get_config_value(
                self.__class__.__name__, 'group_name')
        except PlaceConfigError:
            raise RuntimeError(
                'Cannot find the group name for the {} '.format(self.__class__.__name__) +
                'in ~/.place.cfg\nPlease determine the group name and ' +
                'add it to this file.\n(See the XPS Controller ' +
                'documentation for more details.')
        try:
            self._positioner = PlaceConfig().get_config_value(
                self.__class__.__name__, 'positioner_name')
        except PlaceConfigError:
            raise RuntimeError(
                'Cannot find the positioner name for the {} '.format(self.__class__.__name__) +
                'in ~/.place.cfg\nPlease determine the positioner name and ' +
                'add it to this file.\n(See the XPS Controller ' +
                'documentation for more details.')


class LongStage(Stage):
    """Short stage"""

    def __init__(self, config, plotter):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Stage.__init__(self, config, plotter)
        try:
            self._group = PlaceConfig().get_config_value(
                self.__class__.__name__, 'group_name')
        except PlaceConfigError:
            raise RuntimeError(
                'Cannot find the group name for the {} '.format(self.__class__.__name__) +
                'in ~/.place.cfg\nPlease determine the group name and ' +
                'add it to this file.\n(See the XPS Controller ' +
                'documentation for more details.')
        try:
            self._positioner = PlaceConfig().get_config_value(
                self.__class__.__name__, 'positioner_name')
        except PlaceConfigError:
            raise RuntimeError(
                'Cannot find the positioner name for the {} '.format(self.__class__.__name__) +
                'in ~/.place.cfg\nPlease determine the positioner name and ' +
                'add it to this file.\n(See the XPS Controller ' +
                'documentation for more details.')


class RotStage(Stage):
    """Rotational stage"""

    def __init__(self, config, plotter):
        """Constructor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Stage.__init__(self, config, plotter)
        try:
            self._group = PlaceConfig().get_config_value(
                self.__class__.__name__, 'group_name')
        except PlaceConfigError:
            raise RuntimeError(
                'Cannot find the group name for the {} '.format(self.__class__.__name__) +
                'in ~/.place.cfg\nPlease determine the group name and ' +
                'add it to this file.\n(See the XPS Controller ' +
                'documentation for more details.')
        try:
            self._positioner = PlaceConfig().get_config_value(
                self.__class__.__name__, 'positioner_name')
        except PlaceConfigError:
            raise RuntimeError(
                'Cannot find the positioner name for the {} '.format(self.__class__.__name__) +
                'in ~/.place.cfg\nPlease determine the positioner name and ' +
                'add it to this file.\n(See the XPS Controller ' +
                'documentation for more details.')
