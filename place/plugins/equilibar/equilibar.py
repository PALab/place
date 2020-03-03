"""Equlibar EPR-3000 electronic pressure regulator"""

import serial
import time
import numpy as np

from place.plugins.instrument import Instrument
from place.config import PlaceConfig


class EquilibarEPR3000(Instrument):
    """
    Write the documentation
    """

    def __init__(self, config, plotter):
        Instrument.__init__(self, config, plotter)

    def config(self, metadata, total_updates):
        """
        Configure the EPR-3000 electronic pressure regulator.
        """

        self.name = self.__class__.__name__

        # Initialise configuration variables
        _place_config = PlaceConfig()
        self.serial_port = _place_config.get_config_value(self.name, 'serial_port')
        self.max_p = float(_place_config.get_config_value(self.name, 'maximum_pressure'))
        self.min_p = float(_place_config.get_config_value(self.name, 'minimum_pressure'))
        self.tolerance = float(_place_config.get_config_value(self.name, 'tolerance'))
        self.press_incrs_min = float(_place_config.get_config_value(self.name, 'pressure_increase_minimum'))
        self.press_incrs_min_time_period = float(_place_config.get_config_value(self.name, 'pressure_increase_minimum_time_period'))
        self.press_decrs_min = float(_place_config.get_config_value(self.name, 'pressure_decrease_minimum'))
        self.press_decrs_min_time_period = float(_place_config.get_config_value(self.name, 'pressure_decrease_minimum_time_period'))
        self.max_adjustment_wait_time = float(_place_config.get_config_value(self.name, 'max_adjustment_wait_time'))

        metadata[self.name+'-units'] = self._config['units']

        # Initialise serial
        self.reg = serial.Serial(self.serial_port, baudrate=19200, bytesize=serial.EIGHTBITS, 
                                    parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

        self.reg.flushOutput()
        self.reg.flushInput()
        self.reg.write(bytes('*@=A\r'.encode('ascii')))   #Set to polling mode

        # Go to the starting pressure
        self.starting_press = self._config['start_pressure']
        self._set_pressure(self.starting_press, monitor=True)


    def update(self, update_number, progress):
        """Update the EPR-3000 electronic pressure regulator"""

        current_p, set_point = self._get_data()

        if not (self.starting_press-self.tolerance <= current_p <= self.starting_press+self.tolerance) or\
            set_point != self.starting_press:

            current_p, set_point = self._set_pressure(self.starting_press, monitor=True)

        field = '{}-pressure'.format(self.name)
        data = np.array( [ (current_p, ) ], dtype=[ (field, 'float64') ] )
        return data


    def cleanup(self, abort=False):
        """Cleanup the EPR-3000 electronic pressure regulator"""

        if not abort:
            if self._config['end_true']:
                end_press = self._config['end_pressure']
                self._set_pressure(end_press, monitor=True)
        else:
            if self.reg.isOpen():
                current_p, set_point = self._get_data()
                self._set_pressure(current_p, monitor=False)

        self.reg.close()


    def _get_data(self):

        self.reg.flushOutput()
        self.reg.flushInput()

        # Make sure to flush out any strange data
        i = 0
        t0 = time.time()
        while i < 2:
            self.reg.write(bytes('A\r'.encode('ascii')))
            time.sleep(0.05)
            bytesToRead = self.reg.inWaiting()
            at = self.reg.read(bytesToRead)
            i += 1
        
        self.reg.write(bytes('A\r'.encode('ascii')))
        time.sleep(0.05)
        bytesToRead = self.reg.inWaiting()
        
        try:
            dat = self.reg.read(bytesToRead)
            dat = dat.decode('ascii')
            dat = dat.split()
            current_p = float(dat[1][1:])
            set_point = float(dat[2])

            return current_p, set_point
        except:
            self.reg.close()
            raise RuntimeError('Cannot read data from pressure regulator.')


    def _set_pressure(self, pressure, monitor=True):

        pressure = float(pressure)

        if not (self.min_p <= pressure <= self.max_p): 
            self.reg.close()
            raise ValueError('Pressure regulator value out of range.')

        orig_p, _ =  self._get_data()   
        prev_p = orig_p

        self.reg.flushOutput()
        self.reg.flushInput()
        self.reg.write(bytes('AS{}\r'.format(round(pressure,2)).encode('ascii')))
        set_point = pressure

        if monitor:
            # Monitor the pressure changes
            all_pressures, all_times = [], []
            t0 = time.time()
            if pressure > prev_p+self.tolerance:
                
                while prev_p < set_point-self.tolerance:
                    current_p, _ = self._get_data()

                    if time.time()-t0 > self.press_incrs_min_time_period:
                        press_at_initial_time = np.argmin(np.abs((time.time()-t0)-np.array(all_times)-self.press_incrs_min_time_period))
                        if abs(current_p - all_pressures[press_at_initial_time]) < self.press_incrs_min:
                            self._set_pressure(current_p-self.tolerance, monitor=False)
                            self.reg.close()
                            raise RuntimeError('Pressure not increasing. Please check pressure supply and valves to ensure adequate flow.')
                    
                    prev_p = current_p
                    all_pressures.append(current_p)
                    all_times.append(time.time()-t0)                

            elif pressure < prev_p-self.tolerance:
                
                while prev_p > set_point+self.tolerance:
                    current_p, _ = self._get_data()

                    if time.time()-t0 > self.press_decrs_min_time_period:
                        press_at_initial_time = np.argmin(np.abs((time.time()-t0)-np.array(all_times)-self.press_decrs_min_time_period))
                        if abs(current_p - all_pressures[press_at_initial_time]) < self.press_decrs_min:
                            self._set_pressure(current_p+self.tolerance, monitor=False)
                            self.reg.close()
                            raise RuntimeError('Pressure not decreasing. Please check valves and exhaust.')
                    
                    prev_p = current_p
                    all_pressures.append(current_p)
                    all_times.append(time.time()-t0)                

            # The previous loops made sure the pressure was able to get close to the set point
            # This loop waits until the pressure reaches the exact set point, or 60 seconds, whichever is less.
            t0, counter = time.time(), 0
            while time.time()-t0 < self.max_adjustment_wait_time:
                current_p, _ = self._get_data()
                if abs(current_p - pressure) < 0.0001:
                    counter += 1
                    if counter > 5:
                        break
                    time.sleep(1)
                    continue
                counter = 0
                time.sleep(1)

        current_p, real_set_point = self._get_data()
        return current_p, real_set_point