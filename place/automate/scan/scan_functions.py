#UPDATE PLOTTER
"""Command line options:

-h, --help      prints doc string
--n             define the base file name to save data to (data will be
                saved as 'filename.h5' in current directory).

                Default: TestScan
--n2            define the base file name to save second channel data
                to (data will be saved as 'filename.h5' in current
                directory).

                Default: TestScan2
--scan          defines type of scan.

                Options: point, 1D, 2D, dual

                Default: point

                **Note** dual is a two-dimensional scan that moves
                both stages at the same time.
--s1            defines stage for first dimension

                Options: long (1000mm linear stage),
                short (300mm linear stage),
                rot (rotation stage), or
                picox, picoy (picomotor mirrors in x- and y- direction)

                Default: long
--s2            defines stage for second dimension.

                Options: long (1000mm linear stage),
                short (300mm linear stage),
                rot (rotation stage), or
                picox, picoy (picomotor mirrors in x- and y- direction)

                Default: short
--dm            With polytec receiver, defines distance between polytec
                sensor head and scanning mirrors with picomotors (in cm).
                Otherwise, defines distance from picomotors to point of
                interest.  Necessary input for accurate picomotor scanning.

                Default: 50 cm
--sr            defines sample rate. Supply an integer with suffix,
                e.g. 100K for 10e5 samples/second or 1M for 10e6
                samples/second.

                Options ATS9440 and ATS660: 1K, 2K, 5K, 10K, 20K, 50K,
                100K, 200K, 500K, 1M, 2M, 5M, 10M, 20M, 50M, 100M, 125M

                Default: 10M (10 Megasamples/second)
--tm            defines time duration for each trace in microseconds.

                Example: --tm 400 for 400 microsecond traces

                Default: 256 microseconds

                **NOTE** number of samples will be rounded to next power
                of two to avoid scrambling data
--ch            defines oscilloscope card channel to record data.

                **NOTE** this should be "Q" for OSLDV acquisition

                Example --ch B

                Default: A
--ch2           defines oscilloscope card channel to record data.

                **NOTE** this should be "I" for OSLDV acquisition

                Example --ch2 B

                Default: B
--av            define the number of records that shall be averaged.

                Example: --av 100 to average 100 records

                Default: 64 averages
--wt            time to stall after each stage movement, in seconds.
                Use to allow residual vibrations to dissipate before
                recording traces, if necessary.

                Default: 0
--tl            trigger level in volts.

                Default: 1
--tr            input range for external trigger in volts.

                Default: 4
--cr, --cr2     input range of acquisition channel (for --ch and --ch2).

                Options ATS660: 200_MV, 400_MV, 800_MV, 2_V, 4_V, 8_V, 16_V

                Options ATS9440: 100_MV, 200_MV, 400_MV, 1_V, 2_V, 4_V

                Default: +/- 2V
--cp, --cp2     coupling (for --ch and --ch2) .

                Options: AC, DC

                Default: DC coupling.
--ohm, --ohm2   set impedance of oscilloscope card (for --ch and --ch2)

                Options: 50 (50 ohm impedance), 1 (1Mohm impedance)

                Default: 50 ohm
--i1            define the initial position for dimension 1 stage.
                Defined in units of corresponding stage: rotation
                stage (degrees), short and long stage, and picomotors (mm)

                Default: 0
--d1            define increment for dimension 1 stage. Defined in
                units of corresponding stage: rotation stage (degrees),
                short and long stage, and picomotors (mm).

                Default: 1

                **NOTE** the increment in the header may vary from
                the value specified for the picomotor results, because
                the motors will round to the nearest increment number
                of *steps*.  The increment in the header is **correct**.
--f1            define the final position for dimension 1 stage. Defined
                in units of corresponding stage: rotation stage
                (degrees), short and long stage, and picomotors (mm)

                Default: 0
--i2            define the initial position for dimension 2 stage.
                Defined in units of corresponding stage: rotation
                stage (degrees), short and long stage, and picomotors (mm)

                Default: 0
--d2            define increment for dimension 2 stage. Defined in
                units of corresponding stage: rotation stage (degrees),
                short and long stage, and picomotors (mm)

                Default: 1
--f2            define the final position for dimension 2 stage.
                Defined in units of corresponding stage: rotation
                stage (degrees), short and long stage, and picomotors (mm)

                Default: 0
--rv, --rv2     define which receiver to use (for --ch and --ch2).

                Options: polytec, gclad, osldv, none

                Default: none
--dd            define decoder for Polytec vibrometer.

                Options: VD-08, VD-09, DD-300 (best for ultrasonic
                applications), and DD-900

                Default: DD-300
--rg            define range of decoder of Polytec vibrometer. Specify
                both the value and unit length for the appropriate. See
                Polytec manual for possible decoders.

                Example: --rg 5mm specifies a range of 5 mm/s/V.

                Default: 5 mm/s/V
--vch           define oscilloscope card channel for polytec signal level

                Default: B
--sl            define suitable polytec signal level

                Options: floats range ~0 to 1.1

                Default: 0.90
--pp            defines serial port to to communicate with
                Polytec controller.

                Default: '/dev/ttyS0'
--bp            defines baudrate for serial communication with
                Polytec controller.

                Default: 115200
--so            define which source to use.

                Options: indi none

                Default: none

                **WARNING** If 'indi' chosen, laser will start
                automatically!!
--en            specify the energy of the source used (in mJ/cm^2).

                Default: 0 mJ/cm^2

                if --so is set to 'indi:
                    specify the percentage of maximum percentage of
                    oscillator.

                Default: 0 %
--lm            specify wavelength of the source used (in nm)

                Default: 1064
--rr            specify repetition rate of trigger (in Hz)

                Default: 10
--pl            if True will plot traces, if False, plotting is
                turned off.

                Default: True
--map           define colormap to use during scan to display image.
                Choose 'none' if you do not wish to read/plot the
                2D data.

                Options: built-in matplotlib colormaps

                Example: --map 'jet' to use jet colormap

                Default: 'gray'

                **NOTE** for large datasets, 'none' is recommended,
                as it adds significant time to the scan to read and
                plot the full data set.
--comments      add any extra comments to be added to the trace headers

                Example: --comments='Energy at 50.  Phantom with
                no tube.'

                **NOTE** you must have either '  ' or "  " surrounding
                comments

@author: Jami L Johnson, Evan Rust
March 19 2015
"""
from __future__ import print_function

import re
from math import ceil, log
from time import sleep, time
import numpy as np
from obspy.core.trace import Stats
from obspy import read, Trace, UTCDateTime
import matplotlib.pyplot as plt
import scipy.signal as sig

# place modules
from ...alazartech import atsapi as ats
from ..osci_card import controller as card
from ..osci_card.tc_controller import TriggeredContinuousController
from ..new_focus.picomotor import PMot
from ..polytec.vibrometer import Polytec
from ..xps_control.XPS_C8_drivers import XPS
from ..quanta_ray.QRay_driver import QuantaRay

class Initialize:
    """A (mostly static) class for initializing a scan."""
    def options(self, opts):
        """Parse command line options and save in par dictionary

        :param opts: attribute/value pairs for the scan
        :type opts: list

        :returns: a dictionary of attribute/value pairs
        :rtype: dict
        """
        # Defaults:
        filename = 'TestScan.h5'
        filename2 = 'TestScan.h5'
        scan = 'point'
        group_name_1 = 'LONG_STAGE'
        group_name_2 = 'SHORT_STAGE'
        mirror_dist = 50
        sample_rate = 'SAMPLE_RATE_10MSPS'
        duration = 256.0
        channel_1 = 'CHANNEL_A'
        channel_2 = 'null'
        averaged_records = 64
        wait_time = 0.0
        trig_level = 1.0
        trig_range = 4.0
        channel_range_1 = 'INPUT_RANGE_PM_2_V'
        ac_coupling_1 = False
        ohms = 50
        channel_range_2 = 'INPUT_RANGE_PM_2_V'
        ac_coupling_2 = False
        ohms2 = 50
        initial_1 = 0.0
        delta_1 = 1.0
        final_1 = 0.0
        initial_2 = 0.0
        delta_2 = 1.0
        final_2 = 0.0
        receiver_1 = 'none'
        receiver_2 = 'none'
        ret = 'True'
        source = 'none'
        decoder = 'DD-300'
        drange = '5mm'
        vib_channel = 'null'
        sig_level = 0.90
        port_polytec = '/dev/ttyS0'
        baud_polytec = 115200
        energy = '0 %'
        map_color = 'gray'
        plotter = True
        comments = ''
        wavelength = 1064
        reprate = 10.0

#unused        unit = 'mm'
#unused        positioner = 'Pos'
#unused        max_freq = '6MHz'
#unused        min_freq = '0MHz'
#unused        calib = 1
#unused        calibUnit = 'null'
#unused        instruments = []

        parameters = {}

        for option, argument in opts:
            if option in ('-h', '--help'):
                print(__doc__)
                return
            if option in "--n":
                filename = argument + '.h5'
            if option in "--n2":
                filename2 = argument + '.h5'
            if option in '--scan':
                scan = str(argument)
            if option in '--s1':
                if argument == 'long':
                    group_name_1 = 'LONG_STAGE'
#unused                    unit = 'mm'
                elif argument == 'short':
                    group_name_1 = 'SHORT_STAGE'
#unused                    unit = 'mm'
                elif argument == 'rot':
                    group_name_1 = 'ROT_STAGE'
#unused                    unit = 'deg'
                elif argument == 'picox':
                    group_name_1 = 'PICOMOTOR-X'
#unused                    unit = 'mm'
                elif argument == 'picoy':
                    group_name_1 = 'PICOMOTOR-Y'
#unused                    unit = 'mm'
                else:
                    print('ERROR: invalid stage')
                    exit()
            if option in '--s2':
                if argument == 'long':
                    group_name_2 = 'LONG_STAGE'
#unused                    unit = 'mm'
                elif argument == 'short':
                    group_name_2 = 'SHORT_STAGE'
#unused                    unit = 'mm'
                elif argument == 'rot':
                    group_name_2 = 'ROT_STAGE'
#unused                    unit = 'deg'
                elif argument == 'picox':
                    group_name_2 = 'PICOMOTOR-X'
#unused                    unit = 'mm'
                elif argument == 'picoy':
                    group_name_2 = 'PICOMOTOR-Y'
#unused                    unit = 'mm'
                else:
                    print('ERROR: invalid stage')
                    exit()
            if option in '--dm':
                mirror_dist = float(argument)*10 # mm
            if option in '--sr':
                sample_rate = "SAMPLE_RATE_" + argument + "SPS"
            if option in '--tm':
                duration = float(argument)
            if option in '--ch':
                channel_1 = "CHANNEL_" + str(argument)
            if option in '--ch2':
                channel_2 = "CHANNEL_" + str(argument)
            if option in '--av':
                averaged_records = int(argument)
            if option in '--wt':
                wait_time = float(argument)
            if option in "--tl":
                trig_level = float(argument)
            if option in "--tr":
                trig_range = float(argument)
            if option in "--cr":
                channel_range_1 = "INPUT_RANGE_PM_" + str(argument)
            if option in "--cp":
                if argument == 'AC':
                    ac_coupling_1 = True
                elif argument == 'DC':
                    ac_coupling_1 = False
            if option in "--ohm":
                ohms = int(argument)
            if option in "--cr2":
                channel_range_2 = "INPUT_RANGE_PM_" + str(argument)
            if option in "--cp2":
                if argument == 'AC':
                    ac_coupling_2 = True
                elif argument == 'DC':
                    ac_coupling_2 = False
            if option in "--ohm2":
                ohms2 = int(argument)
            if option in "--i1":
                initial_1 = float(argument)
            if option in "--d1":
                delta_1 = float(argument)
            if option in "--f1":
                final_1 = float(argument)
            if option in "--i2":
                initial_2 = float(argument)
            if option in "--d2":
                delta_2 = float(argument)
            if option in "--f2":
                final_2 = float(argument)
            if option in '--rv':
                receiver_1 = str(argument)
            if option in '--rv2':
                receiver_2 = str(argument)
            if option in '--ret':
                ret = str(argument)
            if option in "--dd":
                decoder = argument
            if option in "--rg":
                drange = argument + '/s/V'
            if option in '--vch':
                vib_channel = "CHANNEL_" + str(argument)
            if option in '--sl':
                sig_level = float(argument)
            if option in "--pp":
                port_polytec = argument
            if option in "--bp":
                baud_polytec = argument
            if option in "--so":
                source = str(argument)
            if option in "--en":
                energy = argument + ' mJ/cm^2'
            if option in "--lm":
                wavelength = argument + 'nm'
            if option in "--rr":
                reprate = float(argument)
            if option in "--map":
                map_color = str(argument)
            if option in "--pl":
                plotter = argument
            if option in "--comments":
                comments = argument

        parameters = {
            'GROUP_NAME_1':group_name_1,
            'GROUP_NAME_2':group_name_2,
            'MIRROR_DISTANCE':mirror_dist,
            'SCAN':scan,
            'SAMPLE_RATE':sample_rate,
            'DURATION':duration,
            'CHANNEL':channel_1,
            'CHANNEL2':channel_2,
            'AVERAGES':averaged_records,
            'WAITTIME':wait_time,
            'RECEIVER':receiver_1,
            'RECEIVER2':receiver_2,
            'RETURN':ret,
            'SIGNAL_LEVEL':sig_level,
            'VIB_CHANNEL':vib_channel,
            'TRIG_LEVEL':trig_level,
            'TRIG_RANGE':trig_range,
            'CHANNEL_RANGE':channel_range_1,
            'CHANNEL_RANGE2':channel_range_2,
            'AC_COUPLING':ac_coupling_1,
            'AC_COUPLING2':ac_coupling_2,
            'IMPEDANCE':ohms,
            'IMPEDANCE2':ohms2,
            'I1':initial_1,
            'D1':delta_1,
            'F1':final_1,
            'I2':initial_2,
            'D2':delta_2,
            'F2':final_2,
            'FILENAME':filename,
            'FILENAME2':filename2,
            'DECODER':decoder,
            'DECODER_RANGE':drange,
            'MAP':map_color,
            'ENERGY':energy,
            'WAVELENGTH':wavelength,
            'REP_RATE':reprate,
            'COMMENTS':comments,
            'PORT_POLYTEC':port_polytec,
            'BAUD_POLYTEC':baud_polytec,
            'SOURCE':source,
            'PX':0,
            'PY':0,
            'PLOT':plotter
            }

        if scan == '1D':
            parameters['DIMENSIONS'] = 1
        elif scan == '2D' or scan == 'dual':
            parameters['DIMENSIONS'] = 2
        else:
            parameters['DIMENSIONS'] = 0

        return parameters

    def time(self, par):
        """Set the time the scan will take."""
        par['TRACE_TIME'] = par['AVERAGES']/par['REP_RATE']
        #timea =
        #Polytec().autofocusVibrometer(span='Small')
        if par['SCAN'] == 'point':
            par['TOTAL_TIME'] = par['TRACE_TIME']
        if par['SCAN'] == '1D' or par['SCAN'] == 'dual':
            # total traces for dimension 1
            par['TOTAL_TRACES_D1'] = ceil(abs((par['F1']-par['I1']))/par['D1'])
            par['TOTAL_TIME'] = par['TRACE_TIME']* par['TOTAL_TRACES_D1']
        if par['SCAN'] == '2D':
            # total traces for dimension 1
            par['TOTAL_TRACES_D1'] = ceil(abs((par['F1']-par['I1']))/par['D1'])
            # total traces for dimension 2
            par['TOTAL_TRACES_D2'] = ceil(abs((par['F2']-par['I2']))/par['D2'])
            par['TOTAL_TIME'] = par['TRACE_TIME']*par['TOTAL_TRACES_D1']*par['TOTAL_TRACES_D2']
        if par['SCAN'] == 'dual':
            # total traces for dimension 1
            par['TOTAL_TRACES_D1'] = ceil(abs((par['F1']-par['I1']))/par['D1'])
            # total traces for dimension 2
            par['TOTAL_TRACES_D2'] = ceil(abs((par['F2']-par['I2']))/par['D2'])
            par['TOTAL_TIME'] = par['TRACE_TIME']* par['TOTAL_TRACES_D1']
            if par['TOTAL_TRACES_D1'] != par['TOTAL_TRACES_D2']:
                print('ERROR: number of traces must be the same in both dimensions')
                exit()
        return par

    def polytec(self, par):
        """Initialize Polytec vibrometer

        Initialize Polytec vibrometer and obtain relevant settings to save in
        trace headers. Also autofocuses vibrometer.
        """
        # open connection to vibrometer
        poly = Polytec(par['PORT_POLYTEC'], par['BAUD_POLYTEC'])
        poly.openConnection()

        # set decoder range
        poly.setRange(par['DECODER'], par['DECODER_RANGE'])

        # determine delay due to decoder
        delay_string = poly.getDelay(par['DECODER'])
        delay = re.findall(r'[-+]?\d*\.\d+|\d+', delay_string) # get time delay in us
        time_delay = float(delay[0])

        # get maximum frequency recorded
        freq_string = poly.getMaxFreq(par['DECODER'])
        freq = re.findall(r'[-+]?\d*\.\d+|\d+', freq_string)
        del_num_f = len(freq)+2
        freq = float(freq[0])
        freq_unit = freq_string[del_num_f:].lstrip()
        freq_unit = freq_unit.rstrip()
        if freq_unit == 'kHz':
            multiplier = 10000
        elif freq_unit == 'MHz':
            multiplier = 10000000
        max_freq = freq * multiplier

        # get range of decoder and amplitude calibration factor
        decoder_range = poly.get_range(par['DECODER'])
        range_num = re.findall(r'[-+]?\d*\.\d+|\d+', par['DECODER_RANGE'])
        del_num_r = len(range_num)+1
        calib = float(range_num[0])
        calib_unit = decoder_range[del_num_r:].lstrip()

        par['TIME_DELAY'] = time_delay
        par['MAX_FREQ'] = max_freq
        par['CALIB'] = calib
        par['CALIB_UNIT'] = calib_unit

        # autofocus vibrometer
        poly.autofocusVibrometer()

        return par

    def osci_card(self, par):
        """Initialize Alazar Oscilloscope Card."""

        # initialize channel for signal from vibrometer decoder
        control = card.TriggeredRecordingController()
        control.configureMode = True
        control.create_input(
            par['CHANNEL'],
            par['CHANNEL_RANGE'],
            par['AC_COUPLING'],
            par['IMPEDANCE'],
            )
        control.setSampleRate(par['SAMPLE_RATE'])
        samples = control.samplesPerSec*par['DURATION']*1e-6
        samples = int(pow(2, ceil(log(samples, 2)))) # round number of samples to next power of two
        control.setSamplesPerRecord(samples=samples)
        control.setRecordsPerCapture(par['AVERAGES'])
        trigger_level = 128 + int(127*par['TRIG_LEVEL']/par['TRIG_RANGE'])

        print(trigger_level)

        control.setTrigger(
            operationType="TRIG_ENGINE_OP_J",
            #TODO: change TRIG_CHAN_A to option (ext, A-D)
            sourceOfJ='TRIG_EXTERNAL',
            levelOfJ=trigger_level,
            )
        control.setTriggerTimeout(10)
        control.configureMode = False

        # FIX THIS
        if par['CHANNEL2'] != 'null':
            control2 = card.TriggeredRecordingController()
            control2.configureMode = True
            control2.create_input(
                par['CHANNEL2'],
                par['CHANNEL_RANGE2'],
                par['AC_COUPLING2'],
                par['IMPEDANCE2'],
                )
            control2.setSampleRate(par['SAMPLE_RATE'])
#unused            samples2 = control.samplesPerSec*par['DURATION']*1e-6
            # round number of samples to next power of two
#unused            samples2 = int(pow(2, ceil(log(samples, 2))))
            control2.setSamplesPerRecord(samples=samples)
            control2.setRecordsPerCapture(par['AVERAGES'])
            trigger_level = 128 + int(127*par['TRIG_LEVEL']/par['TRIG_RANGE'])
            control2.setTrigger(
                operationType="TRIG_ENGINE_OP_J",
                #TODO: change TRIG_CHAN_A to option (ext, A-D)
                sourceOfJ='TRIG_EXTERNAL',
                levelOfJ=trigger_level
                )
            control2.setTriggerTimeout(10)
            control2.configureMode = False
            par['CONTROL2'] = control2

        if par['VIB_CHANNEL'] != 'null':
            # initialize channel for vibrometer sensor head signal
            vib_signal = TriggeredContinuousController()
            vib_signal.configureMode = True
            vib_signal.create_input(
                par['VIB_CHANNEL'],
                ats.INPUT_RANGE_PM_4_V,
                ats.DC_COUPLING,
                par['IMPEDANCE'],
                ) # 0 to 3 V DC
            vib_signal.setSamplesPerRecord(samples=1)
            vib_signal.setRecordsPerCapture(3)
            vib_signal.setTrigger(
                operationType="TRIG_ENGINE_OP_J",
                sourceOfJ='TRIG_EXTERNAL',
                levelOfJ=trigger_level,
                )
            vib_signal.setTriggerTimeout(10)

        else:
            vib_signal = 'null'

        par['SAMPLES'] = samples
        par['CONTROL'] = control
        par['VIB_SIGNAL'] = vib_signal
        print('oscilloscope card ready and parameters set')
        return par

    def controller(self, IP, par, i):
        """Initialize XPS controller and move to stage to starting scan position

        :param par: scan parameters
        :param i: scan axis (1,2,..)
        """

        xps = XPS()
        xps.GetLibraryVersion()

        socket_id = xps.TCP_ConnectToServer(IP, 5001, 3) # connect over network
        print("connected to: ", socket_id)

        controller_error = xps.ControllerStatusGet(socket_id)
        if controller_error[0] == 0:
            print('XPS controller status: ready')
        else:
            print('XPS controller status failed: ERROR =', controller_error)

        log_error = xps.Login(socket_id, "Administrator", "Administrator")
        if log_error[0] == 0:
            print('login successful')
        else:
            print('login failed: ERROR = ', log_error)

        xps.GroupKill(socket_id, par['GROUP_NAME_'+str(i)])
        initialize_group_error = xps.GroupInitialize(socket_id, par['GROUP_NAME_'+str(i)])
        if initialize_group_error[0] == 0:
            print('group initialized')
        else:
            print('group initialize failed: ERROR = ', initialize_group_error)
        xps.GroupStatusGet(socket_id, par['GROUP_NAME_'+str(i)])

        home_err = xps.GroupHomeSearch(socket_id, par['GROUP_NAME_'+str(i)])
        if home_err[0] == 0:
            print('home search successful')
        else:
            print('home search failed: ERROR = ', home_err)

        xps.GroupMoveAbsolute(socket_id, par['GROUP_NAME_'+str(i)], [par['I'+str(i)]])
#unused        ck_value = 0
        actual_pos = xps.GroupPositionCurrentGet(socket_id, par['GROUP_NAME_'+str(i)], 1)

        par['XPS_'+str(i)] = xps
        par['SOCKET_ID_'+str(i)] = socket_id
        print('XPS stage initialized')

        return par

    def picomotor_controller(self, IP, port, par):
        """Initialize Picomotor controller"""

        PMot().connect()

        print('Picomotor controller initialized')

        par['PX'] = 2
        par['PY'] = 1

        # set to high velocity
        PMot().set_VA(par['PX'], 1700)
        PMot().set_VA(par['PY'], 1700)

        # set current position to zero
        PMot().set_DH(par['PX'], 0)
        PMot().set_DH(par['PY'], 0)
        #set units to encoder counts for closed-loop
        PMot().set_SN(par['PX'], 1)
        PMot().set_SN(par['PY'], 1)
        # set following error threshold
        PMot().set_FE(par['PX'], 200)
        PMot().set_FE(par['PY'], 200)
        # set closed-loop update interval to 0.1
        PMot().set_CL(par['PX'], 0.1)
        PMot().set_CL(par['PY'], 0.1)
        # save settings to non-volatile memory
        #PMot().set_SM()
        # enable closed-loop setting
        PMot().set_MM(par['PX'], 1)
        PMot().set_MM(par['PY'], 1)

        # set Deadband
        #PMot().set_DB(10)
        # save settings to non-volatile memory
        PMot().set_SM()

        print('X and Y picomotors initialized')

        return par

    def picomotor(self, motor_num):
        """Initialize PicoMotor"""
        motor = PMot(motor_num)

        print('PicoMotor initialized')

        return motor

    def quanta_ray(self, percent, par):
        """Starts Laser in rep-rate mode and sets watchdog time.

        :returns: the repitition rate of the laser.
        """

        # open laser connection
        QuantaRay().openConnection()
        QuantaRay().setWatchdog(time=100)
        # turn laser on
        QuantaRay().on()
        sleep(20)

        # set-up laser
        QuantaRay().set(cmd='SING') # set QuantaRay to single shot
        QuantaRay().set(cmd='NORM')
        QuantaRay().setOscPower(percent) # set power of laser
        sleep(1)

        print('Power of laser oscillator: ', QuantaRay().getOscPower())

        # get rep-rate
        rep_rate = QuantaRay().getTrigRate()
        rep_rate = re.findall(r'[-+]?\d*\.\d+|\d+', rep_rate) # get number only
        rep_rate_float = float(rep_rate[0])
        trace_time = par['AVERAGES']/rep_rate_float

        # set watchdog time > time of one trace, so laser doesn't turn off between commands
        QuantaRay().setWatchdog(time=ceil(2*trace_time))

        return trace_time

    def header(self, par):
        """Initialize generic trace header for all traces"""

        custom_header = Stats()
        if par['IMPEDANCE'] == 1:
            impedance = '1Mohm'
        else:
            impedance = '50 ohms'
        if par['IMPEDANCE2'] == 1:
            impedance2 = '1Mohm'
        else:
            impedance2 = '50 ohms'
        custom_header.impedance = impedance
        custom_header.impedance2 = impedance2
        custom_header.x_position = par['I1']
        custom_header.max_frequency = par['MAX_FREQ']
        custom_header.receiver = par['RECEIVER']
        custom_header.decoder = par['DECODER']
        custom_header.decoder_range = par['DECODER_RANGE']
        custom_header.source_energy = par['ENERGY']
        custom_header.wavelength = par['WAVELENGTH']
        custom_header.x_unit = 'mm'
        custom_header.theta_unit = 'deg'
        custom_header.y_unit = 'mm'
        custom_header.comments = par['COMMENTS']
        custom_header.averages = par['AVERAGES']
        custom_header.calib_unit = par['CALIB_UNIT']
        custom_header.time_delay = par['TIME_DELAY']
        custom_header.scan_time = ''
        custom_header.focus = 0

        header = Stats(custom_header)
        if par['RECEIVER'] == 'polytec':
            if par['DECODER'] == 'DD-300' and par['IMPEDANCE'] == 1:
                header.calib = 25
            else:
                header.calib = par['CALIB']
        header.channel = par['CHANNEL']

        return header

    def two_plot(self, group_name, header):
        plt.ion()
        plt.show()
        fig = plt.figure()
        axis_1 = fig.add_subplot(211)
        if header.calib_unit.rstrip() == 'nm/V':
            axis_1.set_ylabel('Displacement (nm)')
        elif header.calib_unit.rstrip() == 'mm/s/V':
            axis_1.set_ylabel('Particle Velocity (mm/s)')
        axis_1.set_xlabel(r'Time ($\mu$s)')
        axis_1.set_title('Last Trace Acquired')
        axis_2 = fig.add_subplot(212)
        if group_name in ['LONG_STAGE', 'SHORT_STAGE', 'PICOMOTOR-X', 'PICOMOTOR-Y']:
            axis_2.set_ylabel('Scan Location ('+ header.x_unit + ')')
        elif group_name == 'ROT_STAGE':
            axis_2.set_ylabel('Scan Location ('+ header.theta_unit + ')')
        axis_2.set_xlabel(r'Time ($\mu$s)')

        return axis_1, axis_2, fig

class Execute:
    def get_times(self, control, channel, header):
        times = control.getTimesOfRecord()
        dt_value = times[1]-times[0]
        header.delta = dt_value
        return times, header

    def butter_lowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        return sig.butter(order, normal_cutoff, btype='low', analog=False)

    def butter_lowpass_filter(self, data, fs_value):
        cutoff = np.array(5e6)
        order = 2
        b_value, a_value = Execute().butter_lowpass(cutoff, fs_value, order=order)
        return sig.filtfilt(b_value, a_value, data)

    def butter_bandpass(self, wn_value, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff_low = wn_value[0] / nyq
        normal_cutoff_high = wn_value[1] / nyq
        return sig.butter(
            order,
            [normal_cutoff_low, normal_cutoff_high],
            btype='band',
            analog=False,
            )

    def butter_bandpass_filter(self, data, freqs, carrier):
        wn_value = np.array([carrier - 5*10**6, carrier + 5*10**6])
        order = 2
        b_value, a_value = Execute().butter_bandpass(wn_value, freqs, order)
        return sig.filtfilt(b_value, a_value, data)

    def osldv_process(self, records, records2, par):
        """Function for processing I & Q from OSLDV receiver"""
        print('begin processing...')
        fd_value = 2/(1550*1e-9)

        for index in range(0, len(records)):
            time1 = time()
            sample_rate = par['CONTROL'].samplesPerSec
            q_value = Execute().butter_lowpass_filter(records[index], sample_rate)
            i_value = Execute().butter_lowpass_filter(records2[index], sample_rate)

            # MEASURE FREQUENCY FROM Q & I
            vfm = np.array(
                (i_value[0:-1]*np.diff(q_value) - q_value[0:-1]*np.diff(i_value))
                / (i_value[0:-1]**2 + q_value[0:-1]**2)
                )
            end = vfm[-1]
            vfm[0] = 0.0

            # FREQUENCY TO mm/s
            vfm = sample_rate*np.concatenate((vfm, [end]))/(2*np.pi*fd_value)*1000

            records[index] = (vfm)

        return records


    def data_capture(self, par):
        """Capture data for up to two channels, and OSLDV pre-averaging
        processing
        """
        par['CONTROL'].start_capture()
        par['CONTROL'].readData()

        if par['RECEIVER'] == 'osldv':
            par['CONTROL2'].start_capture()
            par['CONTROL2'].readData()

            # get I & Q
            records = par['CONTROL'].getDataRecordWise(par['CHANNEL'])
            records2 = par['CONTROL2'].getDataRecordWise(par['CHANNEL2'])
            par['CONTROL'].endCapture()

            # calculate partical velocity from I & Q
            records = Execute().osldv_process(records, records2, par)

            average = np.average(records, 0)
            average2 = []

        else:
            # two channel acquisition
            if par['CHANNEL2'] != 'null':
                par['CONTROL2'].start_capture()
                par['CONTROL2'].readData()

            # record channel 1
            records = par['CONTROL'].getDataRecordWise(par['CHANNEL'])
            average = np.average(records, 0)

            if par['CHANNEL2'] != 'null':
                # record channel 2
                records2 = par['CONTROL2'].getDataRecordWise(par['CHANNEL2'])
                average2 = np.average(records2, 0)
            else:
                average2 = []

        return average, average2

    def update_header(self, header, x_value, group_name=''):
        header.starttime = UTCDateTime()
        if group_name in ['LONG_STAGE', 'PICOMOTOR-X']:
            header.x_position = x_value
        elif group_name == 'ROT_STAGE':
            header.theta_position = x_value
        elif group_name in ['SHORT_STAGE', 'PICOMOTOR-Y']:
            header.y_position = x_value
        else:
            header.x_position = x_value

    def move_stage(self, group_name, xps, socket_id, x_value):
        if group_name in ['LONG_STAGE', 'SHORT_STAGE', 'ROT_STAGE']:
            xps.GroupMoveAbsolute(socket_id, group_name, [x_value])
            actual_pos = xps.GroupPositionCurrentGet(socket_id, group_name, 1)
            return actual_pos[1]

    def save_trace(self, header, average, filename):
        header.npts = len(average)
        trace = Trace(data=average, header=header)
        trace.write(filename, 'H5', mode='a')
        return

    def update_time(self, par):
        """calculate time remaining"""
        par['TOTAL_TIME'] -= par['TRACE_TIME']
        hour_left = int(par['TOTAL_TIME']/3600)
        less_hour = par['TOTAL_TIME']- hour_left*3600
        min_left = int(less_hour/60)
        sec_left = int(less_hour - min_left*60)
        print(str(hour_left) + ':' + str(min_left) + ':' + str(sec_left) + ' remaining')
        return par

    def check_vibfocus(self, channel, vibSignal, sigLevel):
        """Check vibrometer and focus

        Checks focus of vibrometer sensor head and autofocuses if less
        then sigLevel specified (0 to ~1.1)

        :param channel: channel "signal" from polytec controller is
                        connected to on oscilloscope card
        """

        vibSignal.start_capture()
        vibSignal.readData(channel)
        signal = vibSignal.getDataRecordWise(channel)
        signal = np.average(signal, 0)

        k = 0
        while signal < sigLevel:
            print('sub-optimal focus:')
            if k == 0:
                Polytec().autofocusVibrometer(span='Small')
            elif k == 1:
                Polytec().autofocusVibrometer(span='Medium')
            else:
                Polytec().autofocusVibrometer(span='Full')
                vibSignal.start_capture()
                vibSignal.readData()
                signal = vibSignal.getDataRecordWise(channel)
                signal = np.average(signal, 0)
            k += 1
            if k > 3:
                print('unable to obtain optimum signal')
                break

            return signal

    def plot(self, header, times, average, par):
        """ plot trace """
        plt.plot(times*1e6, average*header.calib)
        plt.xlim((0, max(times)*1e6))
        if header.calib_unit.rstrip() == 'nm/V':
            plt.ylabel('Displacement (nm)')
        elif header.calib_unit.rstrip() == 'mm/s/V':
            plt.ylabel('Particle Velocity (mm/s)')
        plt.xlabel('Time (us)')

    def update_two_plot(self, times, average, x_value, par, header, fig, axis_1, axis_2):
        """Plot single trace and cumulative wavefield"""
        plt_data = read(par['FILENAME'], 'H5', calib=True)

        if par['GROUP_NAME_1'] in ['LONG_STAGE', 'SHORT_STAGE', 'PICOMOTOR-X', 'PICOMOTOR-Y']:
            plt_data.sort(keys=['x_position'])
            axis_2.set_ylabel('Scan Location ('+ header.x_unit + ')')
        elif par['GROUP_NAME_1'] == 'ROT_STAGE':
            plt_data.sort(keys=['theta_position'])
            axis_2.set_ylabel('Scan Location ('+ header.theta_unit + ')')

        axis_1.cla()
        axis_2.cla()
        axis_1.plot(times*1e6, average*header.calib)
        axis_1.set_xlim((0, max(times)*1e6))
        axis_2.imshow(
            plt_data,
            extent=[0, max(times)*1e6, x_value, par['I1']],
            cmap=par['MAP'],
            aspect='auto',
            )
        axis_1.set_xlabel('Time (us)')

        if header.calib_unit.rstrip() == 'nm/V':
            axis_1.set_ylabel('Displacement (nm)')
        elif header.calib_unit.rstrip() == 'mm/s/V':
            axis_1.set_ylabel('Particle Velocity (mm/s)')

        axis_2.set_xlabel('Time (us)')
        axis_1.set_xlim((0, max(times)*1e6))
        fig.canvas.draw()

    def close(self, instruments, par):
        for device in instruments:
            if device == 'POLYTEC':
                Polytec().closeConnection()
            if device == 'INDI':
                QuantaRay().set(cmd='SING') # trn laser to single shot
                QuantaRay().off()
                QuantaRay().closeConnection()
            if device in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
                PMot().close()
            if par['DIMENSIONS'] == 1 and device in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']:
                par['XPS_1'].TCP__CloseSocket(par['SOCKET_ID_1'])
                print('Connection to %s closed'%par['GROUP_NAME_1'])
            if par['DIMENSIONS'] == 2 and device in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']:
                par['XPS_2'].TCP__CloseSocket(par['SOCKET_ID_2'])
                print('Connection to %s closed'%par['GROUP_NAME_2'])

class Scan:
    def point(self, par, header):
        """Record a single trace"""

        print('recording trace...')

        times, header = Execute().get_times(par['CONTROL'], par['CHANNEL'], header)

        Execute().update_header(header, par['I1'])

        if par['SOURCE'] == 'indi':
            laser_check = input('Turn laser on REP? (yes/N) \n')
            if laser_check == 'yes':
                QuantaRay().set('REP')
                sleep(1)
                QuantaRay().getStatus() # keep watchdog happy
            else:
                print('Turning laser off ...')
                QuantaRay().off()
                QuantaRay().closeConnection()
                # add code to close connection to instruments
                exit()

        # capture data
        average, average2 = Execute().data_capture(par)

        if par['PLOT'] is True:
            Execute().plot(header, times, average, par)
            if par['CHANNEL2'] != 'null' and par['RECEIVER'] != 'osldv':
                Execute().plot(header, times, average2, par)
            plt.show()

        # save data
        Execute().save_trace(header, average, par['FILENAME'])

        if par['CHANNEL2'] != 'null' and par['RECEIVER'] != 'osldv':
            Execute().save_trace(header, average2, par['FILENAME2'])

        if par['SOURCE'] == 'indi':
            QuantaRay().set('SING')
            QuantaRay().off()

        print('Trace recorded!')
        print('data saved as: %s \n '%par['FILENAME'])

    def oneD(self, par, header):
        """Scanning function for 1-stage scanning"""

        #QSW().set(cmd='REP') # turn laser on repetitive shots
        #QRstatus().getStatus() # send command to laser to keep watchdog happy

        print('beginning 1D scan...')

        times, header = Execute().get_times(par['CONTROL'], par['CHANNEL'], header)

        if par['SOURCE'] == 'indi':
            laser_check = input('Turn laser on REP? (yes/N) \n')
            if laser_check == 'yes':
                QuantaRay().set('REP')
                sleep(1)
                QuantaRay().getStatus() # keep watchdog happy
            else:
                print('Turning laser off ...')
                QuantaRay().off()
                QuantaRay().closeConnection()
                # add code to close connection to instruments

        tracenum = 0
        if par['I1'] > par['F1']:
            par['D1'] = -par['D1']

        x_value = par['I1']

#unused        total_time = par['TOTAL_TIME']

        if par['GROUP_NAME_1'] == 'ROT_STAGE':
            pos = par['I1']
            unit = 'degrees'

        # set up mirrors
        elif par['GROUP_NAME_1'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            theta_step = 1.8e-6 # 1 step = 1.8 urad
            print('Go to starting position for picomotors')
            PMot().Position(par['PX'], par['PY'])
            # set position to 'zero'
            PMot().set_DH(par['PX'])
            PMot().set_DH(par['PY'])
            if par['RECEIVER'] == 'polytec' or par['RECEIVER2'] == 'polytec':
                Polytec().autofocusVibrometer(span='Full')
                l_value = par['MIRROR_DISTANCE']
                unit = 'mm'
            else:
                l_value = par['MIRROR_DISTANCE']
                unit = 'radians'
            par['I1'] = float(par['I1'])/(l_value*theta_step)
            par['D1'] = float(par['D1'])/(l_value*theta_step)
            print('group name 1 %s' %par['GROUP_NAME_1'])
            if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
                PMot().move_rel(par['PX'], par['I1'])
            else:
                PMot().move_rel(par['PY'], par['I1'])
        else:
            unit = 'mm'

        # setup plot
        axis_1, axis_2, fig = Initialize().two_plot(par['GROUP_NAME_1'], header)
        i = 0

        while i < par['TOTAL_TRACES_D1']:
            if par['SOURCE'] == 'indi':
                QuantaRay().getStatus() # keep watchdog happy
            tracenum += 1
            print('trace ', tracenum, ' of', par['TOTAL_TRACES_D1'])

            # move stage/mirror
            if par['GROUP_NAME_1'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
#unused                x_steps = x_value/theta_step
                if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
                    PMot().move_rel(par['PX'], par['D1'])
                    pos = float(PMot().get_TP(par['PX']))*l_value*theta_step
                elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
                    PMot().move_rel(par['PY'], par['D1'])
                    pos = float(PMot().get_TP(par['PY']))*l_value*theta_step
            else:
                Execute().move_stage(
                    par['GROUP_NAME_1'],
                    par['XPS_1'],
                    par['SOCKET_ID_1'],
                    x_value
                    )
                pos = x_value

            Execute().update_header(header, pos, par['GROUP_NAME_1'])
            print('position = {} {}'.format(pos, unit))
            sleep(par['WAITTIME']) # delay after stage movement

            #Execute().check_vibfocus(par['CHANNEL'],par['VIB_SIGNAL'],par['SIGNAL_LEVEL'])

            average, average2 = Execute().data_capture(par)

            # save current trace
            Execute().save_trace(header, average, par['FILENAME'])

            if par['CHANNEL2'] != 'null' and par['RECEIVER'] != 'osldv':
                Execute().save_trace(header, average2, par['FILENAME2'])

            # update figure
            if par['MAP'] != 'none' and i > 0:
                Execute().update_two_plot(times, average, x_value, par, header, fig, axis_1, axis_2)

            Execute().update_time(par)

            x_value += par['D1']
            i += 1

            #QRstatus().getStatus() # send command to laser to keep watchdog happy

            if par['RETURN'] == 'True':
                if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
                    PMot().move_abs(par['PX'], 0)
                    print('picomotors moved back to zero.')
                elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
                    PMot().move_abs(par['PY'], 0)
                    print('picomotors moved back to zero.')

        if par['SOURCE'] == 'indi':
            QuantaRay().set('SING')
            QuantaRay().off()
        print('scan complete!')
        print('data saved as: %s \n'%par['FILENAME'])

    def twoD(self, par, header):
        """Scanning function for 2-stage scanning."""

        print('beginning 2D scan...')

        _, header = Execute().get_times(par['CONTROL'], par['CHANNEL'], header)

        if par['SOURCE'] == 'indi':
            laser_check = input('Turn laser on REP? (yes/N) \n')
            if laser_check == 'yes':
                QuantaRay().set('REP')
                sleep(1)
                QuantaRay().getStatus() # keep watchdog happy
            else:
                print('Turning laser off ...')
                QuantaRay().off()
                QuantaRay().closeConnection()
                # add code to close connection to instruments
        tracenum = 0

        if par['I1'] > par['F1']:
            par['D1'] = -par['D1']
        x_value = par['I1']

        if par['I2'] > par['F2']:
            par['D2'] = -par['D2']
        y_value = par['I2']

#unused        total_time = par['TOTAL_TIME']

        # set up mirrors
        if (par['GROUP_NAME_1'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']
                or par['GROUP_NAME_2'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']):
            theta_step = 2.265e-6 # 1 step or count = 26 urad
            print('Go to starting position for picomotors')
            PMot().Position(par['PX'], par['PY'])
            print('done moving')
            # set current position to zero/home
            PMot().set_DH(par['PX'])
            PMot().set_DH(par['PY'])

        if par['GROUP_NAME_1'] == 'ROT_STAGE':
            unit1 = 'degrees'
        elif par['GROUP_NAME_1'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            if par['RECEIVER'] == 'polytec':
                Polytec().autofocusVibrometer(span='Full')
                l_value = par['MIRROR_DISTANCE']
                unit1 = 'mm'
            else:
                l_value = par['MIRROR_DISTANCE']
                unit1 = 'radians'
            pos1 = 0
            par['I1'] = par['I1']/(l_value*theta_step)
            par['D1'] = par['D1']/(l_value*theta_step)

        else:
            unit1 = 'mm'

        if par['GROUP_NAME_2'] == 'ROT_STAGE':
            unit2 = 'degrees'
        elif par['GROUP_NAME_2'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            if par['RECEIVER'] == 'polytec':
                Polytec().autofocusVibrometer(span='Full')
                l_value = par['MIRROR_DISTANCE']
                unit2 = 'mm'
            else:
                l_value = par['MIRROR_DISTANCE']
                unit2 = 'radians'
            pos2 = 0
            par['I2'] = par['I2']/(l_value*theta_step)
            par['D2'] = par['D2']/(l_value*theta_step)

        else:
            unit2 = 'mm'

        if par['GROUP_NAME_1'] in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']:
            pos1 = Execute().move_stage(
                par['GROUP_NAME_1'],
                par['XPS_1'],
                par['SOCKET_ID_1'],
                x_value,
                )
        if par['GROUP_NAME_2'] in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']:
            pos2 = Execute().move_stage(
                par['GROUP_NAME_2'],
                par['XPS_2'],
                par['SOCKET_ID_2'],
                y_value,
                )

        i = 0
        j = 0

        while i < par['TOTAL_TRACES_D1']:
            if par['SOURCE'] == 'indi':
                QuantaRay().getStatus() # keep watchdog happy
            print('trace {} of {}'.format(tracenum, par['TOTAL_TRACES_D1']*par['TOTAL_TRACES_D2']))

            if i > 0:
                if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
                    PMot().move_rel(par['PX'], par['D1'])
                    pos1 = float(PMot().get_TP(par['PX']))*l_value*theta_step
                elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
                    PMot().move_rel(par['PY'], par['D1'])
                    pos1 = float(PMot().get_TP(par['PY']))*l_value*theta_step
                else:
                    pos1 = Execute().move_stage(
                        par['GROUP_NAME_1'],
                        par['XPS_1'],
                        par['SOCKET_ID_1'],
                        x_value,
                        )

            Execute().update_header(header, pos1 , par['GROUP_NAME_1'])

            print('dimension 1 = %s %s ' %(pos1, unit1))

            sleep(par['WAITTIME']) # delay after stage movement
            Polytec().autofocusVibrometer(span='Small')

            while j < par['TOTAL_TRACES_D2']:

                if par['SOURCE'] == 'indi':
                    QuantaRay().getStatus() # keep watchdog happy

                tracenum += 1
                print('trace %s of %s' %(tracenum, par['TOTAL_TRACES_D1']*par['TOTAL_TRACES_D2']))

                if j > 0:
                    if par['GROUP_NAME_2'] == 'PICOMOTOR-X':
                        PMot().move_rel(par['PX'], par['D2'])
                        pos2 = float(PMot().get_TP(par['PX']))*l_value*theta_step
                    elif par['GROUP_NAME_2'] == 'PICOMOTOR-Y':
                        PMot().move_rel(par['PY'], par['D2'])
                        pos2 = float(PMot().get_TP(par['PY']))*l_value*theta_step
                    else:
                        pos2 = Execute().move_stage(
                            par['GROUP_NAME_2'],
                            par['XPS_2'],
                            par['SOCKET_ID_2'],
                            y_value,
                            )

                Execute().update_header(header, pos2, par['GROUP_NAME_2'])

                print('dimension 2 = %s %s '%(pos2, unit2))

                sleep(par['WAITTIME']) # delay after stage movement

                #Execute().check_vibfocus(par['CHANNEL'],par['VIB_SIGNAL'],par['SIGNAL_LEVEL'])
                #Polytec().autofocusVibrometer(span='Small')

                average, average2 = Execute().data_capture(par)#par['CONTROL'],par['CHANNEL'])

                # save current trace
                Execute().save_trace(header, average, par['FILENAME'])

                if par['CHANNEL2'] != 'null' and par['RECEIVER'] != 'osldv':
                    Execute().save_trace(header, average2, par['FILENAME2'])

                Execute().update_time(par)

                y_value += par['D2']
                j += 1

            x_value += par['D1']

            # move stage/mirror to starting position
            y_value = par['I2']

            if par['GROUP_NAME_2'] == 'PICOMOTOR-X':
                PMot().move_abs(par['PX'], float(y_value))
                #PMot().set_OR(par['PX'])
                pos2 = float(PMot().get_TP(par['PX']))*l_value*theta_step
            elif par['GROUP_NAME_2'] == 'PICOMOTOR-Y':
                #PMot().set_OR(par['PY'])
                PMot().move_abs(par['PY'], float(y_value))
                pos2 = float(PMot().get_TP(par['PY']))*l_value*theta_step
            else:
                pos2 = Execute().move_stage(
                    par['GROUP_NAME_2'],
                    par['XPS_2'],
                    par['SOCKET_ID_2'],
                    y_value
                    )
            j = 0
            i += 1

        if par['SOURCE'] == 'indi':
            QuantaRay().set('SING')
            QuantaRay().off()

        print('scan complete!')
        print('data saved as: {} \n'.format(par['FILENAME']))

    def dual(self, par, header):
        """Scanning function for 2-stage scanning.

        Scanning function for 2-stage scanning where both stages move at
        the same time.
        """

        print('beginning 2D scan...')

        times, header = Execute().get_times(par['CONTROL'], par['CHANNEL'], header)

        tracenum = 0

        if par['I1'] > par['F1']:
            par['D1'] = -par['D1']
        x_value = par['I1']

        if par['I2'] > par['F2']:
            par['D2'] = -par['D2']
        y_value = par['I2']

#unused        total_time = par['TOTAL_TIME']

        # set up mirrors
        if (par['GROUP_NAME_1'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']
                or par['GROUP_NAME_2'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']):
            theta_step = 2.265e-6 # 1 step or count = 26 urad
            print('Go to starting position for picomotors')
            PMot().Position(par['PX'], par['PY'])
            print('done moving')
            # set current position to zero/home
            PMot().set_DH(par['PX'])
            PMot().set_DH(par['PY'])

        if par['GROUP_NAME_1'] == 'ROT_STAGE':
            unit1 = 'degrees'
        elif par['GROUP_NAME_1'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            if par['RECEIVER'] == 'polytec':
                Polytec().autofocusVibrometer(span='Full')
                l_value = par['MIRROR_DISTANCE']
                unit1 = 'mm'
            else:
                l_value = par['MIRROR_DISTANCE']
                unit1 = 'radians'
            pos1 = 0
            par['I1'] = par['I1']/(l_value*theta_step)
            par['D1'] = par['D1']/(l_value*theta_step)

        else:
            unit1 = 'mm'

        if par['GROUP_NAME_2'] == 'ROT_STAGE':
            unit2 = 'degrees'
        elif par['GROUP_NAME_2'] in ['PICOMOTOR-X', 'PICOMOTOR-Y']:
            if par['RECEIVER'] == 'polytec':
                Polytec().autofocusVibrometer(span='Full')
                l_value = par['MIRROR_DISTANCE']
                unit2 = 'mm'
            else:
                l_value = par['MIRROR_DISTANCE']
                unit2 = 'radians'
            pos2 = 0
            par['I2'] = par['I2']/(l_value*theta_step)
            par['D2'] = par['D2']/(l_value*theta_step)

        else:
            unit2 = 'mm'

        if par['GROUP_NAME_1'] in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']:
            pos1 = Execute().move_stage(
                par['GROUP_NAME_1'],
                par['XPS_1'],
                par['SOCKET_ID_1'],
                x_value,
                )
        if par['GROUP_NAME_2'] in ['SHORT_STAGE', 'LONG_STAGE', 'ROT_STAGE']:
            pos2 = Execute().move_stage(
                par['GROUP_NAME_2'],
                par['XPS_2'],
                par['SOCKET_ID_2'],
                y_value,
                )

        axis_1, axis_2, fig = Initialize().two_plot(par['GROUP_NAME_1'], header)
        i = 0

        while i < par['TOTAL_TRACES_D1']:

            print('trace %s of %s' %(tracenum, par['TOTAL_TRACES_D1']))

            if i > 0:
                if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
                    PMot().move_rel(par['PX'], par['D1'])
                    pos1 = float(PMot().get_TP(par['PX']))*l_value*theta_step
                elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
                    PMot().move_rel(par['PY'], par['D1'])
                    pos1 = float(PMot().get_TP(par['PY']))*l_value*theta_step
                else:
                    pos1 = Execute().move_stage(
                        par['GROUP_NAME_1'],
                        par['XPS_1'],
                        par['SOCKET_ID_1'],
                        x_value,
                        )

                if par['GROUP_NAME_2'] == 'PICOMOTOR-X':
                    PMot().move_rel(par['PX'], par['D2'])
                    pos2 = float(PMot().get_TP(par['PX']))*l_value*theta_step
                elif par['GROUP_NAME_2'] == 'PICOMOTOR-Y':
                    PMot().move_rel(par['PY'], par['D2'])
                    pos2 = float(PMot().get_TP(par['PY']))*l_value*theta_step
                else:
                    pos2 = Execute().move_stage(
                        par['GROUP_NAME_2'],
                        par['XPS_2'],
                        par['SOCKET_ID_2'],
                        y_value,
                        )

            Execute().update_header(header, pos1, par['GROUP_NAME_1'])
            Execute().update_header(header, pos2, par['GROUP_NAME_2'])

            print('dimension 1 = {} {}'.format(pos1, unit1))
            print('dimension 2 = {} {}'.format(pos2, unit2))

            sleep(par['WAITTIME']) # delay after stage movement

            #Execute().check_vibfocus(par['CHANNEL'],par['VIB_SIGNAL'],par['SIGNAL_LEVEL'])
            #Polytec().autofocusVibrometer(span='Small')
            average, average2 = Execute().data_capture(par)#['CONTROL'],par['CHANNEL'])

            # save current trace
            Execute().save_trace(header, average, par['FILENAME'])

            if par['CHANNEL2'] != 'null':
                Execute().save_trace(header, average2, par['FILENAME2'])

            # update figure
            if par['MAP'] != 'none' and i > 0:
                Execute().update_two_plot(times, average, x_value, par, header, fig, axis_1, axis_2)

            Execute().update_time(par)

            y_value += par['D2']
            x_value += par['D1']
            i += 1
            tracenum += 1

        # move stages back to starting position
        x_value = par['I1']
        y_value = par['I2']

        if par['GROUP_NAME_2'] == 'PICOMOTOR-X':
            PMot().move_abs(par['PX'], float(y_value))
            pos2 = float(PMot().get_TP(par['PX']))*l_value*theta_step
        elif par['GROUP_NAME_2'] == 'PICOMOTOR-Y':
            PMot().move_abs(par['PY'], float(y_value))
            pos2 = float(PMot().get_TP(par['PY']))*l_value*theta_step
        else:
            pos2 = Execute().move_stage(
                par['GROUP_NAME_2'],
                par['XPS_2'],
                par['SOCKET_ID_2'],
                y_value,
                )

        if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
            PMot().move_abs(par['PX'], float(x_value))
            pos1 = float(PMot().get_TP(par['PX']))*l_value*theta_step
        elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
            PMot().move_abs(par['PY'], float(x_value))
            pos1 = float(PMot().get_TP(par['PY']))*l_value*theta_step
        else:
            pos1 = Execute().move_stage(
                par['GROUP_NAME_1'],
                par['XPS_1'],
                par['SOCKET_ID_1'],
                x_value,
                )

        # finish.
        print('scan complete!')
        print('data saved as: %s \n'%par['FILENAME'])
