"""Mirror movement using the New Focus picomotors."""
from time import sleep
from threading import Thread
from itertools import count, zip_longest
import numpy as np
import matplotlib.pyplot as plt
import mpld3
from place.plugins.instrument import Instrument, send_data_thread
from place.config import PlaceConfig
from .pmot import PMot
from . import pmot

class Picomotor(Instrument):
    """The picomotor class."""

    def __init__(self, config):
        """Initialize the controller, without configuring.

        Requires the following JSON values:

        plot : bool
            tells the instrument if it should plot data or not

        sleep_time : float
            amount of time to sleep after moving the motors

        mirror_distance : float
            mirror distance

        x_start : float
            start position of the x motor

        y_start : float
            start position of the y motor

        x_increment : float
            increment for the x motor

        y_increment : float
            increment for the y motor

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Instrument.__init__(self, config)
        # socket for sending commands to the New Focus controller
        self._controller = None
        # an iterator for motor positions
        self._position = None

    def config(self, metadata, total_updates):
        """Configure the picomotors for a scan.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this scan
        :type total_updates: int
        """
        self._configure_controller()
        self._create_position_iterator()

    def update(self, update_number, socket=None):
        """Move the mirror.

        :param update_number: the current update count
        :type update_number: int

        :param socket: connection to the plot
        :type socket: websocket

        :returns: the position data collected
        :rtype: numpy.recarray
        """
        x_position, y_position = self._move_picomotors()
        data = np.array(
            (update_number, x_position, y_position),
            dtype=[('update', int), ('x_position', float), ('y_position', float)])
        if self._config['plot']:
            _make_position_plot(data, update_number, socket)
        sleep(self._config['sleep_time'])
        return data

    def cleanup(self, abort=False):
        """Stop picomotor and end scan.

        :param abort: indicates the scan is being aborted rather than having
                      finished normally
        :type abort: bool
        """
        self._controller.close()

# PRIVATE METHODS

    def _configure_controller(self):
        """Send all the starting configurations to the picomotors."""
        ip_address = PlaceConfig().get_config_value(__name__, "picomotor_ip_address")
        port = PlaceConfig().get_config_value(__name__, "picomotor_port")

        self._controller = PMot()
        self._controller.connect(ip_address, int(port))

        self._controller.set_velocity(pmot.PX, 1700)
        self._controller.set_velocity(pmot.PY, 1700)

        self._controller.set_home_position(pmot.PX, 0)
        self._controller.set_home_position(pmot.PY, 0)

        self._controller.set_axis_displacement(pmot.PX, 1)
        self._controller.set_axis_displacement(pmot.PY, 1)

        self._controller.set_following_error(pmot.PX, 200)
        self._controller.set_following_error(pmot.PY, 200)

        self._controller.set_cl(pmot.PX, 0.1)
        self._controller.set_cl(pmot.PY, 0.1)

        self._controller.set_mm(pmot.PX, 1)
        self._controller.set_mm(pmot.PY, 1)

        self._controller.set_sm()

    def _create_position_iterator(self):
        """Create a Python iterator object to control motion.

        Each time next() is called on this object, it will return the next x,y
        position.
        """
        # 1 step = 1.8 urad
        theta_step = 1.8e-6
        divisions = self._config['mirror_distance'] / theta_step
        x_start = self._config['x_start'] / divisions
        y_start = self._config['y_start'] / divisions
        x_increment = self._config['x_increment'] / divisions
        y_increment = self._config['y_increment'] / divisions
        self._position = zip_longest(count(x_start, x_increment),
                                     count(y_start, y_increment))

    def _move_picomotors(self):
        """Move the picomotors.

        :returns: the x and y positions of the motors
        :rtype: (float, float)
        """
        x_position, y_position = next(self._position)
        self._controller.absolute_move(pmot.PX, x_position)
        self._controller.absolute_move(pmot.PY, y_position)
        return x_position, y_position

def _make_position_plot(data, update_number, socket=None):
    """Plot the x,y position throughout the scan.

    :param data: the data to display on the plot
    :type data: numpy.array

    :param update_number: the current update
    :type update_number: int

    :param socket: communication with the web interface
    :type socket: websocket
    """
    if update_number == 0:
        plt.clf()
        if socket is None:
            plt.ion()
        plt.plot(data[0]['x_position'], data[0]['y-position'], '-o')
    else:
        i = update_number - 1
        j = update_number
        plt.plot([data[i]['x_position'], data[j]['x_position']],
                 [data[i]['y-position'], data[j]['y-position']], '-o')
    if socket is None:
        plt.pause(0.05)
    else:
        out = mpld3.fig_to_html(plt.gcf())
        thread = Thread(target=send_data_thread, args=(socket, out))
        thread.start()
        thread.join()
