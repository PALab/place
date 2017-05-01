"""Static functions for scanning.

This file contains the static methods that were previously in
scan_functions.py.
"""
import re
from math import ceil, log
from ...alazartech import atsapi as ats
from ... import automate
from .parameters import Parameters
from .cli import CLI_HELP
from ...scripts import scan

def options(opts): # pylint: disable=too-many-branches
    """Parse command line options and save in par dictionary

    :param opts: attribute/value pairs for the scan
    :type opts: list

    :returns: a dictionary of attribute/value pairs
    :rtype: dict

    :raises ValueError: on invalid argument
    """
    par = Parameters()
    for option, argument in opts:
        if option in ('-h', '--help'):
            print(CLI_HELP)
            exit(0)
        elif option == "--n":
            par.FILENAME = argument + '.h5'
        elif option == "--n2":
            par.FILENAME2 = argument + '.h5'
        elif option == '--scan':
            if argument == 'point':
                par.scan_type = scan.SCAN_POINT
                par.DIMENSIONS = 0
            elif argument == '1D':
                par.scan_type = scan.SCAN_1D
                par.DIMENSIONS = 1
            elif argument == '2D':
                par.scan_type = scan.SCAN_2D
                par.DIMENSIONS = 2
            elif argument == 'dual':
                par.scan_type = scan.SCAN_DUAL
                par.DIMENSIONS = 2
            else:
                raise ValueError(argument + ' is an invalid scan type')
        elif option == '--s1':
            if argument == 'long':
                par.GROUP_NAME_1 = 'LONG_STAGE'
            elif argument == 'short':
                par.GROUP_NAME_1 = 'SHORT_STAGE'
            elif argument == 'rot':
                par.GROUP_NAME_1 = 'ROT_STAGE'
            elif argument == 'picox':
                par.GROUP_NAME_1 = 'PICOMOTOR-X'
            elif argument == 'picoy':
                par.GROUP_NAME_1 = 'PICOMOTOR-Y'
            else:
                raise ValueError('ERROR: invalid stage')
        elif option == '--s2':
            if argument == 'long':
                par.GROUP_NAME_2 = 'LONG_STAGE'
            elif argument == 'short':
                par.GROUP_NAME_2 = 'SHORT_STAGE'
            elif argument == 'rot':
                par.GROUP_NAME_2 = 'ROT_STAGE'
            elif argument == 'picox':
                par.GROUP_NAME_2 = 'PICOMOTOR-X'
            elif argument == 'picoy':
                par.GROUP_NAME_2 = 'PICOMOTOR-Y'
            else:
                raise ValueError('ERROR: invalid stage')
        elif option == '--dm':
            par.MIRROR_DISTANCE = float(argument)*10 # mm
        elif option == '--sr':
            par.SAMPLE_RATE = "SAMPLE_RATE_" + argument + "SPS"
        elif option == '--tm':
            par.DURATION = float(argument)
        elif option == '--ch':
            par.CHANNEL = "CHANNEL_" + str(argument)
        elif option == '--ch2':
            par.CHANNEL2 = "CHANNEL_" + str(argument)
        elif option == '--av':
            par.AVERAGES = int(argument)
        elif option == '--wt':
            par.WAITTIME = float(argument)
        elif option == "--trigger_source_id_1":
            if hasattr(ats, argument):
                par.trigger_source_id_1 = getattr(ats, argument)
            else:
                raise ValueError(argument + " is not a valid trigger source")
        elif option == "--tl":
            par.TRIG_LEVEL = float(argument)
        elif option == "--tr":
            par.TRIG_RANGE = float(argument)
        elif option == "--cr":
            par.CHANNEL_RANGE = "INPUT_RANGE_PM_" + str(argument)
        elif option == "--cp":
            if argument == 'AC':
                par.AC_COUPLING = True
            elif argument == 'DC':
                par.AC_COUPLING = False
            else:
                raise ValueError('ERROR: invalid coupling')
        elif option == "--ohm":
            par.IMPEDANCE = int(argument)
        elif option == "--cr2":
            par.CHANNEL_RANGE_2 = "INPUT_RANGE_PM_" + str(argument)
        elif option == "--cp2":
            if argument == 'AC':
                par.AC_COUPLING2 = True
            elif argument == 'DC':
                par.AC_COUPLING2 = False
            else:
                raise ValueError('ERROR: invalid coupling')
        elif option == "--ohm2":
            par.IMPEDANCE2 = int(argument)
        elif option == "--i1":
            par.I1 = float(argument)
        elif option == "--d1":
            par.D1 = float(argument)
        elif option == "--f1":
            par.F1 = float(argument)
        elif option == "--i2":
            par.I2 = float(argument)
        elif option == "--d2":
            par.D2 = float(argument)
        elif option == "--f2":
            par.F2 = float(argument)
        elif option == '--rv':
            par.RECEIVER = str(argument)
        elif option == '--rv2':
            par.RECEIVER2 = str(argument)
        elif option == '--ret':
            par.RETURN = str(argument)
        elif option == "--dd":
            par.DECODER = argument
        elif option == "--rg":
            par.DECODER_RANGE = argument + '/s/V'
        elif option == '--vch':
            par.VIB_CHANNEL = "CHANNEL_" + str(argument)
        elif option == '--sl':
            par.SIGNAL_LEVEL = float(argument)
        elif option == "--pp":
            par.PORT_POLYTEC = argument
        elif option == "--bp":
            par.BAUD_POLYTEC = argument
        elif option == "--so":
            par.SOURCE = str(argument)
        elif option == "--en":
            par.ENERGY = argument + ' mJ/cm^2'
        elif option == "--lm":
            par.WAVELENGTH = argument + 'nm'
        elif option == "--rr":
            par.REP_RATE = float(argument)
        elif option == "--map":
            par.MAP = str(argument)
        elif option == "--pl":
            par.PLOT = argument
        elif option == "--autofocus":
            if argument in ['auto', 'off', 'small', 'medium', 'full']:
                par.autofocus = argument
            else:
                raise ValueError(argument + " is not a valid autofocus value")
        elif option == "--comments":
            par.COMMENTS = argument
        else:
            raise ValueError('ERROR: invalid option')
    return par

def scan_time(par):
    """Set the time the scan will take."""
    par.TRACE_TIME = par.AVERAGES/par.REP_RATE
    #timea =
    #Polytec().autofocusVibrometer(span='Small')
    if par.scan_type == scan.SCAN_POINT:
        par.TOTAL_TIME = par.TRACE_TIME
    if par.scan_type == scan.SCAN_1D or par.scan_type == scan.SCAN_DUAL:
        # total traces for dimension 1
        par.TOTAL_TRACES_D1 = ceil(abs((par.F1-par.I1))/par.D1)
        par.TOTAL_TIME = par.TRACE_TIME* par.TOTAL_TRACES_D1
    if par.scan_type == scan.SCAN_2D:
        # total traces for dimension 1
        par.TOTAL_TRACES_D1 = ceil(abs((par.F1-par.I1))/par.D1)
        # total traces for dimension 2
        par.TOTAL_TRACES_D2 = ceil(abs((par.F2-par.I2))/par.D2)
        par.TOTAL_TIME = par.TRACE_TIME*par.TOTAL_TRACES_D1*par.TOTAL_TRACES_D2
    if par.scan_type == scan.SCAN_DUAL:
        # total traces for dimension 1
        par.TOTAL_TRACES_D1 = ceil(abs((par.F1-par.I1))/par.D1)
        # total traces for dimension 2
        par.TOTAL_TRACES_D2 = ceil(abs((par.F2-par.I2))/par.D2)
        par.TOTAL_TIME = par.TRACE_TIME* par.TOTAL_TRACES_D1
        if par.TOTAL_TRACES_D1 != par.TOTAL_TRACES_D2:
            print('ERROR: number of traces must be the same in both dimensions')
            exit()
    return par

def polytec(par):
    """Initialize Polytec vibrometer

    Initialize Polytec vibrometer and obtain relevant settings to save in
    trace headers. Also autofocuses vibrometer.
    """
    # open connection to vibrometer
    poly = automate.Polytec(par.PORT_POLYTEC, par.BAUD_POLYTEC)
    poly.openConnection()

    # set decoder range
    poly.setRange(par.DECODER, par.DECODER_RANGE)

    # determine delay due to decoder
    delay = re.findall(r'[-+]?\d*\.\d+|\d+', poly.getDelay(par.DECODER))
    time_delay = float(delay[0])

    # get maximum frequency recorded
    freq_string = poly.getMaxFreq(par.DECODER)
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
    decoder_range = poly.get_range(par.DECODER)
    range_num = re.findall(r'[-+]?\d*\.\d+|\d+', par.DECODER_RANGE)
    del_num_r = len(range_num)+1
    calib = float(range_num[0])
    calib_unit = decoder_range[del_num_r:].lstrip()

    par.TIME_DELAY = time_delay
    par.MAX_FREQ = max_freq
    par.CALIB = calib
    par.CALIB_UNIT = calib_unit

    # autofocus vibrometer
    poly.autofocusVibrometer()

    return par

def osci_card(par):
    """Initialize Alazar Oscilloscope Card."""

    # initialize channel for signal from vibrometer decoder
    control = automate.TriggeredRecordingController()
    control.configureMode = True
    control.create_input(
        par.CHANNEL,
        par.CHANNEL_RANGE,
        par.AC_COUPLING,
        par.IMPEDANCE,
        )
    control.setSampleRate(par.SAMPLE_RATE)
    samples = control.samplesPerSec*par.DURATION*1e-6
    samples = int(pow(2, ceil(log(samples, 2)))) # round number of samples to next power of two
    control.setSamplesPerRecord(samples=samples)
    control.setRecordsPerCapture(par.AVERAGES)
    trigger_level = 128 + int(127*par.TRIG_LEVEL/par.TRIG_RANGE)

    print(trigger_level)

    control.setTrigger(
        operationType="TRIG_ENGINE_OP_J",
        sourceOfJ=par.trigger_source_id_1,
        levelOfJ=trigger_level,
        )
    control.setTriggerTimeout(10)
    control.configureMode = False

    # FIX THIS
    if par.CHANNEL2 != 'null':
        control2 = automate.TriggeredRecordingController()
        control2.configureMode = True
        control2.create_input(
            par.CHANNEL2,
            par.CHANNEL_RANGE2,
            par.AC_COUPLING2,
            par.IMPEDANCE2,
            )
        control2.setSampleRate(par.SAMPLE_RATE)
#unused            samples2 = control.samplesPerSec*par.DURATION*1e-6
        # round number of samples to next power of two
#unused            samples2 = int(pow(2, ceil(log(samples, 2))))
        control2.setSamplesPerRecord(samples=samples)
        control2.setRecordsPerCapture(par.AVERAGES)
        trigger_level = 128 + int(127*par.TRIG_LEVEL/par.TRIG_RANGE)
        control2.setTrigger(
            operationType="TRIG_ENGINE_OP_J",
            sourceOfJ=par.trigger_source_id_1,
            levelOfJ=trigger_level
            )
        control2.setTriggerTimeout(10)
        control2.configureMode = False
        par.CONTROL2 = control2

    if par.VIB_CHANNEL != 'null':
        # initialize channel for vibrometer sensor head signal
        vib_signal = automate.TriggeredContinuousController()
        vib_signal.configureMode = True
        vib_signal.create_input(
            par.VIB_CHANNEL,
            ats.INPUT_RANGE_PM_4_V,
            ats.DC_COUPLING,
            par.IMPEDANCE,
            ) # 0 to 3 V DC
        vib_signal.setSamplesPerRecord(samples=1)
        vib_signal.setRecordsPerCapture(3)
        vib_signal.setTrigger(
            operationType="TRIG_ENGINE_OP_J",
            sourceOfJ='TRIG_EXTERNAL',
            levelOfJ=trigger_level,
            )
        vib_signal.setTriggerTimeout(10)
        par.VIB_SIGNAL = vib_signal
    else:
        par.VIB_SIGNAL = 'null'

    par.SAMPLES = samples
    par.CONTROL = control
    print('oscilloscope card ready and parameters set')
    return par

def controller(ip_address, par, i):
    """Initialize XPS controller and move stage to starting scan position

    :param ip_address: controller IP address
    :type ip_address: str

    :param par: scan parameters
    :type par: dict

    :param i: scan axis (1,2,..)
    :type i: int

    :returns: the modified parameter dictionary
    :rtype: dict
    """
    xps = automate.XPS()
    xps.GetLibraryVersion()

    socket_id = xps.TCP_ConnectToServer(ip_address, 5001, 3) # connect over network
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
    xps.GroupPositionCurrentGet(socket_id, par['GROUP_NAME_'+str(i)], 1)

    par['XPS_'+str(i)] = xps
    par['SOCKET_ID_'+str(i)] = socket_id
    print('XPS stage initialized')

    return par

#TODO: This should be using the IP address and port, but it's not
def picomotor_controller(ip_address, port, par): #pylint: disable=unused-argument
    """Initialize Picomotor controller"""

    pmot = automate.PMot()
    pmot.connect()

    print('Picomotor controller initialized')

    par.PX = 2
    par.PY = 1

    # set to high velocity
    pmot.set_VA(par.PX, 1700)
    pmot.set_VA(par.PY, 1700)

    # set current position to zero
    pmot.set_DH(par.PX, 0)
    pmot.set_DH(par.PY, 0)
    #set units to encoder counts for closed-loop
    pmot.set_SN(par.PX, 1)
    pmot.set_SN(par.PY, 1)
    # set following error threshold
    pmot.set_FE(par.PX, 200)
    pmot.set_FE(par.PY, 200)
    # set closed-loop update interval to 0.1
    pmot.set_CL(par.PX, 0.1)
    pmot.set_CL(par.PY, 0.1)
    # save settings to non-volatile memory
    #PMot().set_SM()
    # enable closed-loop setting
    pmot.set_MM(par.PX, 1)
    pmot.set_MM(par.PY, 1)

    # set Deadband
    #PMot().set_DB(10)
    # save settings to non-volatile memory
    pmot.set_SM()

    print('X and Y picomotors initialized')

    return par
