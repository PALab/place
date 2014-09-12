'''
Master script to record a single trace experiment using PLACE automation.

1. Instruments are initialized
2. Header is created
3. Shot is recorded
 - Data is saved to an HDF5 file (e.g. filename.h5) in same folder as Shot.py
4. Instrument connections are closed

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
       Default: Channel B
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
-e --energy= 
        specify the energy of the source used (in mJ).  
        Example: -e 100 specifies a 100 mJ source energy
        Default: 0 mJ
        *NOTE: the source laser energy must be manaually set on the laser power supply.  This value is for documentation purposes, only.
-m --comments=
        add any extra comments to be added to the trace headers.  
        Example: --comments='Energy at 50.  Phantom with no tube.'
        *NOTE: you must have either '  ' or "  " surrounding comments

FULL EXAMPLE:
python Shot.py -r 1M -t 256 -c A -a 200 -v polytec -d DD-300 -z 0.8 -u B -n Testing123 -d DD-300 -g 5mm -e 100  

For Apple:
python Shot.py -r 1M -t 50000 -c B -a 500 -n Apple2_day3 -d VD-09 -g 5mm --comments='Apple2 day 3 pos =180'

FOR SAM:
python Shot.py -t 200 -c B -a 200 -n H21 -v polytec -d VD-09 -g 50mm --comments='Transducer, 250 kHz.'

@author: Jami L Johnson 
September 8, 2014
'''

import sys
import os
os.system('sudo chmod -R 0777 /dev/ttyS0') # set permissions of vibrometer port
os.system('sudo chmod a+rw /dev/ttyS0')

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

# PLACE modules
import place.automate.osci_card.controller as card
from place.automate.xps_control.XPS_C8_drivers import XPS
from place.automate.polytec.vibrometer import Polytec, PolytecDecoder, PolytecSensorHead
from place.automate.scan.scanFunctions import initialize, checks

def main():
    
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:r:t:c:a:v:z:u:l:q:y:p:o:n:d:g:e:m', ['help', 'sampleRate=', 'timeDuration=', 'channel=', 'averagedRecords=', 'receiver=', 'sigLevel','vibChannel','trigLevel=','trigRange=','channelRange=','coupling=', 'ohms=', 'fileName=', 'decoder=', 'range=','energy=','comments='])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    # default values
    global receiver
    sampleRate = 'SAMPLE_RATE_10MSPS'
    channel = 'CHANNEL_B'
    vibChannel = 'CHANNEL_A'
    averagedRecords = 64    
    duration = 256
    filename = 'TestScan.h5'
    waitTime = 0
    mapColor = 'gray'
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
    global us
    us = 1e6
    timeDelay = 0
    maxFreq = '6MHz'
    minFreq = '0MHz'
    calib = 1
    calibUnit = 'null'
    unit = 'null'
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
    
    # initialize and set header information for receiver
    if receiver == 'polytec':
        [timeDelay, maxFreq, calib, calibUnit] = initialize().Polytec(portPolytec,baudPolytec, decoder, drange)
    elif receiver == 'gclad':
        maxFreq = '6MHz'
        minFreq = '50kHz'
        timeDelay = 'air gap dependent'
        decoder = ''
        drange = ''
        calib = ''
        calibUnit = 'V'
    elif receiver == 'paldv':
        maxFreq = ''
        minFreq = ''
        timeDelay = 0
        decoder = ''
        drange = ''
        calib = '52'
        calibUnit = 'mm/s/V'
    
    # initialize oscilloscope card
    [samples, control, vibSignal] = initialize().OsciCard(channel, vibChannel, sampleRate, duration, averagedRecords,trigLevel, trigRange, channelRange, ACcouple, ohms)   
    
    # initialize header
    header = initialize().Header(averagedRecords, channel, ohms, receiver, decoder, drange, timeDelay, energy, maxFreq, minFreq, unit, calib, calibUnit, comments)
    
    # record and plot shot
    shot(channel, control, filename, header, receiver, vibChannel, vibSignal, sigLevel)

    # close instrument connections
    if receiver == 'polytec':
        Polytec().closeConnection()

def shot(channel, control, filename, header, receiver, vibChannel, vibSignal, sigLevel):
    '''Record a single trace'''
   
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
    plt.plot(times*us, average*header.calib)
    plt.xlim((0,max(times)*us))
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
    try:
        while(True):
            main()
    except KeyboardInterrupt:
        print 'Keyboard Interrupt!  Instrument connections closing...'
        if receiver == 'polytec':
            Polytec().closeConnection()
