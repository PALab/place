"""PLACE plugin for the Arduino stage"""
import time
import serial
import numpy as np

from place.plugins.instrument import Instrument
from place.config import PlaceConfig


class ArduinoStage(Instrument):
    """Subclass of a PLACE Instrument"""

    def __init__(self, config, plotter):
        """Initialize the Arduino stage

        :param config: configuration data (as a parsed JSON object)
        :type config: dict

        :param plotter: a plotting object to return plots to the web interface
        :type plotter: plots.PlacePlotter
        """
        Instrument.__init__(self, config, plotter)
        self._position = None
        self.name = None
        self.serial_port = None
        self.arduino = None
        self.initial_position = None
        self.servo_min = None
        self.servo_min_deg = None
        self.servo_max_deg = None
        self.deg_to_ms = None
        self.start = None
        self.increment = None
        self.end = None

    def config(self, metadata, total_updates):
        """Configure the Arduino stage

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        self.name = self.__class__.__name__

        self.serial_port = PlaceConfig().get_config_value(self.name, 'serial_port')

        self._get_calibration()  # Get the calibration of the servo from ms to deg

        # Get the start, end, and increment parameters for this scan
        self._get_positions(total_updates)

        # Initialise serial communication
        self.arduino = serial.Serial(self.serial_port, timeout=0.5)
        self.arduino.flush()
        wait = _read_serial(self.arduino)  # Waits for ready code from Arduino

        self.arduino.write(bytes('i\n', 'ascii'))  # Get id from Arduino
        id_string = _read_serial(self.arduino)
        self.initial_position = _get_position(self.arduino)

        metadata['ArduinoStage-id-string'] = id_string.strip()

    def update(self, update_number, progress):
        """Update the Arduino stage

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param progress: A blank dictionary for sending data back to the frontend
        :type progress: dict

        :returns: the position of the stage
        :rtype: dtype=[('*classname*-position', 'float64')])
        """
        new_pos_deg = self.start + (update_number * self.increment)
        new_pos = self.servo_min + (new_pos_deg * self.deg_to_ms)

        self.arduino.write(bytes('c{}\n'.format(new_pos), 'ascii'))

        time.sleep(self._config['wait'])
        self._position = _read_serial(self.arduino)

        field = '{}-position'.format(self.name)
        data = np.array([(new_pos_deg, )], dtype=[(field, 'float64')])
        return data

    def cleanup(self, abort=False):
        """Return the stepper motor to the 0 position.

        :param abort: ``True`` if the experiement is being aborted
        :type abort: bool
        """
        # Return stepper motor to 0 position, but not changing roation direction
        # Assuming that the stepper is not less than 0.0.
        if self.increment > 0.0:
            if self.servo_max_deg > 180.0:
                full_rot = 360.0 * self.deg_to_ms
                rotation_dir = abs(self.increment) // self.increment
                if rotation_dir < 0:
                    new_pos = 0.0
                else:
                    new_pos = float(self._position) + (full_rot -
                                                       (abs(float(self._position)) % full_rot))
                    self.arduino.write(bytes('c{}\n'.format(new_pos), 'ascii'))

            # Return a servo to its initial position
            else:
                self.arduino.write(
                    bytes('c{}\n'.format(self.initial_position), 'ascii'))

            wait = _read_serial(self.arduino)  # Waits for motor to stop moving

    ####Private Methods####

    def _get_calibration(self):
        '''Function which sets the calibration between ms of a
           pulse to the servo and degrees of rotation'''

        # Minimum pulse length which causes servo rotation
        self.servo_min = float(
            PlaceConfig().get_config_value(self.name, 'servo_min'))
        self.servo_min_deg = float(PlaceConfig().get_config_value(
            self.name, 'servo_min_deg'))  # Position in degrees corresponding to servo_min
        # Maximum pulse length which causes servo rotation
        servo_max = float(
            PlaceConfig().get_config_value(self.name, 'servo_max'))
        self.servo_max_deg = float(PlaceConfig().get_config_value(
            self.name, 'servo_max_deg'))  # Position in degrees corresponding to servo_max

        self.deg_to_ms = (servo_max-self.servo_min) / \
            (self.servo_max_deg-self.servo_min_deg)

    def _get_positions(self, updates):
        '''Retrieve and calculate the start and end positions and increment'''
        try:
            self.start = self._config['start']
            self.increment = self._config['increment']
            self.end = self.start + (self.increment * updates)

            self._check_start()
            self._check_inc()

        except KeyError:
            self.start = self._config['start']
            if updates > 1:
                self.increment = (
                    self._config['end'] - self._config['start']) / (updates - 1)
            else:
                self.increment = 0.0
            self.end = self._config['end']

            self._check_start()
            self._check_end()

    def _check_start(self):
        '''Check that the start value is within bounds'''
        if not self.servo_min_deg <= self.start <= self.servo_max_deg:
            raise ValueError("{} start not between {} and {}".format(
                self.name, self.servo_min_deg, self.servo_max_deg))

    def _check_end(self):
        '''Check that the end value is within bounds'''
        if not self.servo_min_deg <= self.end <= self.servo_max_deg:
            raise ValueError("{} end not between {} and {}".format(
                self.name, self.servo_min_deg, self.servo_max_deg))

    def _check_inc(self):
        '''Check that the increment doesn't put any updates outside bounds'''
        if not self.servo_min_deg <= self.end <= self.servo_max_deg:
            if self.increment > 0.0:
                raise ValueError(
                    "{}: please choose increment with final position no greater than {}".format(
                        self.name, self.servo_max_deg)
                )
            if self.increment < 0.0:
                raise ValueError(
                    "{}: please choose increment with final position no less than {}".format(
                        self.name, self.servo_min_deg)
                )

    ########################


def _get_position(arduino):
    '''
    Function to get the current position of the servo
    '''

    arduino.write(bytes('g\n', 'ascii'))
    time.sleep(0.05)
    pos = _read_serial(arduino)

    return float(pos)


def _read_serial(arduino):
    '''
    Function to read a byte from the arduino
    '''
    string = ""
    looping = True

    while looping:
        byte = arduino.read()
        if byte == bytes('\n', 'ascii'):
            looping = False
        else:
            string += byte.decode('ascii')

    return string
