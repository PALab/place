"""Static functions for scanning.

This file contains the static methods that were previously in
scan_functions.py.
"""
import re
from math import ceil, log
from ...alazartech import atsapi as ats
from ..osci_card import controller as card
from ..osci_card.tc_controller import TriggeredContinuousController
from ..polytec.vibrometer import Polytec
from ..xps_control.XPS_C8_drivers import XPS
from ..new_focus.picomotor import PMot
from .cli import CLI_HELP

def options(opts):
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
            print(CLI_HELP)
            exit(0)
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
                raise ValueError('ERROR: invalid stage')
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
                raise ValueError('ERROR: invalid stage')
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

def scan_time(par):
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

def polytec(par):
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

def osci_card(par):
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
        par['VIB_SIGNAL'] = vib_signal
    else:
        par['VIB_SIGNAL'] = 'null'

    par['SAMPLES'] = samples
    par['CONTROL'] = control
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
    xps = XPS()
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
