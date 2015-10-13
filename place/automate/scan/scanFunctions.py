'''
-------------------------
Command line options:
-------------------------

-h, --help
     prints doc string
--n
     define the base file name to save data to (data will be saved as 'filename.h5' in current directory). 
     Default: TestScan
--scan
     defines type of scan.
     Options: point, 1D, 2D
     Default: point
--s1 
     defines stage for first dimension.  
     Options: long (1000mm linear stage), short (300mm linear stage), rot (rotation stage), or picox, picoy (picomotor mirrors in x- and y- direction)
     Default: long
--s2
     defines stage for second dimensoin.
     Options: long (1000mm linear stage), short (300mm linear stage), rot (rotation stage), or picox, picoy (picomotor mirrors in x- and y- direction)
     Default: short
--dm 
     With polytec receiver, defines distance between polytec sensor head and scanning mirrors with picomotors (in cm). Otherwise, defines distance from picomotors to point of interest.  Necessary input for accurate picomotor scanning.
     Default: 50 cm
--sr 
     defines sample rate.  Supply an integer with suffix, e.g. 100K for 10e5 samples/second or 1M for 10e6 samples/second.
     Options ATS9440 and ATS660: 1K, 2K, 5K, 10K, 20K, 50K, 100K, 200K, 500K, 1M, 2M, 5M, 10M, 20M, 50M, 100M, 125M
    
     Default: 10M (10 Megasamples/second)
--tm 
     defines time duration for each trace in microseconds.
     Example: --tm 400 for 400 microsecond traces
     Default: 256 microseconds
     *NOTE: number of samples will be rounded to next power of two to avoid scrambling data
--ch
     defines oscilloscope card channel to record data.
     Example --ch B
     Default: A
--av
     define the number of records that shall be averaged. 
     Example: --av 100 to average 100 records
     Default: 64 averages
--wt
     time to stall after each stage movement, in seconds.  Use to allow residual vibrations to dissipate before recording traces, if necessary.
     Default: 0
--tl
     trigger level in volts.  
     Default: 1
--tr
     input range for external trigger in volts. 
     Default: 4
--cr
     input range of acquisition channel. 
     Options ATS660: 200_MV, 400_MV, 800_MV, 2_V, 4_V, 8_V, 16_V 
     Options ATS9440: 100_MV, 200_MV, 400_MV, 1_V, 2_V, 4_V
     Default: +/- 2V
--cp
     coupling.  
     Options: AC, DC   
     Default: DC coupling.
--ohm
     set impedance of oscilloscope card
     Options: 50 (50 ohm impedance), 1 (1Mohm impedance)
     Default: 50 ohm
--i1
     define the initial position for dimension 1 stage.  Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm)
     Default: 0
--d1
     define increment for dimension 1 stage. Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm). 
     Default: 1
     *NOTE: the increment in the header may vary from the value specified for the picomotor results, because the motors will round to the nearest increment number of *steps*.  The increment in the header is CORRECT.
--f1 
     define the final position for dimension 1 stage. Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm)
     Default: 0
--i2
     define the initial position for dimension 2 stage.  Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm)
     Default: 0
--d2
     define increment for dimension 2 stage. Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm)
     Default: 1
--f2 
     define the final position for dimension 2 stage. Defined in units of corresponding stage: rotation stage (degrees), short and long stage, and picomotors (mm)
     Default: 0
--rv
     define which receiver to use. 
     Options: polytec, gclad, osldv, none
     Default: none
--dd
     define decoder for Polytec vibrometer. 
     Options: VD-08, VD-09, DD-300 (best for ultrasonic applications), and DD-900.  
     Default: DD-300
--rg 
     define range of decoder of Polytec vibrometer.  Specify both the value and unit length for the appropriate. See Polytec manual for possible decoders.
     Example: --rg 5mm specifies a range of 5 mm/s/V. 
     Default: 5 mm/s/V
--vch
     define oscilloscope card channel for polytec signal level      
     Default: B
--sl
     define suitable polytec signal level 
     Options: floats range ~0 to 1.1
     Default: 0.90
--pp 
     defines serial port to to communicate with Polytec controller.
     Default: '/dev/ttyS0'
--bp
     defines baudrate for serial communication with Polytec controller.
     Default: 115200
--en
     specify the energy of the source used (in mJ).  
     Default: 0 mJ
    *NOTE: the source laser energy must be manaually set on the laser power supply.  This value is for documentation purposes, only.
--map
     define colormap to use during scan to display image. Choose 'none' if you do not wish to read/plot the 2D data. 
     Options: built-in matplotlib colormaps
     Example: --map 'jet' to use jet colormap
     Default: 'gray'
     *NOTE: for large datasets, 'none' is recommended, as it adds significant time to the scan to read and plot the full data set. 
--comments
     add any extra comments to be added to the trace headers.  
     Example: --comments='Energy at 50.  Phantom with no tube.'
     *NOTE: you must have either '  ' or "  " surrounding comments

@author: Jami L Johnson, Evan Rust
March 19 2015
'''

import re
from math import ceil, log
from obspy.core.trace import Stats
from time import sleep
import numpy as np
from obspy import read, Trace, UTCDateTime
import matplotlib.pyplot as plt
import sys
import os
from string import atof

# place modules

from place.automate.new_focus.picomotor import PMot
from place.automate.polytec.vibrometer import Polytec, PolytecDecoder, PolytecSensorHead
import cPickle as pickle
from place.automate.polytec import vibrometer
from place.automate.osci_card import controller
card = controller
from place.automate.xps_control.XPS_C8_drivers import XPS
from place.automate.quanta_ray.QRay_driver import QuantaRay, QSW, QRread, QRset, QRstatus, QRcomm


class Initialize:
    def __init__(self):
        pass

    def options(self,opts,args):
        '''
        Parse command line options and save in par dictionary
        '''
        # Defaults:
        filename = 'TestScan.h5'
        scan = 'point'
        GroupName1 = 'LONG_STAGE' 
        GroupName2 = 'SHORT_STAGE'
        mirror_dist = 50
        sampleRate = 'SAMPLE_RATE_10MSPS'
        duration = 256
        channel = 'CHANNEL_A'
        averagedRecords = 64
        waitTime = 0  
        trigLevel=1
        trigRange=4 
        channelRange='INPUT_RANGE_PM_2_V'
        ACcouple = False
        ohms=50
        i1 = 0 
        d1 = 1
        f1 = 0
        i2 = 0 
        d2 = 1
        f2 = 0
        receiver = 'none'
        decoder = 'DD-300'
        drange = '5mm'
        vibChannel = 'null'
        sigLevel = 0.90
        portPolytec = '/dev/ttyS0'
        baudPolytec = 115200
        energy = '0 mJ'
        mapColor = 'gray'
        comments = ''

        # ---non-commandline defaults
        unit = 'mm'
        Positioner = 'Pos'
        maxFreq = '6MHz'
        minFreq = '0MHz'
        calib = 1
        calibUnit = 'null'
        instruments = []
        parameters = []

        for o, a in opts:
            if o in ('-h', '--help'):
                print __doc__
                sys.exit(0)
            if o in ("--n"):
                filename = a + '.h5'
            if o in ('--scan'):
                scan = str(a)
            if o in ('--s1'):
                if a == 'long':
                    GroupName1 = 'LONG_STAGE'
                    unit = 'mm'
                elif a == 'short':
                    GroupName1 = 'SHORT_STAGE'
                    unit = 'mm'
                elif a == 'rot':
                    GroupName1 = 'ROT_STAGE'
                    unit = 'deg'
                elif a == 'picox':
                    GroupName1 = 'PICOMOTOR-X'
                    unit = 'mm'
                elif a == 'picoy':
                    GroupName1 = 'PICOMOTOR-Y'
                    unit = 'mm'
                else: 
                    print 'ERROR: invalid stage'
                    exit()
            if o in ('--s2'):
                if a == 'long':
                    GroupName2 = 'LONG_STAGE'
                    unit = 'mm'
                elif a == 'short':
                    GroupName2 = 'SHORT_STAGE'
                    unit = 'mm'
                elif a == 'rot':
                    GroupName2 = 'ROT_STAGE'
                    unit = 'deg'
                elif a == 'picox':
                    GroupName2 = 'PICOMOTOR-X'
                    unit = 'mm'
                elif a == 'picoy':
                    GroupName2 = 'PICOMOTOR-Y'
                    unit = 'mm'
                else: 
                    print 'ERROR: invalid stage'
                    exit()
            if o in ('--dm'):
                mirror_dist = float(a)*10 # mm
            if o in ('--sr'):
                sampleRate = "SAMPLE_RATE_" + a + "SPS" 
            if o in ('--tm'):
                duration = float(a)
            if o in ('--ch'):
                channel = "CHANNEL_" + str(a) 
            if o in ('--av'):
                averagedRecords = int(a)            
            if o in ('--wt'):
                waitTime = float(a)
            if o in ("--tl"):
                trigLevel = float(a)
            if o in ("--tr"):
                trigRange = float(a)
            if o in ("--cr"):
                channelRange = "INPUT_RANGE_PM_" + str(a)
            if o in ("--cp"):
                if a == 'AC':
                    ACcouple = True
                elif a == 'DC':
                    ACcouple = False
            if o in ("--ohm"):
                ohms = int(a)
            if o in ("--i1"):
                i1 = float(a)
            if o in ("--d1"):
                d1 = float(a)
            if o in ("--f1"):
                f1 = float(a)
            if o in ("--i2"):
                i2 = float(a)
            if o in ("--d2"):
                d2 = float(a)
            if o in ("--f2"):
                f2 = float(a)
            if o in ('--rv'):
                receiver = str(a)    
            if o in ("--dd"):
                decoder = a
            if o in ("--rg"):
                drange = a + '/s/V'
            if o in ('--vch'):
                vibChannel = "CHANNEL_" + str(a) 
            if o in ('--sl'):
                sigLevel = float(a)
            if o in ("--pp"):
                portPolytec = a
            if o in ("--bp"):
                baudPolytec = a
            if o in ("--en"):
                energy = a + ' mJ'
            if o in ("--map"):
                mapColor = str(a)
            if o in ("--comments"):
                comments = a

        parameters = {'GROUP_NAME_1':GroupName1,'GROUP_NAME_2':GroupName2,'MIRROR_DISTANCE':mirror_dist,'SCAN':scan,'SAMPLE_RATE':sampleRate,'DURATION':duration,'CHANNEL':channel,'AVERAGES':averagedRecords,'WAITTIME':waitTime,'RECEIVER':receiver,'SIGNAL_LEVEL':sigLevel,'VIB_CHANNEL':vibChannel,'TRIG_LEVEL':trigLevel,'TRIG_RANGE':trigRange,'CHANNEL_RANGE':channelRange,'AC_COUPLING':ACcouple,'IMPEDANCE':ohms,'I1':i1,'D1':d1,'F1':f1,'I2':i2,'D2':d2,'F2':f2,'FILENAME':filename,'DECODER':decoder,'DECODER_RANGE':drange,'MAP':mapColor,'ENERGY':energy,'COMMENTS':comments,'PORT_POLYTEC':portPolytec,'BAUD_POLYTEC':baudPolytec,'PX':0,'PY':0}

        if scan == '1D':
            parameters['DIMENSIONS'] = 1
        elif scan == '2D':
            parameters['DIMENSIONS'] = 2
        else:
            parameters['DIMENSIONS'] = 0
        
        return parameters

    def time(self,par):
        ''' set the time the scan will take'''
        par['TRACE_TIME'] = par['AVERAGES']/10
        
        if par['SCAN'] == 'point':
            par['TOTAL_TIME'] = par['TRACE_TIME']
        if par['SCAN'] == '1D':
            par['TOTAL_TRACES_D1'] = ceil(abs((par['F1']-par['I1']))/par['D1']) # total traces for dimension 1
            par['TOTAL_TIME'] = par['TRACE_TIME']* par['TOTAL_TRACES_D1']
        if par['SCAN'] == '2D':  
            par['TOTAL_TRACES_D1'] = ceil(abs((par['F1']-par['I1']))/par['D1']) # total traces for dimension 1
            par['TOTAL_TRACES_D2'] = ceil(abs((par['F2']-par['I2']))/par['D2']) # total traces for dimension 2
            par['TOTAL_TIME'] = par['TRACE_TIME']*par['TOTAL_TRACES_D1']*par['TOTAL_TRACES_D2']
        
        return par

    def polytec(self, par):
        '''Initialize Polytec vibrometer and obtain relevant settings to save in trace headers. Also autofocuses vibrometer.'''
        # open connection to vibrometer
        Polytec(par['PORT_POLYTEC'], par['BAUD_POLYTEC']).openConnection() 
       
        # set decoder range
        PolytecDecoder().setRange(par['DECODER'],par['DECODER_RANGE'])

        # determine delay due to decoder
        delayString = PolytecDecoder().getDelay(par['DECODER'])
        delay =  re.findall(r'[-+]?\d*\.\d+|\d+', delayString) # get time delay in us
        timeDelay =  float(delay[0])

        # get maximum frequency recorded
        freqString = PolytecDecoder().getMaxFreq(par['DECODER'])
        freq =  re.findall(r'[-+]?\d*\.\d+|\d+',freqString)
        delNumF = len(freq)+2
        freq = float(freq[0])
        freqUnit = freqString[delNumF:].lstrip()
        freqUnit = freqUnit.rstrip()
        if freqUnit=='kHz':
            multiplier = 10**3
        elif freqUnit == 'MHz':
            multiplier = 10**6
        maxFreq = freq*multiplier
  
        # get range of decoder and amplitude calibration factor
        decoderRange = PolytecDecoder().getRange(par['DECODER'])
        rangeNum = re.findall(r'[-+]?\d*\.\d+|\d+',par['DECODER_RANGE']) 
        delNumR = len(rangeNum)+1
        calib = float(rangeNum[0])
        calibUnit = decoderRange[delNumR:].lstrip()

        par['TIME_DELAY'] = timeDelay
        par['MAX_FREQ'] = maxFreq
        par['CALIB'] = calib
        par['CALIB_UNIT'] = calibUnit

        # autofocus vibrometer
        PolytecSensorHead().autofocusVibrometer()

        return par

    def osci_card(self, par):
        '''Initialize Alazar Oscilloscope Card.'''

        global control
        # initialize channel for signal from vibrometer decoder
        control = card.TriggeredRecordingController()  
        control.configureMode = True
        control.createInput(channel=par['CHANNEL'],inputRange=par['CHANNEL_RANGE'], AC=par['AC_COUPLING'], impedance=par['IMPEDANCE'])
        control.setSampleRate(par['SAMPLE_RATE'])  
        samples = control.samplesPerSec*par['DURATION']*1e-6 
        samples = int(pow(2, ceil(log(samples,2)))) # round number of samples to next power of two
        control.setSamplesPerRecord(samples=samples)
        control.setRecordsPerCapture(par['AVERAGES'])
        triggerLevel = 128 + int(127*par['TRIG_LEVEL']/par['TRIG_RANGE'])
        control.setTrigger(operationType="TRIG_ENGINE_OP_J",sourceOfJ='TRIG_EXTERNAL',levelOfJ=triggerLevel) 
        control.setTriggerTimeout(10)  
        control.configureMode = False    

        if par['VIB_CHANNEL'] != 'null':
            # initialize channel for vibrometer sensor head signal
            vibSignal = card.TriggeredContinuousController()
            vibSignal.configureMode=True
            vibSignal.createInput(channel=par['VIB_CHANNEL'],inputRange='INPUT_RANGE_PM_4_V', AC=False, impedance=par['IMPEDANCE']) # 0 to 3 V DC
            vibSignal.setSamplesPerRecord(samples=1)
            vibSignal.setRecordsPerCapture(3)
            vibSignal.setTrigger(operationType="TRIG_ENGINE_OP_J",sourceOfJ='TRIG_EXTERNAL',levelOfJ=triggerLevel) 
            vibSignal.setTriggerTimeout(10)
            
        else: 
            vibSignal = 'null'

        par['SAMPLES'] = samples
        par['CONTROL'] = control
        par['VIB_SIGNAL'] = vibSignal
        print 'oscilloscope card ready and parameters set'
        return par#, control, vibSignal
                
    def controller(self, IP, par, i):
        '''Initialize XPS controller and move to stage to starting scan position
        Inputs:
        par = scan parameters
        i = scan axis (1,2,..)
        Outputs:
        '''
       
        xps = XPS()
        xps.GetLibraryVersion()
        
        socketId = xps.TCP_ConnectToServer(IP,5001,3) # connect over network
        print "connected to: ", socketId

        ControllerErr = xps.ControllerStatusGet(socketId)
        if ControllerErr[0] == 0:
            print 'XPS controller status: ready'
        else:
            print 'XPS controller status failed: ERROR =', ControllerErr

        LogErr =  xps.Login(socketId, "Administrator", "Administrator")
        if LogErr[0] == 0:
            print 'login successful'
        else:
            print 'login failed: ERROR = ', LogErr
      
        xps.GroupKill(socketId, par['GROUP_NAME_'+str(i)])
        InitializeGrpErr = xps.GroupInitialize(socketId,  par['GROUP_NAME_'+str(i)])
        if InitializeGrpErr[0] == 0:
            print 'group initialized'
        else:
            print 'group initialize failed: ERROR = ', InitializeGrpErr
        xps.GroupStatusGet(socketId,  par['GROUP_NAME_'+str(i)])
    
        HomeErr = xps.GroupHomeSearch(socketId,  par['GROUP_NAME_'+str(i)])
        if HomeErr[0] == 0:
            print 'home search successful'
        else:
            print 'home search failed: ERROR = ', HomeErr

        xps.GroupMoveAbsolute(socketId, par['GROUP_NAME_'+str(i)], [par['I'+str(i)]])
        ck = 0 
        actualPos =  xps.GroupPositionCurrentGet(socketId, par['GROUP_NAME_'+str(i)],1)

        par['XPS_'+str(i)] = xps
        par['SOCKET_ID_'+str(i)] = socketId
        print 'XPS stage initialized'
        
        return par

    def picomotor_controller (self, IP, port, par):
        '''Initialize Picomotor controller'''
        
        PMot().connect()
        
        print 'Picomotor controller initialized'

        par['PX'] = 2
        par['PY'] = 1

        # set to high velocity 
        PMot().set_VA(par['PX'],1700) 
        PMot().set_VA(par['PY'],1700)

        # set current position to zero
        PMot().set_DH(par['PX'],0) 
        PMot().set_DH(par['PY'],0)
        #set units to encoder counts for closed-loop
        PMot().set_SN(par['PX'],1)
        PMot().set_SN(par['PY'],1)
        # set following error threshold
        PMot().set_FE(par['PX'],200)
        PMot().set_FE(par['PY'],200)
        # set closed-loop update interval to 0.1
        PMot().set_CL(par['PX'],0.1)
        PMot().set_CL(par['PY'],0.1)
        # save settings to non-volatile memory
        #PMot().set_SM()
        # enable closed-loop setting
        PMot().set_MM(par['PX'],1)
        PMot().set_MM(par['PY'],1)
       
        # set Deadband
        #PMot().set_DB(10)
        # save settings to non-volatile memory
        PMot().set_SM()
        
        print 'X and Y picomotors initialized'

        return par

    def picomotor (self,motor_num):
        '''Initialize PicoMotor'''
        motor = PMot(motor_num)
     
        print 'PicoMotor initialized'

        return motor
    
    def quanta_ray(self, percent, averagedRecords):
        ''' Starts Laser in rep-rate mode and sets watchdog time.  Returns the repitition rate of the laser.'''

        # open laser connection
        QuantaRay().openConnection()
        QRcomm().setWatchdog(time=100) 

        # set-up laser
        QSW().set(cmd='SING') # set QuantaRay to single shot
        QSW().set(cmd='NORM')
        QRset().setOscPower(percent) # set power of laser
        sleep(1)

        # turn laser on
        QuantaRay().on()
        sleep(20)

        print 'Power of laser oscillator: ', QRread().getOscPower()

        # get rep-rate
        repRate = QRread().getTrigRate()
        repRate = re.findall(r'[-+]?\d*\.\d+|\d+',repRate) # get number only
        repRate = float(repRate[0])
        traceTime = averagedRecords/repRate

        # set watchdog time > time of one trace, so laser doesn't turn off between commands
        QRcomm().setWatchdog(time=ceil(2*traceTime)) 

        return traceTime

    def header(self,par):
        '''Initialize generic trace header for all traces'''
        
        custom_header = Stats()
        if par['IMPEDANCE'] == 1:
            impedance = '1Mohm'
        else:
            impedance = '50 ohms'
        custom_header.impedance = impedance
        custom_header.x_position = par['I1']
        custom_header.max_frequency = par['MAX_FREQ']
        custom_header.receiver = par['RECEIVER']
        custom_header.decoder = par['DECODER']
        custom_header.decoder_range = par['DECODER_RANGE']
        custom_header.source_energy = par['ENERGY']
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

    def two_plot(self, GroupName, header):
        plt.ion()
        plt.show()
        fig = plt.figure()   
        ax = fig.add_subplot(211)
        if header.calib_unit.rstrip() == 'nm/V':
            ax.set_ylabel('Displacement (nm)')
        elif header.calib_unit.rstrip() == 'mm/s/V':
            ax.set_ylabel('Particle Velocity (mm/s)')
        ax.set_xlabel('Time ($\mu$s)')
        ax.set_title('Last Trace Acquired')
        ax2 = fig.add_subplot(212)
        if GroupName in ['LONG_STAGE','SHORT_STAGE','PICOMOTOR-X','PICOMOTOR-Y']:
            ax2.set_ylabel('Scan Location ('+ header.x_unit + ')')
        elif GroupName == 'ROT_STAGE':
            ax2.set_ylabel('Scan Location ('+ header.theta_unit + ')')
        ax2.set_xlabel('Time ($\mu$s)')
       
        return ax, ax2, fig

class Execute:

    def __init__(self):
        pass

    def get_times(self,control,channel,header):
        times = control.getTimesOfRecord()
        dt = times[1]-times[0]
        header.delta = dt
        return times, header

    def data_capture(self,control, channel):
        '''
        capture data
        '''
        control.startCapture()  
        control.readData()
        records = control.getDataRecordWise(channel)
        average = np.average(records,0)
        return average

    def update_header(self,header, x,GroupName=''):
        header.starttime = UTCDateTime()
        if GroupName in ['LONG_STAGE', 'SHORT_STAGE', 'PICOMOTOR-X']:
            header.x_position = x
        elif GroupName == 'ROT_STAGE':
            header.theta_position = x
        elif GroupName == 'PICOMOTOR-Y':
            header.y_position = x
        else:
            header.x_position = x

    def move_stage(self, GroupName, xps, socketId, x):
        if GroupName in ['LONG_STAGE','SHORT_STAGE','ROT_STAGE']:
            xps.GroupMoveAbsolute(socketId, GroupName, [x])
            actualPos = xps.GroupPositionCurrentGet(socketId, GroupName,1) 
            return actualPos[1]
        
    def save_trace(self,header, average, filename):
        header.npts = len(average)
        trace = Trace(data=average,header=header)
        trace.write(filename,'H5',mode='a')
        return

    def update_time(self, par):
        '''
        calculate time remaining
        '''
        par['TOTAL_TIME'] -= par['TRACE_TIME']
        hourLeft = int(par['TOTAL_TIME']/3600)
        lessHour = par['TOTAL_TIME']- hourLeft*3600
        minLeft = int(lessHour/60)
        secLeft = int(lessHour - minLeft*60)
        print str(hourLeft) + ':' + str(minLeft) + ':' + str(secLeft) + ' remaining'    
        return par

    def check_vibfocus(self, channel, vibSignal, sigLevel):
        ''' 
        Checks focus of vibrometer sensor head and autofocuses if less then sigLevel specified (0 to ~1.1)
        channel = channel "signal" from polytec controller is connected to on oscilloscope card
        ''' 
        
        vibSignal.startCapture()
        vibSignal.readData(channel)
        signal = vibSignal.getDataRecordWise(channel)
        signal = np.average(signal,0)

        k = 0
        while signal < sigLevel:
            print 'sub-optimal focus:'
            if k == 0:
                PolytecSensorHead().autofocusVibrometer(span='Small')
            elif k == 1:
                PolytecSensorHead().autofocusVibrometer(span='Medium')
            else: 
                PolytecSensorHead().autofocusVibrometer(span='Full')
                vibSignal.startCapture()
                vibSignal.readData()
                signal = vibSignal.getDataRecordWise(channel)
                signal = np.average(signal,0)
            k+=1
            if k > 3:
                print 'unable to obtain optimum signal'
                break
            
            return signal

    def plot(self, header, times, average):
        '''
        plot trace
        '''
        plt.plot(times*1e6, average*header.calib)
        plt.xlim((0,max(times)*1e6))
        if header.calib_unit.rstrip() == 'nm/V':
            plt.ylabel('Displacement (nm)')
        elif header.calib_unit.rstrip() == 'mm/s/V':
            plt.ylabel('Particle Velocity (mm/s)')
        plt.xlabel('Time (us)')
        plt.show()

    def update_two_plot(self, times, average, x, par, header, fig, ax, ax2):
        pltData = read(par['FILENAME'],'H5',calib=True)

        if par['GROUP_NAME_1'] in ['LONG_STAGE','SHORT_STAGE','PICOMOTOR-X','PICOMOTOR-Y']:
            pltData.sort(keys=['x_position'])
            ax2.set_ylabel('Scan Location ('+ header.x_unit + ')')
        elif par['GROUP_NAME_1'] == 'ROT_STAGE':
            pltData.sort(keys=['theta_position'])
            ax2.set_ylabel('Scan Location ('+ header.theta_unit + ')')

        ax.cla()
        ax2.cla()
        ax.plot(times*1e6, average*header.calib)  
        ax.set_xlim((0,max(times)*1e6))
        ax2.imshow(pltData,extent=[0,max(times)*1e6,x,par['I1']],cmap=par['MAP'],aspect='auto')
        ax.set_xlabel('Time (us)')

        if header.calib_unit.rstrip() == 'nm/V':
            ax.set_ylabel('Displacement (nm)')
        elif header.calib_unit.rstrip() == 'mm/s/V':
            ax.set_ylabel('Particle Velocity (mm/s)')

        ax2.set_xlabel('Time (us)')
        ax.set_xlim((0,max(times)*1e6))
        fig.canvas.draw()
    
    def close(self,instruments,par):
        for device in instruments:
            if device == 'POLYTEC':
                Polytec().closeConnection() 
            if device == 'QUANTA_RAY':
                QSW().set(cmd='SING') # trn laser to single shot
                QuantaRay().off()
                QuantaRay().closeConnection()
            if device in ['PICOMOTOR-X','PICOMOTOR-Y']:
                PMot().close()
            if par['DIMENSIONS'] == 1 and device in ['SHORT_STAGE','LONG_STAGE','ROT_STAGE']:
                par['XPS_1'].TCP__CloseSocket(par['SOCKET_ID_1'])
                print 'Connection to %s closed'%par['GROUP_NAME_1']
            if par['DIMENSIONS'] == 2 and device in ['SHORT_STAGE','LONG_STAGE','ROT_STAGE']:
                par['XPS_2'].TCP__CloseSocket(par['SOCKET_ID_2'])
                print 'Connection to %s closed'%par['GROUP_NAME_2']
                
class Scan:

    def __init__(self):
        pass

    def point(self, par, header):
        '''Record a single trace'''
        print 'recording trace...'

        times, header = Execute().get_times(par['CONTROL'],par['CHANNEL'],header)
    
        Execute().update_header(header,par['I1'])
        
        # capture data
        average = Execute().data_capture(par['CONTROL'],par['CHANNEL'])
        
        Execute().plot(header,times,average)
        
        Execute().save_trace(header,average,par['FILENAME'])

        print 'Trace recorded!'
        print 'data saved as: %s \n '%par['FILENAME']

    def oneD(self, par, header):

        '''Scanning function for 1-stage scanning'''

        #QSW().set(cmd='REP') # turn laser on repetitive shots
        #QRstatus().getStatus() # send command to laser to keep watchdog happy

        print 'beginning 1D scan...'
      
        times, header = Execute().get_times(par['CONTROL'],par['CHANNEL'],header)

        tracenum = 0
        if par['I1'] > par['F1']:
            par['D1'] = -par['D1']
       
        x = par['I1']
        
        totalTime = par['TOTAL_TIME']

        if par['GROUP_NAME_1'] == 'ROT_STAGE':
            unit = 'degrees'
        # set up mirrors        
        elif par['GROUP_NAME_1'] in ['PICOMOTOR-X','PICOMOTOR-Y']:
            theta_step = 1.8e-6 # 1 step = 1.8 urad
            print 'Go to starting position for picomotors'
            PMot().Position(par['PX'],par['PY'])
            # set position to 'zero'
            PMot().set_DH(par['PX'])
            PMot().set_DH(par['PY'])
            if par['RECEIVER'] == 'polytec':
                PolytecSensorHead().autofocusVibrometer(span='Full')
                #focusLength = float(PolytecSensorHead().getFocus())*0.5+258 # (experimental linear relationship for focusLength in mm)
                L = par['MIRROR_DISTANCE']
                unit = 'mm'
            else:
                L = par['MIRROR_DISTANCE']
                unit = 'radians'
            par['I1'] = float(par['I1'])/(L*theta_step)
            par['D1'] = float(par['D1'])/(L*theta_step)
            print 'group name 1 %s' %par['GROUP_NAME_1']
            if par['GROUP_NAME_1'] == 'PICOMOTOR-X': 
                PMot().move_rel(par['PX'],par['I1'])
            else:
                PMot().move_rel(par['PY'],par['I1'])                              
        else:
            unit = 'mm'

        # setup plot
        ax, ax2, fig = Initialize().two_plot(par['GROUP_NAME_1'], header)
        i = 0    
        
        while i < par['TOTAL_TRACES_D1']:  

            tracenum += 1
            print 'trace ', tracenum, ' of', par['TOTAL_TRACES_D1']

            # move stage/mirror
            if par['GROUP_NAME_1'] in ['PICOMOTOR-X','PICOMOTOR-Y']:
                x_steps = x/theta_step
                if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
                    PMot().move_rel(par['PX'],par['D1'])
                    pos = atof(PMot().get_TP(par['PX']))*L*theta_step   
                elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
                    PMot().move_rel(par['PY'],par['D1'])
                    pos = atof(PMot().get_TP(par['PY']))*L*theta_step
            else:
                Execute().move_stage(par['GROUP_NAME_1'],par['XPS_1'],par['SOCKET_ID_1'],x)
                pos = x

            Execute().update_header(header, pos, par['GROUP_NAME_1'])
            print 'position = %s %s' %(pos,unit)
            sleep(par['WAITTIME']) # delay after stage movement

            #Execute().check_vibfocus(par['CHANNEL'],par['VIB_SIGNAL'],par['SIGNAL_LEVEL'])
 
            average = Execute().data_capture(par['CONTROL'],par['CHANNEL'])
            
            # save current trace
            Execute().save_trace(header,average,par['FILENAME'])

            # update figure
            if par['MAP'] != 'none' and i > 0:
                Execute().update_two_plot(times, average, x, par, header, fig, ax, ax2)
            
            Execute().update_time(par)

            x += par['D1']
            i += 1
           
            #QRstatus().getStatus() # send command to laser to keep watchdog happy
        if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
            PMot().move_abs(par['PX'],0)
            print 'picomotors moved back to zero.'
        elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
            PMot().move_abs(par['PY'],0)
            print 'picomotors moved back to zero.'
        print 'scan complete!'
        print 'data saved as: %s \n'%par['FILENAME']     

    def twoD(self,par,header):
        '''
        Scanning function for 2-stage scanning.
        '''
        
        print 'beginning 2D scan...'
      
        times, header = Execute().get_times(par['CONTROL'],par['CHANNEL'],header)
        
        tracenum = 0                                 
    
        if par['I1'] > par['F1']:
            par['D1'] = -par['D1']       
        x = par['I1']
        
        if par['I2'] > par['F2']:
            par['D2'] = -par['D2']
        y = par['I2']

        totalTime = par['TOTAL_TIME']

        # set up mirrors 
        if par['GROUP_NAME_1'] in ['PICOMOTOR-X','PICOMOTOR-Y'] or par['GROUP_NAME_2'] in ['PICOMOTOR-X','PICOMOTOR-Y']: 
            theta_step = 2.265e-6 # 1 step or count = 26 urad
            print 'Go to starting position for picomotors'
            PMot().Position(par['PX'],par['PY'])
            print 'done moving'
            # set current position to zero/home
            PMot().set_DH(par['PX'])
            PMot().set_DH(par['PY'])
            
        if par['GROUP_NAME_1'] == 'ROT_STAGE':
            unit1 = 'degrees'
        elif par['GROUP_NAME_1'] in ['PICOMOTOR-X','PICOMOTOR-Y']:
            if par['RECEIVER'] == 'polytec':
                PolytecSensorHead().autofocusVibrometer(span='Full')
                #focusLength = float(PolytecSensorHead().getFocus())*0.5+258 # (experimental linear relationship for focusLength in mm)
                L = par['MIRROR_DISTANCE']
                unit1 = 'mm'
            else:
                L = par['MIRROR_DISTANCE']
                unit1 = 'radians'
            pos1 = 0
            par['I1'] = par['I1']/(L*theta_step)
            par['D1'] = par['D1']/(L*theta_step)
            
        else:
            unit1 = 'mm'

        if par['GROUP_NAME_2'] == 'ROT_STAGE':
            unit2 = 'degrees'
        elif par['GROUP_NAME_2'] in ['PICOMOTOR-X','PICOMOTOR-Y']:
            if par['RECEIVER'] == 'polytec':
                PolytecSensorHead().autofocusVibrometer(span='Full')
                #focusLength = float(PolytecSensorHead().getFocus())*0.5+258 # (experimental linear relationship for focusLength in mm)
                L = par['MIRROR_DISTANCE']
                unit2 = 'mm'
            else:
                L = par['MIRROR_DISTANCE']
                unit2 = 'radians'
            pos2= 0
            par['I2'] = par['I2']/(L*theta_step)
            par['D2'] = par['D2']/(L*theta_step)
            
        else:
            unit2 = 'mm'

        if par['GROUP_NAME_1'] in ['SHORT_STAGE','LONG_STAGE','ROT_STAGE']:
            pos1 = Execute().move_stage(par['GROUP_NAME_1'],par['XPS_1'],par['SOCKET_ID_1'],x)
        if par['GROUP_NAME_2'] in ['SHORT_STAGE','LONG_STAGE','ROT_STAGE']:
            pos2 = Execute().move_stage(par['GROUP_NAME_2'],par['XPS_2'],par['SOCKET_ID_2'],x)
        
        i = 0
        j = 0

        while i < par['TOTAL_TRACES_D1']:  
            print 'num traces d1', par['TOTAL_TRACES_D1']
            print 'trace %s of %s' %(tracenum,par['TOTAL_TRACES_D1']*par['TOTAL_TRACES_D2'])
        
            if i > 0:
                if par['GROUP_NAME_1'] == 'PICOMOTOR-X':
                    PMot().move_rel(par['PX'],par['D1'])
                    pos1 = atof(PMot().get_TP(par['PX']))*L*theta_step
                elif par['GROUP_NAME_1'] == 'PICOMOTOR-Y':
                    PMot().move_rel(par['PY'],par['D1'])
                    pos1 = atof(PMot().get_TP(par['PY']))*L*theta_step          
                else:
                    pos1 = Execute().move_stage(par['GROUP_NAME_1'],par['XPS_1'],par['SOCKET_ID_1'],x)

            Execute().update_header(header, pos1 ,par['GROUP_NAME_1'])
            
            print 'dimension 1 = %s %s ' %(pos1,unit1)

            sleep(par['WAITTIME']) # delay after stage movement

            while j < par['TOTAL_TRACES_D2']:  
                print 'num traces d2', par['TOTAL_TRACES_D2']
                tracenum +=1
                print 'trace %s of %s' %(tracenum,par['TOTAL_TRACES_D1']*par['TOTAL_TRACES_D2'])
                             
                if j > 0:
                    print 'j=',j
                    if par['GROUP_NAME_2'] == 'PICOMOTOR-X':
                        PMot().move_rel(par['PX'],par['D2'])
                        pos2 = atof(PMot().get_TP(par['PX']))*L*theta_step
                    elif par['GROUP_NAME_2'] == 'PICOMOTOR-Y':
                        PMot().move_rel(par['PY'],par['D2'])
                        pos2 = atof(PMot().get_TP(par['PY']))*L*theta_step
                    else:
                        pos2 = Execute().move_stage(par['GROUP_NAME_2'],par['XPS_2'],par['SOCKET_ID_2'],y)

                Execute().update_header(header, pos2, par['GROUP_NAME_2'])

                print 'dimension 2 = %s %s '%(pos2,unit2)

                sleep(par['WAITTIME']) # delay after stage movement

                #Execute().check_vibfocus(par['CHANNEL'],par['VIB_SIGNAL'],par['SIGNAL_LEVEL'])
                
                average = Execute().data_capture(par['CONTROL'],par['CHANNEL'])
                
                # save current trace
                Execute().save_trace(header,average,par['FILENAME'])

                Execute().update_time(par)
                
                y += par['D2']
                j += 1

            x += par['D1']
            
            # move stage/mirror to starting position
            y = par['I2']
        
            if par['GROUP_NAME_2'] == 'PICOMOTOR-X':
                PMot().move_abs(par['PX'],float(y))
                #PMot().set_OR(par['PX'])
                pos2 = atof(PMot().get_TP(par['PX']))*L*theta_step
            elif par['GROUP_NAME_2'] == 'PICOMOTOR-Y':
                #PMot().set_OR(par['PY'])
                PMot().move_abs(par['PY'],float(y))
                pos2 = atof(PMot().get_TP(par['PY']))*L*theta_step
            else:
                pos2 = Execute().move_stage(par['GROUP_NAME_2'],par['XPS_2'],par['SOCKET_ID_2'],y)
            j = 0
            i += 1

        print 'scan complete!'
        print 'data saved as: %s \n'%par['FILENAME']    
