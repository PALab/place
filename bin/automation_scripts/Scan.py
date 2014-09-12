'''
Master script to run laser-ultrasound experiment using PLACE automation.

1. Instruments are initialized
2. Header is created
3. Scan: data is acquired, displayed, and appended to stream file for each stage position
  - Data is saved to an HDF5 file (e.g. filename.h5) in the same folder as Scan.py:
4. Connection to instruments are closed

-------------------------
Command line options:
-------------------------

-r --sampleRate=
        define the sample rate.  Supply an integer with
        suffix, e.g. 100K for 10e5 samples per second or 1M for 10e6 samples per second (Max of 125M).
        options: 1K, 2K, 5K, 10K, 20K, 50K, 100K, 100K, 500K, 1M, 2M, 5M, 10M, 20M, 25M, 50M, 100M, 125M
        Example: -r 25M for 25 megasamples/second
        Default: 100 kSamples/second
-t --timeDuration=
        define total time to record each trace in microseconds. 
        Example: -t 100 for 100 us.
        Default: 100 us.
        *NOTE: number of samples will be rounded to next power of two to avoid scrambling data
-c --channel=
        define the channel that will be used to acquire data.
        Example: -c A for channel A. 
        Default: Channel A
-a --averagedRecords=
        define the number of records that shall be averaged. 
        Example: -a 100 to average 100 records
        Default: 64 averages
-s --stage=
        define which stage to use. rot = rotation, lin = linear, none = no stage. If no stage used, a single trace will be recorded. 
        Example: -s rot to use the rotation stag. 
        Default: linear stage
-w --waitTime=
       time to stall after each stage movement.
       Example: -w 2 to stall 2 seconds
       Default: 0
-v --receiver=
       define which receiver to use. polytec, gclad, paldv
       Example: -v gclad
       Default: polytec
-z --sigLevel=
       define suitable polytec signal level (range ~0 to 1.1)
       Example: -z 0.50 for signal level 0.5
       Default: 0.90
-u --vibChannel=
       define oscilloscope card channel for polytec signal level     
       Example: -c B for channel B. 
       Default: null
-l --trigLevel=
        trigger level in volts.  
        Example: -l 2 for a trigger level of +2 V
        Default: 1V
-q, --trigRange=
        input range for external trigger. 
        Example: -q 4 for +/- 4V trigger range.
        Default: 4
-y --channelRange=
        input range of acquisition channel. 
        options: 100_MV, 200_MV, 400_MV, 1_V, 2_V, 4_V
        Example: -v 4 for a input range of +/- 4 V
        Default: +/- 2V
-p --coupling=
        AC for AC coupling, DC for DC coupling.  
        Example: -p AC. 
        Default: DC coupling.
-o --ohms=
        set impedance of oscilloscope card
        50 for 50 ohm impedance, 1 for 1Mohm impedance
        Example: -o 50
        Default: 50
-i --initialPosition=
        define the initial position for scan.  
        Example: -i 0 for a scan starting at position x = 0. 
        Default: 0 mm
-x --increment=
        define increment for scan. 
        Example: -d 1 for an increment of 1 mm. 
        Default: 1 mm
-f --finalPosition=
        define the final position for scan.  
        Example: -f 10 for a scan ending at position x = 10 mm. 
        Default: 0 mm
-n --fileName=
        define the base file name to save data to. 
        Example: -n Scan1 for image data to be saved to Scan1.h5 
        Default: TestScan.h5
-d --decoder=
        define decoder for Polytec vibrometer. Possible decoders are VD-08, VD-09, DD-300 (best for ultrasonic applications), and DD-900.  
        Example: -d 'DD-300'
        Default: DD-300 decoder
-g --range= 
        define range of decoder of Polytec vibrometer.  Specify both the value and unit length for the appropriate 
        Example: -g 5mm specifies a range of 5 mm/s/V. 
        Default: 5 mm/s/V
-k --map=
        define colormap to use during scan to display image.  
        Example: --map='jet' to use jet colormap
        Default: 'gray'
-e --energy= 
        specify the energy of the source used (in mJ).  
        Example: -e 100 specifies a 100 mJ source energy
        Default: 0 mJ
        *NOTE: the source laser energy must be manaually set on the laser power supply.  This value is for documentation purposes, only.
-m --comments=
        add any extra comments to be added to the trace headers.  
        Example: --comments='Energy at 50.  Phantom with no tube.'
        *NOTE: you must have either '  ' or "  " surrounding comments

FULL EXAMPLE 
python Scan.py -t 256 -a 10 -s lin -i -10 -x 1 -f 10 -d DD-300 -g 5mm -n TestScan -e 50 --comments='Experiment on sample with laser source and vibrometer receiver'

FOR RACHEL:
python Scan.py -t 256 -c B -a 200 -s rot -i 0 -x 1 -f 180 -n S5-V -d DD-300 -g 5mm -e 200 --comments=''

FOR JACKSON:
python Scan.py -t 500 -c B -a 200 -s lin -i 20 -x 1 -f -40 -n aluminum_shotgather -d DD-300 -e 200 --comments='Jackson test'

new shale
python Scan.py -t 256 -c B -a 200 -s rot -i 195 -x 1 -f 179 -n S5H-jacket -d DD-300 -e 200 --comments='S5-H shale with jacket'

for wood:
python Scan.py -t 256 -c B -a 200 -s lin -i -80 -x 0.5 -f 110 -d DD-300 -g 5mm -e 50 -n wood_aluminum_source --comments='wood scan.  source and receiver aligned with aluminum tape on source side.'

rotational scan (Jackson):
python Scan.py -t 200 -c B -a 200 -s rot -i 0 -x 1 -f 180 -n S3-rot -d DD-300 -g 5mm -k 'gray' -e 200 --comments='Beam diameter 3.5 mm'


Miriam's air gap scan:
python Scan.py -r 1M -t 400 -c A -a 500 -s lin -i -140 -x 10 -f -40 -n air_scan -d DD-300 --comments='Transducer only.  10 cm air gap scan.  500 khZ.  Current = 75 mA (fiber laser).'

# XPS Controller:
# STATIC IP: 192.168.0.254 (direct connect)
# DYNAMIC IP: "130.216.55.92"

@author: Jami L Johnson
September 8, 2014
'''

import sys
import os
os.system('sudo chmod -R 0777 /dev/ttyS0') # set permissions of RS-232 serial port for vibrometer control
os.system('sudo chmod a+rw /dev/ttyS0')
os.system('sudo chmod -R 0777 /dev/ttyUSB1')
os.system('sudo chmod a+rw /dev/ttyUSB1')


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
from string import atoi
from time import sleep

# PLACE modules
import place.automate.osci_card.controller as card
from place.automate.xps_control.XPS_C8_drivers import XPS
from place.automate.polytec.vibrometer import Polytec, PolytecDecoder, PolytecSensorHead
from place.automate.quanta_ray.QRay_driver import QuantaRay, QSW, QRread, QRstatus, QRcomm
from place.automate.scan.scanFunctions import initialize, checks 

def main():
    
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:r:t:c:a:s:w:v:z:u:l:q:y:p:o:i:x:f:n:d:g:k:e:m', ['help', 'sampleRate=', 'timeDuration=', 'channel=', 'averagedRecords=', 'stage=','waitTime','receiver=', 'sigLevel','vibChannel','trigLevel=','trigRange=','channelRange=','coupling=', 'ohms=', 'initialPosition=', 'increment=', 'finalPosition=', 'fileName=', 'decoder=', 'range=','map=', 'energy=','comments='])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    # default values
    global us, xps, socketId, receiver # for keyboard interrupt handling

    sampleRate = 'SAMPLE_RATE_10MSPS'
    channel = 'CHANNEL_A'
    vibChannel = 'null'
    averagedRecords = 64    
    duration = 256
    filename = 'TestScan.h5'
    GroupName = 'SingleH' #linear stage
    stage = 'Linear Stage'
    waitTime = 0
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
    ohms=50
    trigLevel=1
    trigRange=4 
    channelRange='INPUT_RANGE_PM_2_V'
    us = 1e6
    timeDelay = 0
    maxFreq = '6MHz'
    minFreq = '0MHz'
    calib = 1
    calibUnit = 'null'
    sigLevel = 0.90 # vibrometer signal level
    receiver = 'polytec'
    
   # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-r", "--sampleRate"):
            sampleRate = "SAMPLE_RATE_" + a + "SPS" 
        if o in ("-t", "--timeDuration"):
            duration = float(a)
        if o in ("-c", "--channel"):
            channel = "CHANNEL_" + str(a) 
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
        if o in ('-w','--waitTime'):
            waitTime = float(a)
        if o in ('-v', '--receiver'):
            receiver = str(a)
        if o in ('-z', '--sigLevel'):
            sigLevel = float(a)
        if o in ('-u','--vibChannel'):
            vibChannel = "CHANNEL_" + str(a) 
        if o in ("-l", "--trigLevel"):
            trigLevel = float(a)
        if o in ("-q", "--trigRange"):
            trigRange = float(a)
        if o in ("-y", "--channelRange"):
            channelRange = "INPUT_RANGE_PM_" + str(a)
        if o in ("-p", "--coupling"):
            if a == 'AC':
                ACcouple = True
            elif a == 'DC':
                ACcouple = False
        if o in ("-o", "--ohms"):
            ohms = int(a)
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

    # -----------------------------------------------------
    # initialize instruments
    # -----------------------------------------------------

    # initialize XPS stage controller
    [GroupName, xps, socketId] = initialize().Controller('130.216.55.92',GroupName, Positioner, xi)

    # initialize and set header information for receiver
    if receiver == 'polytec':
        [timeDelay, maxFreq, calib, calibUnit] = initialize().Polytec(portPolytec,baudPolytec, decoder, drange)
    elif receiver == 'gclad':
        maxFreq = '6MHz'
        minFreq = '50kHz'
        timeDelay = 'air gap dependent'
        decoder = ''
        drange = ''
        calib = '1'
        calibUnit = 'V'
    elif receiver == 'paldv':
        maxFreq = ''
        minFreq = ''
        timeDelay = 0
        decoder = ''
        drange = ''
        calib = ''
        calibUnit = 'V'
        
    # initialize oscilloscope card
    [samples, control, vibSignal] = initialize().OsciCard(channel, vibChannel, sampleRate, duration, averagedRecords,trigLevel, trigRange, channelRange, ACcouple, ohms)
   
    # initialize Quanta-Ray source laser
    traceTime = initialize().QuantaRay(portINDI='/dev/ttyUSB1',percent=energy,averagedRecords=averagedRecords)

    totalTraces = int(abs((xf-xi))/dx)+1

    # -----------------------------------------------------
    # initialize header
    # -----------------------------------------------------

    header = initialize().Header(averagedRecords=averagedRecords, channel=channel, ohms=ohms, receiver=receiver, decoder=decoder, drange=drange, timeDelay=timeDelay, energy=energy, maxFreq=maxFreq, minFreq=minFreq, position='0', position_unit=unit, calib=calib, calibUnit=calibUnit, comments=comments)

    # -----------------------------------------------------
    # perform scan
    # -----------------------------------------------------

    scan(channel, vibChannel, control, vibSignal, sigLevel, GroupName, xps, socketId, xi, dx, xf, totalTraces, traceTime, waitTime, mapColor, filename, header, receiver)

    # -----------------------------------------------------
    # close instrument connections
    # -----------------------------------------------------
   
    xps.TCP_CloseSocket(socketId)
    print 'Connection to XPS controller closed'

    if receiver == 'polytec':
        Polytec().closeConnection()

    QSW().set(cmd='SING') # turn laser to single shot
    QuantaRay().off()
    QuantaRay().closeConnection()


def scan(channel, vibChannel, control, vibSignal, sigLevel, GroupName, xps, socketId, xi, dx, xf, totalTraces, traceTime, waitTime, mapColor, filename, header, receiver):   
    '''Scanning function for 1-stage scanning'''

    QSW().set(cmd='REP') # turn laser on repetitive shots
    QRstatus().getStatus() # send command to laser to keep watchdog happy

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

    if xi > xf:
        xtemp = xf
        xf = xi
        xi = xtemp
   
    totalTime = traceTime*totalTraces

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

        sleep(waitTime) # delay after stage movement
            
        # check focus of vibrometer sensor head
        if receiver == 'polytec':
            signal = checks().vibrometerFocus(vibChannel, vibSignal, sigLevel)
            header.focus = signal
 
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
            ax.plot(times*us, average*header.calib)  
            ax2.imshow(pltData,extent = [0,max(times)*us,x,xi],cmap=mapColor,aspect='auto')
            ax.set_xlabel('Time (us)')
            if header.calib_unit.rstrip() == 'nm/V':
                ax.set_ylabel('Displacement (nm)')
            elif header.calib_unit.rstrip() == 'mm/s/V':
                ax.set_ylabel('Particle Velocity (mm/s)')
            ax2.set_ylabel('Scan Location ('+ header.position_unit + ')')
            ax2.set_xlabel('Time (us)')
            fig.canvas.draw()

        # calculate time remaining
        totalTime -= traceTime  
        hourLeft = int(totalTime/3600)
        lessHour = totalTime - hourLeft*3600
        minLeft = int(lessHour/60)
        secLeft = int(lessHour - minLeft*60)
        print str(hourLeft) + ':' + str(minLeft) + ':' + str(secLeft) + ' remaining'

        x += dx
        QRstatus().getStatus() # send command to laser to keep watchdog happy
   
    print 'scan complete!'
    print 'data saved as: ', filename


if __name__ == "__main__":
    try:
        while(True):
            main()
    except KeyboardInterrupt:
        print 'Keyboard Interrupt!  Instrument connections closing...'
        xps.TCP_CloseSocket(socketId)
        print 'Connection to XPS controller closed'
        QSW().set(cmd='SING') # turn laser to single shot
        QuantaRay().off()
        QuantaRay().closeConnection()
        if receiver == 'polytec':
            Polytec().closeConnection()
