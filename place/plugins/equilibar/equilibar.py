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
        self.name = None
        self.serial_port = None
        self.max_p = 20.
        self.min_p = 0.
        self.tolerance = 0.01
        self.press_incrs_min = 0.
        self.press_incrs_min_time_period = 1.
        self.press_decrs_min = 0.
        self.press_decrs_min_time_period = 1.
        self.max_adjustment_wait_time = 1.
        self.starting_press = 0.
        self._all_pressures = []


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

        self._initialise_serial()

        # Go to the starting pressure
        self.starting_press = self._config['start_pressure']
        #current_p, set_point = self._set_pressure(self.starting_press, monitor=False)
        current_p, set_point = self._get_data()
        p_data = np.array([current_p, set_point])
        self._all_pressures.append(p_data)


    def update(self, update_number, progress):
        """Update the EPR-3000 electronic pressure regulator"""

        current_p, set_point = self._get_data()

        #if not (self.starting_press-self.tolerance <= current_p <= self.starting_press+self.tolerance) or\
        #    set_point != self.starting_press:

        #    current_p, set_point = self._set_pressure(self.starting_press, monitor=True)

        p_data = np.array([current_p, set_point])
        self._all_pressures.append(p_data)
        self._draw_plot(self._all_pressures, update_number, "Equilibar Pressure", 
                        ["Actual Pressure", "Setpoint"], ["green","purple"], ["square","square"])

        field = '{}-pressure'.format(self.name)
        data = np.array( [ (p_data, ) ], dtype=[ (field, 'f8', 2) ] )
        return data


    def cleanup(self, abort=False):
        """Cleanup the EPR-3000 electronic pressure regulator"""

        if not abort:
            if self._config['end_true']:
                end_press = self._config['end_pressure']
                self._set_pressure(end_press, monitor=True)
        else:
            current_p, _ = self._get_data()
            self._set_pressure(current_p, monitor=False)

    def _initialise_serial(self):
        """
        Initialise serial comms
        """
        # Initialise serial
        reg = self._open_connection()
        reg.write(bytes('*@=A\r'.encode('ascii')))   #Set to polling mode
        reg.close()

    def _open_connection(self):
        """
        Open the serial connection to the regulator
        """
        i = 0
        while i < 5:
            try:
                reg = serial.Serial(self.serial_port, baudrate=19200, bytesize=serial.EIGHTBITS, 
                                            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
                break
            except:
                time.sleep(1)
                i += 1
                if i == 5:
                    raise IOError("Equilibar: Cannot connect to regulator.")
        reg.flushOutput()
        reg.flushInput()
        return reg

    def _get_data(self):
        """
        Read the current pressure and the set point
        from the regulator
        """

        reg = self._open_connection()

        i = 0
        while i < 2:
            reg.write(bytes('A\r'.encode('ascii')))
            time.sleep(0.05)
            bytesToRead = reg.inWaiting()
            _ = reg.read(bytesToRead)
            i += 1
        
        reg.write(bytes('A\r'.encode('ascii')))
        time.sleep(0.05)
        bytesToRead = reg.inWaiting()
        
        try:
            dat = reg.read(bytesToRead)
            reg.close()
            dat = dat.decode('ascii')
            dat = dat.split()
            current_p = float(dat[1][1:])
            set_point = float(dat[2])
        except:
            reg.close()
            raise RuntimeError('Cannot read data from pressure regulator.')

        return current_p, set_point


    def _set_pressure(self, pressure, monitor=True):
        """
        Set the pressure of the regulator and monitor
        (hold) until the desired pressure is reached
        """

        pressure = float(pressure)

        if not (self.min_p <= pressure <= self.max_p): 
            raise ValueError('Pressure regulator value out of range.')

        orig_p, _ =  self._get_data()   
        prev_p = orig_p

        reg = self._open_connection()
        reg.write(bytes('AS{}\r'.format(round(pressure,2)).encode('ascii')))
        reg.close()
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

    def _draw_plot(self, data, update_number, title, labels, colors, symbols):
        """Draw a plot of the pressure"""

        lines = []
        for i in range(len(data[0])):
            line_data = [l[i] for l in data]
            line = self.plotter.line(
                    line_data,
                    color=colors[i],
                    shape=symbols[i],
                    label=labels[i]
                )
            lines.append(line)

        self.plotter.view( title, lines )

        # TODO: add axis labels when PLACE supports it
        # plt.xlabel('Update Number')
        # plt.ylabel('Temperature (C)')