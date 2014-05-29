'''
Program to run laser-ultrasound experiment using pyPAL.

1. Instruments are initialized
2. Header is created
3. Scan: data is acquired, plotted and appended to scan image at each stage position
4. Data is saved to same folder as Scan.py:
       -Image data is saved to HDF5 fil, e.g. 'filename.h5' 
5. Connection to instruments are closed

Command line options:

-r --sampleRate=
        define the sample rate. Attention only certain values are possible (check AlazarCmd.py). Supply an integer with
        suffix, e.g. 100K for 10e5 samples per second or 1M for 10e6 samples per second (Max of 125M).
        options: 1K, 2K, 5K, 10K, 20K, 50K, 100K, 100K, 500K, 1M, 2M, 5M, 10M, 20M, 25M, 50M, 100M, 125M
-t --timeDuration=
        define total time to record each trace in us. Example: -t 100 for 100 us 
        default = 100 us
-c --channel=
        define the channel that shall be recorded. Example: -c A for channel A. Default: Channel B
-l --trigLevel=
        trigger level in volts.  Example: -l 2 for a trigger level of +2 V
-q, --trigRange=
        input range for external trigger. Example: -q 4 for +/- 4V trigger range.
-v --channelRange=
        input range of acquisition channel. 
        options: 100_MV, 200_MV, 400_MV, 1_V, 2_V, 4_V
        Example: -v 4 for a input range of 4 V
-p --coupling=
        AC for AC coupling, DC for DC coupling.  Example: -p AC. Default is DC coupling.
-a --averagedRecords=
        define the number of records that shall be averaged. Example: -a 100 to average 100 records.
-s --stage=
        define which stage to use. rot = rotation, lin = linear, none = no stage. If no stage used, a single trace will be recorded. Example: -s rot to use the rotation stag. Default: linear stage
-i --initialPosition=
        define the initial position for scan.  Example: -i 0 for a scan starting at position x = 0. Default: 0 mm
-x --increment=
        define increment for scan. Example: -d 1 for an increment of 1 mm. Default: 1 mm
-f --finalPosition=
        define the final position for scan.  Example: -f 10 for a scan ending at position x = 10 mm. Default: 0 mm
-n --fileName=
        define the base file name to save data to. Example: -n Scan1 for image data to be saved to Scan1.h5 
        Default: TestScan.h5
-d --decoder=
        define decoder for Polytec vibrometer. Possible decoders are VD-08, VD-09, DD-300 (best for ultrasonic applications), and DD-900.  Example: -d 'DD-300'.  Default: 'DD-300'
-g --range= 
        define range of decoder of Polytec vibrometer.  Specify both the value and unit length for the appropriate Example: -g 5mm specifies a range of 5 mm/s/V. 
Default: '5 mm'
-k --map=
        define colormap to use during scan to display image.  Default: 'gray'
        Example: --map='jet' to use jet colormap
-e --energy= 
        specify the energy of the source used (in mJ).  Example: -e 100 specifies a 100 mJ source energy. 
        Default: 0 mJ
-m --comments=
        here you can add any extra comments to be added to the comments file.  Example: --comments='Energy at 50.  Phantom with no tube.'
        *NOTE: you must have either '  ' or "  " surrounding comments

FULL EXAMPLE 
python Scan.py -t 256 -a 10 -s lin -i -10 -x 1 -f 10 -d DD-300 -g 5mm -n TestScan -e 50 --comments='Transducer'

FOR RACHEL:
python Scan.py -t 256 -c B -a 200 -s rot -i 0 -x 1 -f 180 -n S5-V -d DD-300 -g 5mm -e 200 --comments=''

FOR SAM:
python Scan.py -t 200 -c B -a 200 -s none -n H21 -d VD-09 -g 50mm --comments='Transducer, 250 kHz.'

FOR JAMI:
python Scan.py -t 256 -c B -a 200 -s lin -i -20 -x 1 -f 20 -d DD-300 -g 5mm -e 100 -n phantom_aluminum --comments='Test aluminum tape fortape on phantom'

FOR JACKSON:
python Scan.py -t 500 -c B -a 200 -s lin -i 20 -x 1 -f -40 -n aluminum_shotgather -d DD-300 -e 200 --comments='Jackson test'

new shale
python Scan.py -t 256 -c B -a 200 -s rot -i 195 -x 1 -f 179 -n S5H-jacket -d DD-300 -e 200 --comments='S5-H shale with jacket'

for wood:
python Scan.py -t 256 -c B -a 200 -s lin -i -80 -x 0.5 -f 110 -d DD-300 -g 5mm -e 50 -n wood_aluminum_source --comments='wood scan.  source and receiver aligned with aluminum tape on source side.'

@author: Jami
'''
#source control--turn off after scan (y/n)
#update calib factor for DD-900 and VD
#add check for stage position to ensure moved!
import sys
import os
sys.path.append('/home/jami/LabSoftware/') # directory that python should search for Python packages
os.system('export LD_LIBRARY_PATH=/usr/lib/mpich2/lib/')
os.system('export PYTHONPATH=/home/jami/LabSoftware')
os.system('sudo chgrp permission /dev/ttyS0') # give permissions to communicate with serial RS-232 and USB port
os.system('sudo chmod 0060 /dev/ttyS0') # set permissions of RS-232 serial port for vibrometer control
os.system('sudo chmod a+rw /dev/ttyS0')
#os.system('sudo chgrp permission /dev/ttyUSB0') # USB = Quanta-Ray INDI
#os.system('sudo chmod 0060 /dev/ttyUSB0')
#os.system('sudo chmod a+rw /dev/ttyUSB0')

from math import ceil, log
import matplotlib.pyplot as plt 
import numpy as np
from numpy import matrix
import getopt
import time
from obspy import read, Trace, UTCDateTime
from obspy.core.trace import Stats
from obspy.core import AttribDict
import re
import h5py
import obspyh5

# pyPAL modules
import pypal.automate.osci_card.controller as card
from pypal.automate.xps_control.XPS_C8_drivers import XPS
from pypal.automate.polytec.vibrometer import Polytec, PolytecDecoder, PolytecSensorHead
#import osciCard.controller as card
#from polytec.vibrometer import Polytec, PolytecDecoder, PolytecSensorHead
#from XPSControl.XPS_C8_drivers import XPS

def main():
    
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:r:t:a:s:c:l:q:v:p:i:x:f:n:d:g:k:e:m', ['help', 'sampleRate=', 'timeDuration=' 'averagedRecords=', 'stage=', 'channel=','trigLevel=','trigRange=','channelRange=','coupling=', 'initialPosition=', 'increment=', 'finalPosition=', 'fileName=', 'decoder=', 'range=','map=', 'energy=','comments='])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    # default values
    sampleRate = 'SAMPLE_RATE_100KSPS'
    channel = 'CHANNEL_B'
    averagedRecords = 64    
    duration = 256
    filename = 'TestScan.h5'
    GroupName = 'SingleH' #linear stage
    stage = 'Linear Stage'
    unit = 'mm'
    Positioner = 'Pos'
    mapColor = 'gray'
    xi = 0 
    dx = 1
    xf = 0
    comments = ''
    portPolytec = '/dev/ttyS0'
    baudPolytec = 115200
    decoder = 'DD-300'
    drange = '5mm'
    energy = '0 mJ'
    ACcouple = False
    trigLevel=1
    trigRange=4 
    channelRange='INPUT_RANGE_PM_2_V'
 
   # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-r", "--sampleRate"):
            sampleRate = "SAMPLE_RATE_" + a + "SPS" 
        if o in ("-t", "--timeDuration"):
            duration = float(a)
        if o in ("-a", "--averagedRecords"):
            averagedRecords = int(a)
        if o in ("-s", "--stage"):
            if a == 'lin':
                GroupName = 'SingleH'
                stage = 'Linear Stage'
                unit = 'mm'
                unitCode = 1
                unitScalar = -3
            elif a == 'rot':
                GroupName = 'SpindleROT'
                stage = 'Rotational Stage'
                unit = 'deg'
                unitCode = 4
                unitScalar = 1
            elif a == 'none':
                unit = ' '
                stage = 'None'
            else: 
                print 'ERROR: invalid stage'
                exit()
        if o in ("-c", "--channel"):
            channel = "CHANNEL_" + str(a) 
        if o in ("-l", "--trigLevel"):
            trigLevel = float(a)
        if o in ("-q", "--trigRange"):
            trigRange = float(a)
        if o in ("-v", "--channelRange"):
            channelRange = "INPUT_RANGE_PM_" + str(a)
        if o in ("-p", "--coupling"):
            if a == 'AC':
                ACcouple = True
            elif a == 'DC':
                ACcouple = False
        if o in ("-i", "--initialPosition"):
            xi = float(a)
        if o in ("-x", "--increment"):
            dx = float(a)
        if o in ("-f", "--finalPosition"):
            xf = float(a)
        if o in ("-n", "--fileName"):
            filename = a + '.h5'
        if o in ("-d", "--decoder"):
            decoder = a
        if o in ("-g", "--range"):
            drange = a + '/s/V'
        if o in ("-k", "--map"):
            mapColor = str(a)
        if o in ("-e", "--energy"):
            energy = a + ' mJ'
        if o in ("-m", "--comments"):
            comments = a

    if stage == 'Linear Stage' or stage == 'Rotational Stage':
        [GroupName, xps, socketId] = initializeController(GroupName, Positioner, xi)
  
    [timeDelay, maxFreq, calib, calibUnit] = initializePolytec(portPolytec,baudPolytec, decoder, drange)
    
    samples = initializeOsciCard(channel, sampleRate, duration, averagedRecords,trigLevel, trigRange, channelRange, ACcouple)
  
    totalTraces = int(abs((xf-xi))/dx)+1

    header = initializeHeader(totalTraces, averagedRecords, channel, decoder, drange, timeDelay, energy, maxFreq, unit, calib, calibUnit, comments)

    if stage == 'Linear Stage' or stage == 'Rotational Stage':
        scan(channel, GroupName, xps, socketId, xi, dx, xf, totalTraces, mapColor, filename, header)

    elif stage == 'None':
        shot(channel, filename, header)
    
    if stage == 'Linear Stage' or stage == 'Rotational Stage':
        xps.TCP_CloseSocket(socketId)
        print 'Connection to XPS controller closed'

    Polytec().closeConnection()

def initializeController(GroupName, Positioner, xi):
    '''Function to initialize XPS controller and move to initial scan position'''
    xps = XPS()
    xps.GetLibraryVersion()

    # below: when hardwired to controller
    socketId = xps.TCP_ConnectToServer("192.168.0.254",5001,3)
    print "connected to: ", socketId
    #print xps.CloseAllOtherSockets(socketId) #NEED ADMINISTRATIVE RIGHTS (ERROR -107)

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

    xps.GroupKill(socketId, GroupName)
    InitializeGrpErr = xps.GroupInitialize(socketId, GroupName)
    if InitializeGrpErr[0] == 0:
        print 'group initialized'
    else:
        print 'group initialize failed: ERROR = ', InitializeGrpErr
    xps.GroupStatusGet(socketId, GroupName)
    
    HomeErr = xps.GroupHomeSearch(socketId, GroupName)
    if HomeErr[0] == 0:
        print 'home search successful'
    else:
        print 'home search failed: ERROR = ', HomeErr

    xps.GroupMoveAbsolute(socketId, GroupName, [xi])
    ck = 0 
    actualPos =  xps.GroupPositionCurrentGet(socketId, GroupName,1)
    while int(actualPos[1]*10**2)!= int(xi*10**2): # make sure stage actually moved
        xps.GroupMoveAbsolute(socketId, GroupName, [xi])
        if ck > 3: 
            print 'STAGE ERROR: restart program'
            exit()
        ck+=1
    print 'XPS stage initialized'

    return GroupName, xps, socketId

def initializePolytec(portPolytec, baudPolytec, decoder, drange):
    '''Function to initialize Polytec Vibrometer and obtain relevant parameters to save in trace headers'''
    # set decoder range
    Polytec(portPolytec, baudPolytec).openConnection() #runs __init__ and opens serial connection
    PolytecDecoder().setRange(decoder, drange)

    # calculate delay due to decoder
    delayString = PolytecDecoder().getDelay(decoder)
    delay =  re.findall(r'[-+]?\d*\.\d+|\d+', delayString) # get time delay in us
    timeDelay =  float(delay[0])

    # get maximum frequency recorded
    freqString = PolytecDecoder().getMaxFreq(decoder)
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
    decoderRange = PolytecDecoder().getRange(decoder)
    rangeNum = re.findall(r'[-+]?\d*\.\d+|\d+',decoderRange) 
    delNumR = len(rangeNum)+1
    calib = float(rangeNum[0])
    calibUnit = decoderRange[delNumR:].lstrip()

    # autofocus vibrometer
    PolytecSensorHead().autofocusVibrometer()

    return timeDelay, maxFreq, calib, calibUnit

def initializeOsciCard(channel, sampleRate, duration, averagedRecords, trigLevel, trigRange, channelRange, ACcouple):
    '''Function to initialize Alazar Oscilloscope Card'''
    global control, vibSignal

    # initialize channel for signal from vibrometer decoder
    control = card.TriggeredRecordingController()  
    control.configureMode = True
    control.createInput(channel=channel,inputRange=channelRange, AC=ACcouple)
    control.setSampleRate(sampleRate)  
    samples = control.samplesPerSec*duration*10**-6 
    samples = int(pow(2, ceil(log(samples,2)))) # round number of samples to next power of two
    control.setSamplesPerRecord(preTriggerSamples=0,postTriggerSamples=samples)
    control.setRecordsPerCapture(averagedRecords)
    triggerLevel = 128 + int(127*trigLevel/trigRange)
    control.setTrigger(operationType="TRIG_ENGINE_OP_J",sourceOfJ='TRIG_EXTERNAL',levelOfJ=triggerLevel) 
    control.setTriggerTimeout(10)  
    configureMode = False    

    # initialize channel for vubrometer sensor head signal
    vibSignal = card.TriggeredContinuousController()
    vibSignal.configureMode=True
    vibSignal.createInput(channel='CHANNEL_C',inputRange='INPUT_RANGE_PM_4_V', AC=False) # 0 to 3 V DC
    vibSignal.setSamplesPerRecord(preTriggerSamples=0,postTriggerSamples=1)
    vibSignal.setRecordsPerCapture(3)
    vibSignal.setTrigger(operationType="TRIG_ENGINE_OP_J",sourceOfJ='TRIG_EXTERNAL',levelOfJ=triggerLevel) 
    vibSignal.setTriggerTimeout(10)

    print 'oscilloscope card ready and parameters set'
    return samples

def initializeHeader(totalTraces, averagedRecords, channel, decoder, drange, timeDelay, energy, maxFreq, unit, calib, calibUnit, comments):
    '''Function to initialize data trace header information generic to all traces'''
    custom_header = Stats()
    custom_header.max_frequency = maxFreq
    custom_header.decoder = decoder
    custom_header.decoder_range = drange
    custom_header.source_energy = energy
    custom_header.position = 0
    custom_header.position_unit = unit
    custom_header.comments = comments
    custom_header.averages = averagedRecords
    custom_header.calib_unit = calibUnit
    custom_header.time_delay = timeDelay
    custom_header.scan_time = ''
    custom_header.focus = 0
    header = Stats(custom_header)
    header.calib = calib
    header.channel = channel

    return header

def scan(channel, GroupName, xps, socketId, xi, dx, xf, totalTraces, mapColor, filename, header):   

    '''Scanning function'''
    print 'beginning scan...'
    times = control.getTimesOfRecord()
    dt = times[1]-times[0]
    dataArray = times

    # setup plot
    plt.ion()
    plt.show()
    fig = plt.figure()     
    ax = fig.add_subplot(211)
    if header.calib_unit.rstrip() == 'nm/V':
        ax.set_ylabel('Displacement (nm)')
    elif header.calib_unit.rstrip() == 'mm/s/V':
        ax.set_ylabel('Particle Velocity (mm/s)')
    ax.set_xlabel('Time (us)')
    ax.set_title('Last Trace Acquired')
    ax2 = fig.add_subplot(212)
    ax2.set_ylabel('Scan Location ('+ header.position_unit + ')')
    ax2.set_xlabel('Time (us)')
        
    x = xi
    tracenum = 0
        
    if xi <= xf:

        start = time.time()

        while x < (xf+dx):  

            tracenum += 1
            print 'trace ', tracenum, ' of', totalTraces

            
            header.starttime = UTCDateTime()
            header.delta = dt
            header.position = x

            # move stage
            xps.GroupMoveAbsolute(socketId, GroupName, [x])
            actualPos = xps.GroupPositionCurrentGet(socketId, GroupName,1) 
            print 'x = ', actualPos[1]
    
            # check focus of vibrometer sensor head 
            vibSignal.startCapture()
            vibSignal.readData()
            signal = vibSignal.getDataRecordWise('CHANNEL_C')
            signal = np.average(signal,0)

            k = 0
            while signal < 0.90:
                print 'sub-optimal focus:'
                if k == 0:
                    PolytecSensorHead().autofocusVibrometer(span='Small')
                elif k == 1:
                    PolytecSensorHead().autofocusVibrometer(span='Medium')
                else: 
                    PolytecSensorHead().autofocusVibrometer(span='Full')
                vibSignal.startCapture()
                vibSignal.readData()
                signal = vibSignal.getDataRecordWise('CHANNEL_C')
                signal = np.average(signal,0)
                k+=1
                if k > 3:
                    print 'unable to obtain optimum signal'
                    break
    
            header.focus = float(signal)

            # capture data
            control.startCapture()  
            control.readData()
            records = control.getDataRecordWise(channel)
            average = np.average(records,0)    
 
            # save current trace
            header.npts = len(average)
            trace = Trace(data=average,header=header)
            trace.write(filename,'H5',mode='a')
            
            # plot data
            if x > xi:
                pltData = read(filename,'H5',calib=True)
                ax.cla()
                ax2.cla()
                ax.plot(times*1e6, average*header.calib)               
                ax2.imshow(pltData,extent = [0,max(times)*1e6,x,pltData[0].stats.position],cmap=mapColor,aspect='auto')
                ax.set_xlabel('Time (us)')
                if header.calib_unit.rstrip() == 'nm/V':
                    ax.set_ylabel('Displacement (nm)')
                elif header.calib_unit.rstrip() == 'mm/s/V':
                    ax.set_ylabel('Particle Velocity (mm/s)')
                ax2.set_ylabel('Scan Location ('+ header.position_unit + ')')
                ax2.set_xlabel('Time (us)')
                fig.canvas.draw()

            # calculate time remaining
            if x == xi:
                traceTime = time.time()-start
                totalTime = traceTime*totalTraces - traceTime
                header.scan_time = totalTime
            else:
                totalTime -= traceTime
          
            hourLeft = int(totalTime/3600)
            lessHour = totalTime - hourLeft*3600
            minLeft = int(lessHour/60)
            secLeft = int(lessHour - minLeft*60)
            print str(hourLeft) + ':' + str(minLeft) + ':' + str(secLeft) + ' remaining'

            x += dx
            
    else:
        start = time.time()

        while x > (xf-dx): 
          
            tracenum += 1
            print 'trace ', tracenum, ' of', totalTraces            
           
            header.starttime = UTCDateTime()
            header.delta = dt
            header.position = x

            # move stage
            xps.GroupMoveAbsolute(socketId, GroupName, [x])
            actualPos = xps.GroupPositionCurrentGet(socketId, GroupName,1) 
            print 'x = ', actualPos[1]    

            # check focus of vibrometer sensor head 
            vibSignal.startCapture()
            vibSignal.readData()
            signal = vibSignal.getDataRecordWise('CHANNEL_C')
            signal = np.average(signal,0)

            k = 0
            while signal < 0.90:
                print 'sub-optimal focus:'
                if k == 0:
                    PolytecSensorHead().autofocusVibrometer(span='Small')
                elif k == 1:
                    PolytecSensorHead().autofocusVibrometer(span='Medium')
                else: 
                    PolytecSensorHead().autofocusVibrometer(span='Full')
                vibSignal.startCapture()
                vibSignal.readData()
                signal = vibSignal.getDataRecordWise('CHANNEL_C')
                signal = np.average(signal,0)
                k+=1
                if k > 3:
                    print 'unable to obtain optimum signal'
                    break
        
            header.focus = float(signal)
  
            # capture data
            control.startCapture()     
            control.readData()
            records = control.getDataRecordWise(channel)
            average = np.average(records,0)
        
            # save current trace
            header.npts = len(average)
            trace = Trace(data=average,header=header)
            trace.write(filename,'H5',mode='a')

            # plot data
            if x < xi:
                pltData = read(filename,'H5',calib=True)
                ax.cla()
                ax2.cla()
                ax.plot(times*1e6, average*header.calib)
                ax2.imshow(pltData,extent = [0,max(times)*1e6,x,pltData[0].stats.position],cmap=mapColor,aspect='auto')
                ax.set_xlabel('Time (us)')
                if header.calib_unit.rstrip() == 'nm/V':
                    ax.set_ylabel('Displacement (nm)')
                elif header.calib_unit.rstrip() == 'mm/s/V':
                    ax.set_ylabel('Particle Velocity (mm/s)')
                ax2.set_ylabel('Scan Location ('+ header.position_unit + ')')
                ax2.set_xlabel('Time (us)')
                fig.canvas.draw()
            
            # calculate time remaining
            if x == xi:
                traceTime = time.time()-start
                totalTime = traceTime*totalTraces - traceTime
                header.scan_time = totalTime
            else:
                totalTime -= traceTime
          
            hourLeft = int(totalTime/3600)
            lessHour = totalTime - hourLeft*3600
            minLeft = int(lessHour/60)
            secLeft = int(lessHour - minLeft*60)
            print str(hourLeft) + ':' + str(minLeft) + ':' + str(secLeft) + ' remaining'

            x -= dx
            
    print 'scan complete!'
    print 'data saved as: ', filename

def shot(channel, filename, header):
    '''Function to record a single trace'''

    print 'recording trace...'

    times = control.getTimesOfRecord()
    dt = times[1]-times[0]
    header.starttime = UTCDateTime()
    header.delta = dt
    
    # capture data
    control.startCapture()  
    control.readData()
    records = control.getDataRecordWise(channel)
    average = np.average(records,0) 

    # plot trace
    plt.plot(times*1e6, average*header.calib)
    if header.calib_unit.rstrip() == 'nm/V':
        plt.ylabel('Displacement (nm)')
    elif header.calib_unit.rstrip() == 'mm/s/V':
        plt.ylabel('Particle Velocity (mm/s)')
    plt.xlabel('Time (us)')
    plt.show()

    header.npts = len(average)
    trace = Trace(data=average,header=header)
    trace.write(filename,'H5',mode='a')

    print 'Trace recorded!'
    print 'data saved as: ', filename

if __name__ == "__main__":
    main()
  

