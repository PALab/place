"""Driver module for Zurich Instruments MFLI lock-in amplifier. 
The instrument has much greater functionality than what is included 
here. More functionality can be added to the driver as needed"""


import time
import numpy as np

import zhinst.utils
import zhinst.ziPython as zi

class MFLIDriver:
    """Class for low-level access to the MFLI settings.
    
    :param device_name: The name of the MFLI device (e.g. "dev4050")
    :type device_name: str

    :param ip_address: The IP address of the instrument
    :type ip_address: str

    :param port: The port for the instrument (default 8004)
    :type port: int
    """

    def __init__(self, device_name, ip_address, port=8004):
        api_level = 6
        self.device_name = device_name
        print(ip_address, port)
        self.daq_server = zi.ziDAQServer(ip_address, port, api_level)
        self.data_acq = self.daq_server.dataAcquisitionModule()
        self.channel_paths = []

        # Create a clean configuration
        zhinst.utils.disable_everything(self.daq_server, self.device_name)


    def configure_demod(self, parameters, values, demod_index=0):
        """
        Configure one or more of the demodulator settings. The demodulator is the 
        primary instrument of the lock-in amplifier.

        :param parameters: The parameter(s) to be configured. Can be a string or list of strings.
            Valid options are (See Device Node Tree for details):
            
             ['adcselect','bypass','enable','harmonic','order','oscselect',
              'phaseshift','rate','sinc','timeconstant','trigger']

        :type parameters: object

        :param values: The values for configuring the parameters. Can be a single value or a list.
        :type values: str or list

        :param demod_index: The index of the demodulator to address. Either 0 or 1.
        :type demod_index: int
        """

        if not (isinstance(parameters, list) or isinstance(parameters, tuple)):
            parameters = [parameters]
            values = [values]

        if len(parameters) != len(values):
            raise ValueError("Number of values does not match number of parameters.")

        paths_list = ["/{0}/demods/{1}/{2}".format(self.device_name, demod_index, param) for param in parameters]
        set_list = [[paths_list[i],values[i]] for i in range(len(paths_list))]

        self.daq_server.set(set_list)

    def get_demod_parameter(self, parameter, demod_index=0):
        """
        Get the value of a parameter from the demodulator

        :param parameter: The parameter to query the value for.
            Valid options are (See Device Node Tree for details):
            
             ['adcselect','bypass','enable','freq','harmonic','order','oscselect',
              'phaseadjust','phaseshift','rate','sinc','timeconstant','trigger']

        :type parameter: str

        :param demod_index: The index of the demodulator to address. Either 0 or 1.
        :type demod_index: int

        :returns: The value of the parameter
        :rtype: object
        """        

        path = "/{0}/demods/{1}/{2}".format(self.device_name, demod_index, parameter) 
        return self._get_value(path)

    def configure_reference(self, parameters, values, demod_index=0):
        """
        Configure the external reference signal for the demodulator.

        :param parameters: The parameter(s) to be configured. Only two parameters can
            be set for the extrefs: 'automode' and enable'. parameters can be one or
            both (as a list) of these.
        :type parameters: str or list

        :param values: The values for configuring the parameters. Can be a single value or a list.
        :type values: int or list

        :param demod_index: The index of the demodulator to address. Either 0 or 1. Default 0.
        :type ref_index: int
        """

        if not (isinstance(parameters, list) or isinstance(parameters, tuple)):
            parameters = [parameters]
            values = [values]

        if len(parameters) != len(values):
            raise ValueError("Number of values does not match number of parameters.")

        paths_list = ["/{0}/extrefs/{1}/{2}".format(self.device_name, demod_index, param) for param in parameters]
        set_list = [[paths_list[i],values[i]] for i in range(len(paths_list))]

        self.daq_server.set(set_list)

    def get_extref_parameter(self, parameter, demod_index=0):
        """
        Get the value of a parameter from an extref

        :param parameter: The parameter to query the value for.
            Valid options are (See Device Node Tree for details):
            
             ['adcselect','automode','demodselect','enable','locked','oscselect']

        :type parameter: str

        :param demod_index: The index of the demodulator to address. Either 0 or 1. Default 0.
        :type demod_index: int

        :returns: The value of the parameter
        :rtype: object
        """        

        path = "/{0}/extrefs/{1}/{2}".format(self.device_name, demod_index, parameter) 
        return self._get_value(path)

    def configure_voltage_input(self, parameters, values):
        """
        Configure the voltage signal input channel.

        :param parameters: The parameter(s) to be configured. Can be a string or list of strings.
            Valid options are (See Device Node Tree for details):
            
             ['ac','autorange','diff','float','imp50','on','range','scaling']

        :type parameters: str or list

        :param values: The values for configuring the parameters. Can be a single value or a list.
        :type values: object
        """

        if not (isinstance(parameters, list) or isinstance(parameters, tuple)):
            parameters = [parameters]
            values = [values]

        if len(parameters) != len(values):
            raise ValueError("Number of values does not match number of parameters.")

        paths_list = ["/{0}/sigins/0/{1}".format(self.device_name, param) for param in parameters]
        set_list = [[paths_list[i],values[i]] for i in range(len(paths_list))]

        self.daq_server.set(set_list)

    def get_voltage_input_param(self, parameter):
        """
        Get the value of a parameter from an extref

        :param parameter: The parameter to query the value for.
            Valid options are (See Device Node Tree for details):
            
             ['ac','autorange','diff','float','imp50','max','min','on','range','scaling']

        :type parameter: str

        :returns: The value of the parameter
        :rtype: object
        """        

        path = "/{0}/sigins/0/{1}".format(self.device_name, parameter) 
        return self._get_value(path)

    def configure_acquisition(self, channel_names, channel_indices, mode='exact', sampling_rate=1e6,
                             number_of_samples=100, duration=1., count=1, trig_source='trigin_1', trig_type='edge', 
                             demod_trigger_index=0, trig_edge='rising', trig_level=1.0, endless=False):
        """
        Configure the data acquisition on the MFLI. This is a wrapper
        for the DataAcquisition class that makes configuring the module
        easier. 

        :param channel_names: The channel(s) to acquire data for. Valid options are:
            
            ['demod_r','demod_x','demod_y','demod_theta','demod_freq','demod_trigin','auxin']

        :type channel_names: str or list of strings

        :param channel_indices: The index(es) of the demodulator or auxin to record on.
            If channel_names is a list, channel_indices must be a list of equivalent length.
        :type channel_indices: str or list of strings

        :param mode: Specify how the data is resampled onto the acquisition grid.
            Can be 'exact' (default), 'nearest', or 'linear'. 'exact' does not 
            resample the data, but uses the highest sampling rate of the subscribed
            signals (the number of samples is determined from the sampling rate and 
            duration). 'nearest' uses nearest-sample interpolation onto the grid.
            'linear' uses a linear interpolation of the samples to fit the grid.
        :type mode: str

        :param sampling_rate: The sampling rate of the data in Hz. This only applies when 
            mode is 'nearest' or 'linear'. When mode is 'exact', the sampling rate of
            the data is determined by the sampling rate of the input channel.
        :type sampling_rate: float

        :param number_of_samples: The number of samples to record after each trigger event. This
            only applies when mode is 'nearest' or 'linear'.
        :type number_of_samples: int

        :param duration: The duration of each acquisition in seconds. This only applies
            when mode is 'exact' and overrides number_of_samples.
        :type duration: float

        :param count: The number of trigger events to acquire in a single
            acquisition (default 1)
        :type count: int

        :param trig_source: The source of the acquisition trigger. Can be one of 'trigin_1',
            'trigin_2', 'auxin_1', or 'auxin_2'. If using 'trigin_1' or 'trigin_2', the 
            relevant demodulator needs to be specified using demod_trigger_index. The auxin
            options are applied directly to the auxin sample streams, not via the deomds.
        :type trig_source: str

        :param demod_trigger_index: The index of the demodulator to use when the trigger_source
            is either 'trigin_1' or 'trigin_2'. Can be either 0 or 1.
        :type demod_trigger_index: int

        :param trig_type: Specifies the type of trigger to acquire data on. Ensure the
            trigger source is compatible with the trigger type. Can be one of:

            ['continuous','edge','digital','pulse','level','hardware','pulse_tracking','count']

        :type trig_type: str

        :param trig_edge: The edge type to use for triggering. Can be 'rising',
            'falling', or 'both'
        :type trig_edge: str

        :param trig_level: The level of the trigger. This can also be 'auto', in which case
            the appropriate levels will be selected based on the trigger source.
        :type trig_level: float or str

        :param endless: Set to True to enable endless triggering. Default is False
        :type endless: bool

        """

        if not (isinstance(channel_names, list) or isinstance(channel_names, tuple)):
            channel_names = [channel_names]
            channel_indices = [channel_indices]

        if len(channel_names) != len(channel_indices):
            raise ValueError("Number of channel names does not match number of channel indices.")

        channel_paths = []
        channel_sampling_rates = []
        for i, name in enumerate(channel_names):
            if name == 'demod_r':
                channel_paths.append('/{0}/demods/{1}/sample.r'.format(self.device_name,channel_indices[i]))
                channel_sampling_rates.append(self._get_value('/{0}/demods/{1}/rate'.format(self.device_name,channel_indices[i])))
            elif name == 'demod_x':
                channel_paths.append('/{0}/demods/{1}/sample.x'.format(self.device_name,channel_indices[i]))
                channel_sampling_rates.append(self._get_value('/{0}/demods/{1}/rate'.format(self.device_name,channel_indices[i])))
            elif name == 'demod_y':
                channel_paths.append('/{0}/demods/{1}/sample.y'.format(self.device_name,channel_indices[i]))
                channel_sampling_rates.append(self._get_value('/{0}/demods/{1}/rate'.format(self.device_name,channel_indices[i])))
            elif name == 'demod_theta':
                channel_paths.append('/{0}/demods/{1}/sample.theta'.format(self.device_name,channel_indices[i]))
                channel_sampling_rates.append(self._get_value('/{0}/demods/{1}/rate'.format(self.device_name,channel_indices[i])))
            elif name == 'demod_freq':
                channel_paths.append('/{0}/demods/{1}/sample.frequency'.format(self.device_name,channel_indices[i]))
                channel_sampling_rates.append(self._get_value('/{0}/demods/{1}/rate'.format(self.device_name,channel_indices[i])))
            elif name == 'demod_trigin':
                channel_paths.append('/{0}/demods/{1}/sample.TrigIn1'.format(self.device_name,channel_indices[i]))
                channel_sampling_rates.append(self._get_value('/{0}/demods/{1}/rate'.format(self.device_name,channel_indices[i])))
            elif name == 'auxin':
                channel_paths.append('/{0}/auxins/0/sample.AuxIn{1}'.format(self.device_name,channel_indices[i]))
                channel_sampling_rates.append(15e6)

        self.data_acq.set('device', self.device_name)
        self.data_acq.set('clearhistory', 1)

        if mode == 'exact':
            self.data_acq.set('grid/mode', 4)
            sampling_rate = max(channel_sampling_rates)
            print(type(duration), sampling_rate, channel_sampling_rates)
            sample_count = int(sampling_rate * duration)
            self.data_acq.set('grid/cols', sample_count)
        else:
            if mode == 'nearest':
                self.data_acq.set('grid/mode', 1)
            elif mode == 'linear':
                self.data_acq.set('grid/mode', 2)
            duration = number_of_samples / sampling_rate
            self.data_acq.set('duration', duration)
            self.data_acq.set('grid/cols', number_of_samples)

        self.data_acq.set('duration', duration)
        self.data_acq.set('count', count)

        self.data_acq.set('type',['continuous','edge','digital','pulse','level','hardware','pulse_tracking','count'].index(trig_type))

        # This needs sorting out
        if trig_source == "auxin_1":
            self.data_acq.set('triggernode', '/{}/auxins/0/sample.AuxIn0'.format(self.device_name))
        elif trig_source == "auxin_2":
            self.data_acq.set('triggernode', '/{}/auxins/0/sample.AuxIn1'.format(self.device_name))
        elif trig_source == "trigin_1":
            self.data_acq.set('triggernode', '/{0}/demods/{1}/sample.TrigIn1'.format(self.device_name,demod_trigger_index))
        elif trig_source == "trigin_2":
            self.data_acq.set('triggernode', '/{0}/demods/{1}/sample.TrigIn2'.format(self.device_name,demod_trigger_index))
        #######################

        if trig_edge == 'rising':
            self.data_acq.set('edge', 1)
        elif trig_edge == 'falling':
            self.data_acq.set('edge', 2)
        elif trig_edge == 'both':
            self.data_acq.set('edge', 3)

        if trig_level == 'auto':
            self.data_acq.set('findlevel', 1)
        else:
            self.data_acq.set('level', trig_level)
            self.data_acq.set('hysteresis', 0.05*trig_level)

        if endless:
            self.data_acq.set('endless', 1)

        self.channel_paths = channel_paths
        print(channel_paths)

        self.data_acq.subscribe(channel_paths[0])


    def start_acquisition(self, wait=False, timeout=0):
        """
        Begin the data acquisition. The function can wait until
        the acquisition is complete, or return immediately. Note
        that configure_acquisition must be called before calling 
        this function.

        :param wait: True to wait until the acquisition is complete (default False).  
            If False, the instrument will be left in a state to record on the 
            next trigger event.
        :type wait: bool

        :param timeout: A timeout value for the acquisition (in s). 
        :type timeout: float
        """

        self.data_acq.execute()

        if wait:
            t0 = time.time()
            while (not self.data_acq.finished()) and (time.time() - t0 < timeout):
                time.sleep(0.1)

    def stop_acquisition(self):
        """
        Stop the data acquisition manually. Call start_acquisition
        to restart.
        """
        self.data_acq.finish()

    def get_data(self, wait_for_finished=True):
        """
        Return the acquired data. 
        
        :param wait_for_finished: True to wait until the current acquisition 
            is finished before collecting the data. If False and the acquisition 
            has not finished, only partial data will be returned.
        :type wait_for_finished: bool

        :returns data_list: A NumPy array of shape Nx2xJ, where N is the number 
            of channels recording data. The row for each channel contains the times 
            in the first column and the values in the second. Times are transformed 
            to seconds since the trigger. J is the number of samles per acquisition
        :rtype data_list: np.ndarray
        """

        if wait_for_finished:
            while not self.data_acq.finished():
                time.sleep(0.1)


        print("reading data:",time.time())
        data = self.data_acq.read(flat=True)

        print(data)
        data_list = []
        first_times = []
        for path in self.channel_paths:
            channel_data = data[path][0]
            channel_times = channel_data['timestamp'][0]
            channel_data = channel_data['value'][0]

            first_times.append(np.amin(channel_times))
            data_list.append(np.array([channel_times,channel_data]))
        
        # Transform times to seconds
        clockbase = float(self.daq_server.getInt('/{}/clockbase'.format(self.device_name)))
        min_time = np.amin(first_times)
        for item in data_list:
            times = item[0]
            times -= min_time
            new_times = times / clockbase
            item[0] = new_times

        return np.array(data_list)

    def disconnect(self):
        """Disconnect the MFLI"""
        self.daq_server.disconnect()

    def _get_value(self, path):
        """
        Get the value of the given path and return it
        """

        data = self.daq_server.get(path, flat=True, settingsonly=False)
        value = data[path]['value']

        if type(value) == np.ndarray and len(value) == 1:
            value = value[0]

        return value
