'''
Example program to acquire data for while scanning stage.
1. Controller is initialized
2. Stage is moved to initial (absolute) position
3. Data acquisition parameters are set
4. Averaged data for one stage position is recorded and saved to TXT file
5. Stage is moved one increment
6. (4-5) repeated through final stage position
7. Connection to stage is closed

TODO: plot trace each time stage is moved
TODO: update image plot each time stage is moved

This module provides an examples how the osciCard module could be used. 

It acquires a certain number of records at moments when an external trigger signal rises over 0 V and displays the 
average of all records.

Command line options can be used to alter the behavior:

-r --sampleRate=
        define the sample rate. Attention only certain values are possible (check AlazarCmd.py). Supply an integer with
        suffix, e.g. 100K for 10e5 samples per second or 1M for 10e6 samples per second.
-c --channel=
        define the channel that shall be recorded. Example: -c A for channel A.
-n --numberOfRecords=
        define the number of records that shall be averaged. Example: -n 100 to average 100 records.

FULL EXAMPLE 
python exampleAcquire_Average_Save.py -r 100K -c B --numberOfRecords=10

@author: henrik
'''
#To do: get multiple averaged records to save until total number are saved
#Acquire averaged trace, save, move controller: repeat.
#plot in background
#save trace as specific file type (drop down menu?)

import osciCard.controller as card
import matplotlib.pyplot as plt 
import numpy as np
from numpy import matrix
import sys
import getopt

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:r:n:", ["help", "sampleRate=", "numberOfRecords=", "channel=" ])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # default values
    samplerate = "SAMPLE_RATE_100KSPS"
    averagedRecords = 50
    channel = "CHANNEL_A"
    basefilename = "test"
    xi = 0
    dx = 0
    xf = 0

    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-r", "--sampleRate"):
            samplerate = "SAMPLE_RATE_" + a + "SPS"
        if o in ("-n", "--numberOfRecords"):
            averagedRecords = int(a)
        if o in ("-c", "--channel"):
            channel = "CHANNEL_" + a

    #initializeStuff()

    xi = 0 #initial position of stage
    dx = 1 #increment for stage to move
    xf = 5 #final stage position

    #moveStageXi(socketId, xi) #move stage to initial position
 
    control = card.TriggeredContinuousController()  # get card handle
    control.configureMode = True  # go in configureMode; variables can be set without telling the card about it
    control.createInput(channel=channel)  # record on channel A
    control.setSampleRate(samplerate)  # record with 1e6 samples per second
    control.setTrigger(sourceOfJ="TRIG_EXTERNAL")  # use external signal for trigger
    control.setTriggerTimeout(0.1)  # set trigger time out
    control.setRecordsPerCapture(averagedRecords)
    control.configureMode = False  # leave configureMode; startCapture will run functions that configure the card
    control.startCapture()
    control.readData()
  
    fig = plt.figure()        
    ax = fig.add_subplot(111)
    ax.set_ylabel("Voltage [V]")
    ax.set_xlabel("Time [s]")
    fig.canvas.set_window_title("Last Trace Acquired")
    
    #numX = (xf-xi)+1
    #numY = 1024 #change to fit number of data samples?!
    #dataArray = np.zeros(shape=(numY,numX))
    dataArray = []
    x = xi
    #start for loop for stage 
    for x in range(xi,xf+1): 
         times = control.getTimesOfRecord()  # get the time of each sample in one record
         records = control.getDataRecordWise(channel)  # get the data in a list of records
         records = np.array(records)
         average = np.average(records, 0) 

         #save this trace to an array
         dataArray.append(average)
         
         # plot
         ax.plot(times, average)
         plt.show() 

         #next stage position
         #x = x+dx 
         #moveStage(socketId, x)

    
    #save file to TXT file
    finalArray = np.array(dataArray).T
    filename = basefilename + ".csv"
    print filename
    np.savetxt(filename, finalArray, delimiter=",")
    timesfilename = basefilename + "-times.csv"
    np.savetxt(timesfilename, times, delimiter=",")

    #Stop connection to controller
  #  xps.TCP_CloseSocket(socketId)
  #  print "connection to Controller finished."
 

def initializeStuff():
    from XPS_C8_drivers import XPS
    global xps
    xps = XPS()
    xps.GetLibraryVersion()
    global socketId
    socketId = xps.TCP_ConnectToServer("130.216.54.129",5001,3)
    print "connected to: ", socketId
    #print xps.CloseAllOtherSockets(socketId)
    xps.ControllerStatusGet(socketId)
    xps.Login(socketId, "Administrator", "Administrator")
    #print self.xps.GroupStatusListGet(self.socketId)
    print "Controller is initialized."

def moveStageXi(socketId, xi):
    global xps
    print xps.GroupMoveAbsolute(socketId,"GROUP1",[xi])

def moveStage(socketId, x):
    global xps
    print xps.GroupMoveAbsolute(socketId,"GROUP1",[x])


def doStuff():
    global xps
    #print self.xps.GroupKill(self.socketId, "GROUP3")
    #print self.xps.GroupInitialize(socketId, "GROUP3")
    #print self.xps.GroupStatusGet(socketId, "GROUP3")
    #print xps.GroupHomeSearch(socketId, "GROUP3")
    #print xps.GatheringConfigurationSet(socketId,["GROUP3.POSITIONER.CurrentPosition"])
    #print xps.GatheringRun(socketId, 1000, 100)
    #print xps.GroupHomeSearch(socketId, "GROUP3")
    print xps.GroupJogParametersSet(socketId, "GROUP1", [0.05], [1.])
    print 'Jog Command sent'
    #print xps.GroupMoveAbsolute(socketId, "GROUP3", [10.])
    #print xps.GatheringStopAndSave(socketId)
    #data= xps.GatheringDataGet(socketId, 1)
    #print xps.GatheringConfigurationGet(socketId)

    xps.TCP_CloseSocket(socketId)
    print "connection to Controller finished."

if __name__ == "__main__":
    main()
