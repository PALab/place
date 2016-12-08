import place.automate.osci_card.controller as card
from place.automate.scan.scanFunctions import initialize, checks
from place.automate.new_focus.Picomotor_Driver import pMot
from place.automate.new_focus.Calibrate import Center, Position
from place.automate.polytec.vibrometer import PolytecSensorHead, Polytec
import matplotlib.pyplot as plt

import numpy as np
from time import sleep


def createControl(): 
    # !!! Replace this function for continous control initialization once osci_card functions are fixed.
    # Creates control to read signal level from polytec with trigger
    global receiver
    sampleRate = 'SAMPLE_RATE_10KSPS'
    channel = 'CHANNEL_A'
    duration = 1  #seconds
    timeout = 0.1  #seconds

    print('Making card handle')
    control = card.TriggeredRecordingController()  # get card handle
    control.configureMode = True  # go in configureMode; variables can be set without telling the card about it
    control.createInput(channel=channel, # record on channel A
                        inputRange="INPUT_RANGE_PM_1_V", 
                        impedance=50, 
                        AC=False
                        ) 
    control.setSampleRate(sampleRate)  # record with 1e6 samples per second
    control.setCaptureDurationTo(duration)
    control.setTriggerTimeout(timeout)
    control.configureMode = False  # leave configureMode; startCapture will run functions that configure the card
    times = control.getTimesOfRecord()  # get the time of each sample in one record

    return control, channel, times

def focus():
    # Focus polytec sensor head.
    Polytec().openConnection()
    PolytecSensorHead().autofocusVibrometer(span='Full')
    return

def GetSig(control, channel):
    # Record signal level from polytec.
    control.startCapture()
    control.readData()
    data = control.getDataRecordWise(channel)
    return np.average(data)

def signalPlot(xs, ys, zs):
    # Plot signal strength of 2D array. 
    # Returns point on plot selected by user.
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    mymap = plt.get_cmap("Reds")
    plt.scatter(xs, ys, s=100, c=zs, cmap=mymap, vmin=0, vmax=1, edgecolor='none')
    plt.xlabel('X-position')
    plt.ylabel('Y-position')
    plt.colorbar().set_label('Signal Strength')
    plt.title('Signal Level on Object Surface')

    class coordinates():
        def __init__(self):
            self.x = 0
            self.y = 0

    coord = coordinates()

    def onpick(event): # onpick event allows for saving location of user selection on plot.
        coord.x = event.xdata
        coord.y = event.ydata

    fig.canvas.mpl_connect('button_press_event', onpick)
    plt.show()
    return [int(coord.x), int(coord.y)]


def tMax(control, channel, xMot, yMot, limit, gridSize):
    # Scans and records signal level along a t-shaped pattern.

    # Initialize variables
    dataArray = []
    posArray = []
    gridSize -= 1
    xf = limit
    xi = limit * -1
    yf = limit
    yi = limit * -1
    dx = 2 * limit / gridSize
    dy = dx
    x = xi
    y = yi
    data = {}
    xs = []
    ys = []
    zs = []
    maxSig = 0
    
    # Move along x-axis.
    y = 0
    yMot.move_abs(y)
    while x <= xf:
        xMot.move_abs(int(x))
        Signal = GetSig(control, channel)
        print(Signal)
        xs.append(x)
        ys.append(y)
        zs.append(Signal)
        if maxSig < Signal:
            maxSig = Signal
            maxLoc = [x, y]
        data[str((x, y))] = Signal
        x += dx

    # Move along y-axis
    x = 0
    y = yi
    xMot.move_abs(x)
    while y <= yf:
        yMot.move_abs(int(y))
        Signal = GetSig(control, channel)
        xs.append(x)
        ys.append(y)
        zs.append(Signal)
        if maxSig < Signal:
            maxSig = Signal
            maxLoc = [x, y]
        data[str((x, y))] = Signal
        y += dy

    # maxLoc is location of strongest measured signal
    # clickLoc is location of click from graph
    clickLoc = signalPlot(xs, ys, zs)

    xMot.move_abs(clickLoc[0])
    xMot.set_DH()
    yMot.move_abs(clickLoc[1])
    yMot.set_DH()
    return


def findMax(control, channel, xMot, yMot, limit, gridSize): 
    # Completes square scan and moves motors to the maximum signal level found.

    #Initialize variables
    dataArray = []
    posArray = []
    gridSize -= 1
    xf = limit
    xi = limit * -1
    yf = limit
    yi = limit * -1
    dx = 2 * limit / gridSize
    dy = dx
    x = xi
    y = yi
    data = {}
    xs = []
    ys = []
    zs = []
    maxLoc = [0, 0]
    maxSig = 0
    
    # Move motors and record signal level.
    while x <= xf:
        xMot.move_abs(int(x))
        while y <= yf:
            yMot.move_abs(int(y))
            signal = GetSig(control, channel)
            xs.append(x)
            ys.append(y)
            zs.append(signal)
            if maxSig < signal:
                maxSig = signal
                maxLoc = [x, y]
            data[str((x, y))] = signal

            y += dy
        x += dx
        y -= dy
        if x >= xf:
            break
        xMot.move_abs(int(x))

        while y >= yi:
            yMot.move_abs(int(y))
            signal = GetSig(control, channel)
            xs.append(x)
            ys.append(y)
            zs.append(signal)
            if maxSig < signal:
                maxSig = signal
                maxLoc = [x, y]
            data[str((x, y))] = signal
            y -= dy
        x += dx
        y += dy

    print(data)

    # Plot array of signal level
    clickLoc = signalPlot(xs, ys, zs)

    # Move motors to location of maximum signal stength. Can also use clickLoc for location.
    xMot.move_abs(maxLoc[0])
    yMot.move_abs(maxLoc[1])

    # Set home to current location
    xMot.set_DH()
    yMot.set_DH()
    return







