"""Mirror movement using the New Focus picomotors."""
from time import sleep
from threading import Thread
from socket import timeout
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

        sleep_time : float
            amount of time to sleep after moving the motors

        x_one : int32
            first x position

        y_one : int32
            first y position

        x_two : int32
            second x position

        y_two : int32
            second y position

        plot : bool
            tells the instrument if it should plot data or not

        invert_x : bool
            flips the x axis on the output plot

        invert_y : bool
            flips the y axis on the output plot

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Instrument.__init__(self, config)
        # socket for sending commands to the New Focus controller
        self._controller = None
        # an iterator for motor positions
        self._position = None
        self.last_x = None
        self.last_y = None

    def config(self, metadata, total_updates):
        """Configure the picomotors for a scan.

        :param metadata: metadata for the scan
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this scan
        :type total_updates: int
        """
        self._configure_controller()
        self._create_position_iterator(total_updates)

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
            [(update_number, x_position, y_position)],
            dtype=[('update', 'int16'), ('x_position', 'int32'), ('y_position', 'int32')])
        if self._config['plot']:
            self._make_position_plot(data, update_number, socket)
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

        self._controller.set_axis_displacement(pmot.PX, 1)
        self._controller.set_axis_displacement(pmot.PY, 1)

        self._controller.set_following_error(pmot.PX, 200)
        self._controller.set_following_error(pmot.PY, 200)

        self._controller.set_cl(pmot.PX, 0.1)
        self._controller.set_cl(pmot.PY, 0.1)

        self._controller.set_mm(pmot.PX, 1)
        self._controller.set_mm(pmot.PY, 1)

        self._controller.set_sm()

    def _create_position_iterator(self, total_updates):
        """Create a Python iterator object to control motion.

        Each time next() is called on this object, it will return the next x,y
        position.

        :param total_updates: the number of update steps that will be in this scan
        :type total_updates: int
        """
        x_one = self._config['x_one']
        y_one = self._config['y_one']
        x_two = self._config['x_two']
        y_two = self._config['y_two']
        rho = np.sqrt((y_two-y_one)**2 + (x_two-x_one)**2)
        phi_delta = 2 * np.pi / total_updates
        self._position = (polar_to_cart(rho, phi) for phi in np.arange(0, 2*np.pi, phi_delta))

    def _move_picomotors(self):
        """Move the picomotors.

        :returns: the x and y positions of the motors
        :rtype: (int, int)

        :raises RuntimeError: if movement fails
        """
        tries = 25
        pause = 10
        x_position, y_position = next(self._position)
        for i in range(tries):
            try:
                if i > 0:
                    print('starting attempt number {} of {}'.format(i+1, tries))
                    self._configure_controller()
                x_result, y_result = self._controller.absolute_move(x_position, y_position)
                return x_result, y_result
            except OSError:
                print('could not connect to picomotor controller', end="")
                print('- will retry in {} seconds'.format(pause))
            except timeout:
                print('a timeout occurred - will restart in {} seconds'.format(pause))
                self._controller.close()
            if i >= tries - 1:
                raise RuntimeError('could not communicate with picomotors')
            sleep(pause)

    def _make_position_plot(self, data, update_number, socket=None):
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
            if self._config['invert_x']:
                plt.gca().invert_xaxis()
            if self._config['invert_y']:
                plt.gca().invert_yaxis()
            plt.axis('equal')
            if socket is None:
                plt.ion()
            curr_x = data[0]['x_position']
            curr_y = data[0]['y_position']
            plt.plot(curr_x, curr_y, '-o')
            self.last_x = curr_x
            self.last_y = curr_y
        else:
            curr_x = data[0]['x_position']
            curr_y = data[0]['y_position']
            plt.plot([self.last_x, curr_x],
                     [self.last_y, curr_y], '-o')
            self.last_x = curr_x
            self.last_y = curr_y
        if socket is None:
            plt.pause(0.05)
        else:
            out = mpld3.fig_to_html(plt.gcf())
            thread = Thread(target=send_data_thread, args=(socket, out))
            thread.start()
            thread.join()

def polar_to_cart(rho, phi):
    """Convert polar to cartesian"""
    return rho * np.cos(phi), rho * np.sin(phi)
