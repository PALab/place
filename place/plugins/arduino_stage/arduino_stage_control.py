import serial
import time

from place.plugins.instrument import Instrument
from place.config import PlaceConfig

class ArduinoStage(Instrument):

    def __init__(self, config):

        Instrument.__init__(self, config)
        self._position = None
        

    def config(self, metadata, total_updates):
        
        self.name = self.__class__.__name__

        self.serial_port = PlaceConfig().get_config_value(self.name, 'serial_port')

        self._get_calibration()             #Get the calibration of the servo from ms to deg
        
        self._get_positions(total_updates)   #Get the start, end, and increment parameters for this scan
  
        self.arduino = serial.Serial(self.serial_port, timeout=0.5)  #Initialise serial communication
        self.arduino.flush()
        wait = _read_serial(self.arduino)                            #Waits for ready code from Arduino

        self.arduino.write(bytes('i\n','ascii'))                     #Get id from Arduino
        id_string = _read_serial(self.arduino)
        self._position = _get_position(self.arduino)
        
        metadata['ArduinoStage-id-string'] = id_string.strip()


    def update(self, update_number):

        new_pos_deg = self.start + (update_number * self.increment)
        new_pos = self.servo_min + (new_pos_deg * self.deg_to_ms)
        
        self.arduino.write(bytes('c{}\n'.format(new_pos),'ascii'))
        self._position = _get_position(self.arduino)

        time.sleep(self._config['wait'])        


    def cleanup(self, abort=False):
        pass
        

    ####Private Methods####

    def _get_calibration(self):
        '''Function which sets the calibration between ms of a 
           pulse to the servo and degrees of rotation'''

        self.servo_min = float(PlaceConfig().get_config_value(self.name, 'servo_min'))           #Minimum pulse length which causes servo rotation
        self.servo_min_deg = float(PlaceConfig().get_config_value(self.name, 'servo_min_deg'))   #Position in degrees corresponding to servo_min
        servo_max = float(PlaceConfig().get_config_value(self.name, 'servo_max'))                #Maximum pulse length which causes servo rotation
        self.servo_max_deg = float(PlaceConfig().get_config_value(self.name, 'servo_max_deg'))   #Position in degrees corresponding to servo_max
        
        self.deg_to_ms = (servo_max-self.servo_min)/(self.servo_max_deg-self.servo_min_deg)


    def _get_positions(self, updates):
        '''Retrieve and calculate the start and end positions and increment'''
        try:
            self.start = self._config['start']
            self.increment =  self._config['increment']
            self.end = self.start+ (self.increment * updates)

            self._check_start()
            self._check_inc()

        except KeyError:
            self.start = self._config['start']
            if updates > 1:
                self.increment =  (self._config['end'] - self._config['start']) / (updates - 1)
            else:
                self.increment =  0.0
            self.end = self._config['end']

            self._check_start()
            self._check_end()

    def _check_start(self):
        '''Check that the start value is within bounds'''
        if not (self.servo_min_deg <= self.start < self.servo_max_deg):
            raise ValueError("{} start not between {} and {}".format(self.name, self.servo_min_deg, self.servo_max_deg))

    def _check_end(self):
        '''Check that the end value is within bounds'''
        if not (self.servo_min_deg <= self.end < self.servo_max_deg):
            raise ValueError("{} end not between {} and {}".format(self.name, self.servo_min_deg, self.servo_max_deg))

    def _check_inc(self):
        '''Check that the increment doesn't put any updates outside bounds'''
        if not (self.servo_min_deg < self.end <= self.servo_max_deg):
            if self.increment > 0.0:
                raise ValueError("{}: please choose increment with final position no greater than {}".format(self.name, self.servo_max_deg))
            if self.increment < 0.0:
                raise ValueError("{}: please choose increment with final position no less than {}".format(self.name, self.servo_min_deg))

    ########################


def _get_position(arduino):
    '''
    Function to get the current position of the servo
    '''

    arduino.write(bytes('g\n','ascii'))
    pos = _read_serial(arduino)
 
    return pos


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


