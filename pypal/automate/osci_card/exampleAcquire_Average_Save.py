'''
Program for scanning with XPS controller.  Acquires, plots, and saves data for each controller position based on user defined parameters.

1. Controller is initialized
2. Oscilloscope card is initialized
3. Scan: data is acquired, plotted and appended to scan image at each controller position
4. Data is saved to directory folder:
       -Image data is saved to 'filename.csv'
       -Time vector is saved to 'filename-times.csv'
       -Comments file (with all scan parameters) is saved to 'filename-comments.csv'
       * Filetype can be changed manually
5. Connection to stage is closed

NOTE: this file must be in the same directory as 'XPS_C8_drivers.py', 'controller.py',Alazar

Command line options:

-r --sampleRate=
        define the sample rate. Attention only certain values are possible (check AlazarCmd.py). Supply an integer with
        suffix, e.g. 100K for 10e5 samples per second or 1M for 10e6 samples per second.
-c --channel=
        define the channel that shall be recorded. Example: -c A for channel A.
-v --numberAverages=
        define the number of records that shall be averaged. Example: -v 100 to average 100 records.
-i --initialPosition=
        define the initial position for scan.  Example: -i 0 for a scan starting at position x = 0.
-d --increment=
        define increment for scan. Example: -d 1 for an increment of 1 mm
-f --finalPosition=
        define the final position for scan.  Example: -f 10 for a scan ending at position x = 10 mm
-n --fileName=
        define the base file name to save data to. Example: -n Scan1 for image data to be saved to Scan1.csv and time vector to be saved to Scan1-times.csv

FULL EXAMPLE 
python exampleAcquire_Average_Save.py -r 100K -c B -v 16 -i 0 -d 1 -f 2 --fileName=testing 

@author: Jami
'''

import osciCard.controller as card
import matplotlib.pyplot as plt 
import numpy as np
from numpy import matrix
import sys
import getopt
import time

def main():
    global GroupName 
    global Positioner
    global channel
    global samplerate
    global averagedRecords
    global basefilename
    global filetype
    global xi
    global dx
    global xf

    # controller  factory-set options
    GroupName = 'Group1'
    Positioner = 'Pos'

    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:r:v:c:i:d:f:n', ['help', 'sampleRate=', 'numberAverages=', 'channel=', 'initialPosition=', 'increment=', 'finalPosition=', 'fileName='])
    except getopt.error, msg:
        print msg
        print 'for help use --help'
        sys.exit(2)

    # default values
    averagedRecords = 50    
    basefilename = 'TestScan'
    filetype = 'csv'
    xi = 0
    dx = 1
    xf = 0
   
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-r", "--sampleRate"):
            samplerate = "SAMPLE_RATE_" + a + "SPS"
        if o in ("-v", "--numberAverages"):
            averagedRecords = int(a)
        if o in ("-c", "--channel"):
            channel = "CHANNEL_" + a
        if o in ("-i", "--initialPosition"):
            xi = float(a)
        if o in ("-d", "--increment"):
            dx = float(a)
        if o in ("-f", "--finalPosition"):
            xf = float(a)
        if o in ("-n", "--fileName"):
            basefilename = a
        if o in ("-t", "--fileType"):
            filetype = a

    if (xf-xi)%dx != 0:
        print 'ERROR: Scanning range does not divide equally into chosen increments.' 
        exit()

    initializeController()
    initializeOsciCard()
    Scan()
    closeConnection()

def initializeController():
    from XPS_C8_drivers import XPS
    global xps
    global socketId

    xps = XPS()
    xps.GetLibraryVersion()

    # below: when hardwired to controller
    socketId = xps.TCP_ConnectToServer("192.168.0.254",5001,3)
    print "connected to: ", socketId
    #print xps.CloseAllOtherSockets(socketId) #NEED ADMINISTRATIVE RIGHTS (ERROR -107)

    ControllerErr = xps.ControllerStatusGet(socketId)
    if ControllerErr[0] == 0:
        print 'controller status ready'
    else:
        print 'controller status failed: ERROR =', ControllerErr

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

    print 'controller is initialized.'

def initializeOsciCard():
    global control

    control = card.TriggeredContinuousController()  
    control.configureMode = True  
    control.createInput(channel=channel)
    control.setSampleRate(samplerate)  
    control.setTrigger(sourceOfJ='TRIG_EXTERNAL')  
    control.setTriggerTimeout(0.1)  
    control.setRecordsPerCapture(averagedRecords)
    control.configureMode = False  
    print 'oscilloscope card is ready and parameters are set.'

def Scan():   
    print 'beginning scan'
    control.startCapture()
    control.readData()
    dataArray = []
    x = xi
    trace = 1
    totalTraces = int((xf-xi+1)/dx)

    # setup plot
    plt.ion()
    plt.show()
    fig = plt.figure()     
    ax = fig.add_subplot(211)
    ax.set_ylabel("Voltage [V]")
    ax.set_xlabel("Time [s]")
    ax.set_title('Last Trace Acquired')
    ax2 = fig.add_subplot(212)
    ax2.set_ylabel('Trace Number')
    ax2.set_xlabel('Time [s]')

    while x < (xf+1): 
        print 'trace ', trace, ' of', totalTraces
        xps.GroupMoveAbsolute(socketId, GroupName, [x])
        print 'x = ', x
        x += dx
        trace += 1
        print 'recording...'
        times = control.getTimesOfRecord()  
        records = control.getDataRecordWise(channel)  
        records = np.array(records)
        average = np.average(records, 0) 
        ax.plot(times, average)
        fig.canvas.draw()
        dataArray.append(average)
        ax2.imshow(dataArray,extent = [0,max(times),1,trace],aspect='auto')
        time.sleep(2)
     
    # save files 
    filename = basefilename + '.' + filetype
    print 'saving scan data to: ', filename 
    finalArray = np.array(dataArray).T
    np.savetxt(filename, finalArray, delimiter=",")
    
    timesfilename = basefilename + '-times.' + filetype
    print 'saving time vector to: ', timesfilename
    np.savetxt(timesfilename, times, delimiter=",")
'''    
    infofilename = basefilename + '-comments.txt'
    np.savetxt(infofilename, params)
    print 'scan complete!'
'''
    
def closeConnection():
    xps.TCP_CloseSocket(socketId)
    print 'connection to controller closed.' 

if __name__ == "__main__":
    main()

#    print xps.GroupJogModeEnable(socketId, GroupName)
#    print xps.GroupJogParametersSet(socketId, GroupName, [0.05],[1.]) #velocity, acceleration 
#    print xps.GroupJogParametersSet(socketId, GroupName, [0.0],[1.]) #stop
#    print xps.GroupJogParametersSet(socketId, GroupName, [0.0],[1.]) #velocit
#    print xps.GroupJogModeDisable(socketId, GroupName)
#    print 'velocity and acceleration set'
#print PositionerSGammaParametersSet(socketId,GroupName + '.' + Positioner, 0.05,0,
  #  print xps.GroupMotionEnable(socketId,GroupName)
#    [Err, Vel, Acc, MinJerkT, MaxJerkT] = xps.PositionerSGammaParametersGet(socketId,GroupName + '.' + Positioner)
#    print Err, Vel, Acc, MinJerkT, MaxJerkT
#    xps.PositionerSGammaParametersSet(socketId,GroupName + '.' + Positioner, 0.05, Acc, MinJerkT, MaxJerkT)   
    #print xps.GatheringStopAndSave(socketId)
    #data= xps.GatheringDataGet(socketId, 1)
    #print xps.GatheringConfigurationGet(socketId)


