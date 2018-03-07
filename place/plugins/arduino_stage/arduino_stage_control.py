import serial

from place.plugins.instrument import Instrument
from place.config import PlaceConfig

class ArduinoStage(Instrument):

    def __init__(self, config):

        Instrument.__init__(self, config)
        self._position = None
        

    def config(self, metadata, total_updates):
        
        name = self.__class__.__name__
        self.serial_port = PlaceConfig().get_config_value(name, 'serial_port')
        start = self._config['start']
        step = self._config['increment']
        end = start + (step * total_updates)

        self.arduino = serial.Serial(self.serial_port, timeout=0.5)
        self.arduino.flush()
        wait = _read_serial(self.arduino)  #Waits for ready code from Arduino

        self.arduino.write(bytes('i\n','ascii'))
        id_string = _read_serial(self.arduino)
        self._position = _get_position(self.arduino)
        
        metadata['ArduinoStage-id-string'] = id_string.strip()


    def update(self, update_number):

        new_freq = self._config['start'] + (update_number * self._config['increment'])

        self.arduino.write(bytes('c{}\n'.format(new_freq),'ascii'))
        self._position = _get_position(self.arduino)


    def cleanup(self, abort=False):
        pass
        

    ####Private Methods####

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


