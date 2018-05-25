"""Mirror movement using the New Focus picomotors."""
from time import sleep
from socket import timeout
from itertools import cycle, repeat
import numpy as np
import matplotlib.pyplot as plt
from place.plugins.instrument import Instrument
from place.config import PlaceConfig
from .pmot import PMot
from . import pmot

class Picomotor(Instrument):
    """The picomotor class."""

    def __init__(self, config):
        """Initialize the controller, without configuring.

        :param config: configuration data (from JSON)
        :type config: dict
        """
        Instrument.__init__(self, config)
        self._controller = None
        self._position = None
        self.last_x = None
        self.last_y = None

    def config(self, metadata, total_updates):
        """Configure the picomotors for an experiment.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this experiment
        :type total_updates: int
        """
        self._configure_controller()
        self._create_position_iterator(total_updates)
        if self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.clf()
            if self._config['invert_x']:
                plt.gca().invert_xaxis()
            if self._config['invert_y']:
                plt.gca().invert_yaxis()
            plt.axis('equal')
            plt.ion()

    def update(self, update_number):
        """Move the mirror.

        :param update_number: the current update count
        :type update_number: int

        :returns: the position data collected
        :rtype: numpy.array
        """
        x_position, y_position = self._move_picomotors()
        x_field = '{}-x_position'.format(self.__class__.__name__)
        y_field = '{}-y_position'.format(self.__class__.__name__)
        data = np.array(
            [(x_position, y_position)],
            dtype=[(x_field, 'int32'), (y_field, 'int32')])
        if self._config['plot']:
            plt.figure(self.__class__.__name__)
            self._make_position_plot(data, update_number)
        sleep(self._config['sleep_time'])
        return data

    def cleanup(self, abort=False):
        """Stop picomotor and end experiment.

        :param abort: indicates the experiment is being aborted rather than having
                      finished normally
        :type abort: bool
        """
        self._controller.close()
        if abort is False and self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()

# PRIVATE METHODS

    def _configure_controller(self):
        """Send all the starting configurations to the picomotors."""
        name = self.__class__.__name__
        ip_address = PlaceConfig().get_config_value(name, "ip_address")
        port = PlaceConfig().get_config_value(name, "port")

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

        :param total_updates: the number of update steps that will be in this experiment
        :type total_updates: int

        :raises ValueError: if an invalid shape is requested in the JSON configuration
        """
        if self._config['shape'] == 'point':
            x_one = self._config['x_one']
            y_one = self._config['y_one']
            self._position = repeat((x_one, y_one), total_updates)
        elif self._config['shape'] == 'line':
            x_one = self._config['x_one']
            y_one = self._config['y_one']
            x_two = self._config['x_two']
            y_two = self._config['y_two']
            x_delta = (x_two - x_one) / (total_updates - 1)
            y_delta = (y_two - y_one) / (total_updates - 1)
            self._position = ((x_one + i * x_delta,
                               y_one + i * y_delta) for i in np.arange(total_updates))
        elif self._config['shape'] == 'circle':
            x_one = self._config['x_one']
            y_one = self._config['y_one']
            rho = self._config['radius']
            phi_delta = 2 * np.pi / total_updates
            self._position = (polar_to_cart(rho, phi) for phi in np.arange(0, 2*np.pi, phi_delta))
        elif self._config['shape'] == 'arc':
            x_one = self._config['x_one']
            y_one = self._config['y_one']
            rho = self._config['radius']
            phi_delta = 2 * np.pi / self._config['sectors']
            self._position = cycle(
                polar_to_cart(rho, phi) for phi in np.arange(0, 2*np.pi, phi_delta)
                )
            for _ in range(self._config['starting_sector']):
                next(self._position)
        else:
            raise ValueError('unrecognized shape')

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

    def _make_position_plot(self, data, update_number):
        """Plot the x,y position throughout the experiment.

        :param data: the data to display on the plot
        :type data: numpy.array

        :param update_number: the current update
        :type update_number: int
        """
        if update_number == 0:
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
        plt.pause(0.05)

def polar_to_cart(rho, phi):
    """Convert polar to cartesian"""
    return rho * np.cos(phi), rho * np.sin(phi)
