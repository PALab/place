"""A PLACE module for reading/setting/controlling the
temperature during experiments. It can accommodate
a range of sensors/controllers.
"""
import time
import os
import csv
import threading
import numpy as np
import pandas
import serial
import watlow

import place
from place.config import PlaceConfig
from place.plugins.instrument import Instrument


class TemperatureControl(Instrument):
    """Temperature read/set instrument.

    The TemperatureControl module requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    seconds_between_reads     float          number of seconds between reading temperature sensors
    read_ramptrol             bool           whether or not to read temperature values from the RamptTrol
    read_omega                bool           whether or not to read temperature values from the Omega
    plot                      bool           whether or not to plot the data in PLACE
    ========================= ============== ================================================

    The TemperatureControl will produce the following experimental data:

    +---------------+-------------------------+------------------------------------------------------+
    | Heading       | Type                    | Meaning                                              |
    +===============+=========================+======================================================+
    | temperature   | uint64                  | the latest temperature values. The shape of this     |
    |               |                         | array depends on the number of sensors chosen.       |
    |               |                         | The row for each sensor is [ time , temp1 , temp2 ]  |
    +---------------+-------------------------+------------------------------------------------------+

    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``signal`` will be recorded as ``Polytec-signal`` when using
        the Polytec vibrometer. The reason for this is because NumPy will not
        check for duplicate heading names automatically, so prepending the
        class name greatly reduces the likelihood of duplication.

    """

    def __init__(self, config, plotter):
        """Initialize the class, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict

        :param plotter: a plotting object to return plots to the web interface
        :type plotter: plots.PlacePlotter
        """
        Instrument.__init__(self, config, plotter)
        self.seconds_between_reads = None
        self.omega_csv_filename = None
        self.ramptrol_csv_filename =  None
        self._all_r_temps = []
        self._all_o_temps = []
        self._run_threads = True
        self.fixed_wait_time = None
        self.temp_tolerance = None
        self.stability_time = None
        self.last_set = None
        self.new_setpoint = None
        self._change_setpoint = False

    def config(self, metadata, total_updates):
        """Calculate basic values and record basic metadata.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: number of update that will be performed
        :type total_updates: int
        """
        name = self.__class__.__name__
        
        self.seconds_between_reads = self._config["seconds_between_reads"]

        if self._config["read_ramptrol"] == True:
            self.ramptrol_csv_filename = metadata['directory'] + "/ramptrol_temperature_data.csv"
            self._create_data_file(self.ramptrol_csv_filename, ['RAMP_TEMP','RAMP_SETPOINT'])
            ramptrol_port = PlaceConfig().get_config_value(name, "ramptrol_port")
            r_thread = threading.Thread(target=self._ramptrol_loop, args=(ramptrol_port,), daemon=True)
            r_thread.start()

        if self._config["read_omega"] == True:
            self.omega_csv_filename = metadata['directory'] + "/omega_temperature_data.csv"
            self._create_data_file(self.omega_csv_filename, ['IR_TEMP','K_TEMP'])
            omega_port = PlaceConfig().get_config_value(name, "omega_port")
            o_thread = threading.Thread(target=self._read_omega_loop, args=(omega_port,), daemon=True)
            o_thread.start()
            
        if self._config["change_setpoint"]:
            self.fixed_wait_time = self._config["fixed_wait_time"]
            self.temp_tolerance = self._config["equ_temp_tol"]
            self.stability_time = self._config["stability_time"]
            if not self._config["set_on_last"]:
                self.last_set = total_updates - 1
            else:
                self.last_set = total_updates

        time.sleep(2)


    def update(self, update_number, progress):
        """Update the temperature values.

        For reading the temperature, this simply transfers the
        latest data from the files into the PLACE data npy files and
        updates the plot.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :param progress: A blank dictionary for sending data back to the frontend
        :type progress: dict

        :returns: an array containing the temperature values
        :rtype: numpy.array dtype='uint64'
        """
        field = '{}-temperature'.format(self.__class__.__name__)

        current_temps = []
        if self._config["read_ramptrol"] == True:
            r_temps = pandas.read_csv(self.ramptrol_csv_filename)
            r_temps = r_temps.to_numpy()
            current_temps.append([r_temps[-1]])
            self._all_r_temps.append(r_temps[-1][1:])
            if self._config["plot"]:
                self._draw_plot(self._all_r_temps, update_number, "RampTrol Temperature", 
                                ["Actual Temp", "Setpoint"], ["red","blue"], ["circle","circle"])

        if self._config["read_omega"] == True:
            o_temps = pandas.read_csv(self.omega_csv_filename)
            o_temps = o_temps.to_numpy()
            current_temps.append([o_temps[-1]])
            self._all_o_temps.append(o_temps[-1][1:])
            if self._config["plot"]:
                self._draw_plot(self._all_o_temps, update_number, "Omega Temperature", 
                                ["IR Temp", "TC Temp"], ["green","purple"], ["square","square"])

        if self._config["change_setpoint"] and update_number < self.last_set:
            t_profile = pandas.read_csv(self._config['temp_profile_csv'],names=['temps'])
            t_profile = t_profile.to_numpy()[:,0]
            self.new_setpoint = t_profile[update_number]
            self._change_setpoint = True
            while self._change_setpoint:
                time.sleep(0.5)
                if self.new_setpoint < 0.0:
                    raise Exception
            
            print("Waiting for {} hours".format(self.fixed_wait_time))
            time.sleep(self.fixed_wait_time*3600)

            print("Checking for temperature stability")
            num_to_check = int((self.stability_time * 60) / self.seconds_between_reads)
            stability_reached, manual_override = False, 0
            override_file = place.__file__
            override_file = override_file[:override_file.rfind("/")] + "/plugins/temperature_control/manual_override.txt"
            while not stability_reached and not manual_override:
                o_temps = pandas.read_csv(self.omega_csv_filename)
                o_temps = o_temps.to_numpy()
                vals_to_check = o_temps[-num_to_check:]
                if np.std(vals_to_check) < self.temp_tolerance:
                    stability_reached = True
                time.sleep(self.seconds_between_reads*6)
                with open(override_file, 'r') as f:
                    manual_override = int(f.read())
                    print("Temperature loop manual override")
            print("Temperature stability reached")

        current_temps = np.array(current_temps)
        data = np.array([(current_temps,)], dtype=[(field, 'f8', current_temps.shape)])

        return data

    def cleanup(self, abort=False):
        """Stop and cleanup.

        :param abort: ``True`` if the experiement is being aborted, in which
                      case plotting should not occur
        :type abort: bool
        """
        self._run_threads = False

    def serial_port_query(self, serial_port, field_name):
        """Query if the instrument is connected to serial_port.

        :param serial_port: the serial port to query
        :type metadata: string

        :returns: whether or not serial_port is the correct port
        :rtype: bool
        """
        
        if field_name == "ramptrol_port":
            try:
                for i in range(2):
                    tc = watlow.TemperatureController(serial_port)
                    ramp_temp = tc.get()
                    tc.close()
                    if ramp_temp['actual'] != None:
                        break
                else:
                    return False
                return True
            except (OSError, serial.SerialException, serial.SerialTimeoutException):
                return False

        elif field_name == "omega_port":
            try:
                with serial.Serial(port=serial_port,baudrate=19200,
                                    bytesize=8,stopbits = serial.STOPBITS_ONE,
                                    parity = serial.PARITY_NONE,timeout=0.5) as omega:
                    omega.flushInput()
                    data = omega.read(11)
                if len(data) == 11 and data[0]==2 and data[10]==3:
                    # This condition isn't very good, but it's the best we can do.
                    return True
                else:
                    return False
            except (OSError, serial.SerialException, serial.SerialTimeoutException):
                return False
            
            

    #######  Private methods ########

    def _ramptrol_loop(self, ramptrol_port):
        """Read and set the temperature on the Ramptrol"""

        # Initial check of connection
        try:
            tc = watlow.TemperatureController(ramptrol_port)
            ramp_temp = tc.get()['actual']  # Read GlasCol
            ramp_setpoint = tc.get()['setpoint']  # Read GlasCol
            tc.close()
        except:
            print("PlaceScan Temperature Control: Cannot connect to/read Ramptrol controller.")
            raise

        try:
            while self._run_threads:
                try:
                    tc = watlow.TemperatureController(ramptrol_port)
                    ramp_temp = tc.get()['actual']  # Read GlasCol
                    ramp_setpoint = tc.get()['setpoint']  # Read GlasCol
                    tc.close()

                    self._write_to_file(self.ramptrol_csv_filename, time.time(), ['RAMP_TEMP','RAMP_SETPOINT'], [ramp_temp,ramp_setpoint])
                    time.sleep(self.seconds_between_reads)

                except IOError:
                    time.sleep(1)

                if self._change_setpoint:
                    actual_new_sp, i = -300.0, 0
                    while (abs(actual_new_sp - self.new_setpoint) > 0.1) and i < 10:
                        try:
                            if 0.0 < self.new_setpoint < 200.1:
                                tc = watlow.TemperatureController(ramptrol_port)
                                tc.set(self.new_setpoint)
                                time.sleep(1)
                                actual_new_sp = tc.get()['setpoint']
                                tc.close()
                            else:
                                self.new_setpoint = -300.0
                        except (OSError, IOError):
                            time.sleep(1)
                        i += 1
                    if i > 10:
                        print("Could not set ramptrol setpoint.")
                        self.new_setpoint = -300.0  
                        raise Exception 
                    self._change_setpoint = False

        finally:
            try:
                tc.close()
            except:
                pass

    def _read_omega_loop(self, omega_port):
        """Read the Omega Infrared thermometer"""

        # Initial check of connection
        try:
            omega = serial.Serial(port=omega_port,baudrate=19200,bytesize=8,stopbits = serial.STOPBITS_ONE, parity = serial.PARITY_NONE,timeout=5)
            omega.flushInput()
            data = omega.read(11)
            omega.close()
        except:
            print("PlaceScan Temperature Control: Cannot connect to/read Omega thermometer.")
            raise

        try:
            while self._run_threads:
                try:
                    # Read Omega
                    omega = serial.Serial(port=omega_port,baudrate=19200,bytesize=8,stopbits = serial.STOPBITS_ONE, parity = serial.PARITY_NONE,timeout=5)
                    omega.flushInput()
                    data = omega.read(11)
                    omega.close()

                    if len(data) > 0:
                        ir_high_byte = data[1]
                        ir_low_byte = data[2]
                        ir_temp = (ir_low_byte | (ir_high_byte << 8)) / 10.

                        k_high_byte = data[3]
                        k_low_byte = data[4]
                        k_temp = (k_low_byte | (k_high_byte << 8)) / 10.

                    self._write_to_file(self.omega_csv_filename, time.time(), ['IR_TEMP','K_TEMP'], [ir_temp,k_temp])
                    time.sleep(self.seconds_between_reads)

                except IOError:
                    time.sleep(1)
        finally:
            try:
                omega.close()
            except:
                pass

    def _write_to_file(self, filename, time, headers, data):
        """Write some temperature data to a csv file"""

        if os.path.isfile(filename):
            with open(filename, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([time]+data)
        else:
            with open(filename, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['TIME']+headers)
                writer.writerow([time]+data)       

    def _create_data_file(self, filename, headers):
        """Set up the data files"""

        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['TIME']+headers)               

    def _draw_plot(self, data, update_number, title, labels, colors, symbols):
        """Draw a plot of the temperature"""

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
