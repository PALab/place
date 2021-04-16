"""Mirror movement using the New Focus picomotors."""
from itertools import cycle, repeat
from socket import timeout
from time import sleep

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from place.config import PlaceConfig
from place.plugins.instrument import Instrument

from . import pmot
from .pmot import PMot


class Picomotor(Instrument):
    """The picomotor class."""

    def __init__(self, config, plotter):
        """Initialize the controller, without configuring.

        :param config: configuration data (from JSON)
        :type config: dict

        :param plotter: a plotting object to return plots to the web interface
        :type plotter: plots.PlacePlotter
        """
        Instrument.__init__(self, config, plotter)
        self._controller = None
        self._position = None
        self.last_x = None
        self.last_y = None
        self.fig = None
        self.ax = None

    def config(self, metadata, total_updates):
        """Configure the picomotors for an experiment.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this experiment
        :type total_updates: int
        """
        self._configure_controller()
        self._create_position_iterator(total_updates)

    def update(self, update_number, progress):
        """Move the mirror.

        :param update_number: the current update count
        :type update_number: int

        :param progress: the PLACE values sent to your web application
        :type progress: dict

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
            self._position = (polar_to_cart(rho, phi)
                              for phi in np.arange(0, 2*np.pi, phi_delta))
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
        elif self._config['shape'] == 'custom':
            filename = self._config['custom_filename']
            with open(filename,'r') as f:
                data = f.readlines()
            try:
                all_coords = []
                for row in data:
                    coords = row.strip().split(',')
                    coords = (float(val) for val in coords)
                    all_coords.append(coords)
            except ValueError:
                raise ValueError('Invalid custom coordinate file for New Focus. Must be a .txt where each row is the x,y coord.')
            self._position = (values for values in all_coords)
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
                x_result, y_result = self._controller.absolute_move(
                    x_position, y_position)
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

        :returns: the PLACE plot
        :rtype: dict
        """
        name = self.__class__.__name__
        if update_number == 0:
            self.fig = Figure(figsize=(7.29, 4.17), dpi=96)
            FigureCanvas(self.fig)
            self.ax = self.fig.add_subplot(111)
            if self._config['invert_x']:
                self.ax.invert_xaxis()
            if self._config['invert_y']:
                self.ax.invert_yaxis()
            self.ax.axis('equal')
            curr_x = data[0]['{}-x_position'.format(name)]
            curr_y = data[0]['{}-y_position'.format(name)]
            self.ax.plot(curr_x, curr_y, '-o')
            self.last_x = curr_x
            self.last_y = curr_y
        else:
            curr_x = data[0]['{}-x_position'.format(name)]
            curr_y = data[0]['{}-y_position'.format(name)]
            self.ax.plot([self.last_x, curr_x],
                         [self.last_y, curr_y], '-o')
            self.last_x = curr_x
            self.last_y = curr_y
        return self.plotter.png(
            'Picomotor motion',
            self.fig,
            alt='Plot showing the movement of the picomotors'
        )


def polar_to_cart(rho, phi):
    """Convert polar to cartesian"""
    return rho * np.cos(phi), rho * np.sin(phi)
