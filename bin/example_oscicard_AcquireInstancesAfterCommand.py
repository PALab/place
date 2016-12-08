'''
This module is an example where a simple measurement is taken after calling an optional initialization and dummy 
function. The dummy function doStuff can be replaced by any function that needs to be executed before the acquisition. 
For example, doStuff could move an element of an experimental setup to a certain position. When this is done the 
measurement is taken.

Command line options can be used to alter the behavior:

-r --sampleRate=
        define the sample rate. Attention only certain values are possible (check AlazarCmd.py). Supply an integer with
        suffix, e.g. 100K for 10e5 samples per second or 1M for 10e6 samples per second.
-c --channel=
        define the channel that shall be recorded. Example: -c A for channel A.
-d --duration=
        define the duration in seconds over which shall be recorded. Example: -n 5.5 to record 5.5 seconds.

FULL EXAMPLE 
python oscicard_exampleAcquireInstancesAfterCommand.py -r 100K -c B --duration=10.


Created on Aug 14, 2013
@author: henrik
'''

import place.automate.osci_card.controller as card
import matplotlib.pyplot as plt 
import sys
import getopt

def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:r:n:d:", ["help", "sampleRate=", "numberOfRecords","channel=" , "duration="])
    except getopt.error as msg:
        print(msg)
        print("for help use --help")
        sys.exit(2)
    # default values
    samplerate = "SAMPLE_RATE_100KSPS"
    channel = "CHANNEL_A"
    duration = 5.
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        if o in ("-r", "--sampleRate"):
            samplerate = "SAMPLE_RATE_" + a + "SPS"
        if o in ("-n", "--numberOfRecords"):
            averagedRecords = int(a)
        if o in ("-c", "--channel"):
            channel = "CHANNEL_" + a
        if o in ("-d", "--duration"):
            duration = float(a)

 #   initializeStuff()
    control = card.ContinuousController()  # get card handle
    control.configureMode = True  # go in configureMode; variables can be set without telling the card about it
    control.createInput(channel=channel, inputRange="INPUT_RANGE_PM_4_V")  # record on channel A
    control.setSampleRate(samplerate)  # record with 1e6 samples per second
    control.setCaptureDurationTo(duration)
    control.configureMode = False  # leave configureMode; startCapture will run functions that configure the card
    times = control.getTimes()  # get the time of each sample in one record
  #  doStuff()  # call dummy function
    control.startCapture()
    control.readData()
    data = control.getDataAtOnce(channel)

    # plot
    fig = plt.figure()
   # plt.subplots_adjust(hspace=.5)
    ax = fig.add_subplot(111)
    ax.plot(times, data)
    ax.set_ylabel("voltage [V]")
    fig.canvas.set_window_title("Acquired Data")
    plt.xlabel("time [s]")
    plt.show()
    
def initializeStuff():
    from place.automate.xps_control.XPS_C8_drivers import XPS
    global xps
    xps = XPS()
    xps.GetLibraryVersion()
    global socketId
   # socketId = xps.TCP_ConnectToServer("130.216.54.129",5001,3)
    socketId = xps.TCP_ConnectToServer("192.168.0.254",5001,3)
    print("connected to: ", socketId)
    #print xps.CloseAllOtherSockets(socketId)
    xps.ControllerStatusGet(socketId)
    xps.Login(socketId, "Administrator", "Administrator")
    #print self.xps.GroupStatusListGet(self.socketId)
    print("Controller is initialized.")

def doStuff():
    print("Doing stuff before capture.")
    pass

if __name__ == '__main__':
    main()
