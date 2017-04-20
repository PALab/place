'''
This module provides an examples how the osci_card module could be used.

It acquires a certain number of records at moments when an external trigger
signal rises over 0 V and displays the average of all records.

Command line options can be used to alter the behavior:

-r --sampleRate=
        define the sample rate. Attention only certain values are possible (check AlazarCmd.py). Supply an integer with
        suffix, e.g. 100K for 10e5 samples per second or 1M for 10e6 samples per second.
-c --channel=
        define the channel that shall be recorded. Example: -c A for channel A.
-n --numberOfRecords=
        define the number of records that shall be averaged. Example: -n 100 to average 100 records.

FULL EXAMPLE
python oscicard_exampleAverageMultipleRecords.py -r 100K -c B --numberOfRecords=10

@author: henrik
'''

import sys
import getopt

import matplotlib.pyplot as plt
import numpy as np

import place.automate.osci_card.controller as card

def main():
    ''' no docstring '''
    # parse command line options
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hc:r:n:", ["help", "sampleRate=", "numberOfRecords=", "channel="])
    except getopt.error as msg:
        print(msg)
        print("for help use --help")
        sys.exit(2)
    # default values
    samplerate = "SAMPLE_RATE_100KSPS"
    averagedRecords = 50
    channel = "CHANNEL_A"
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

    control = card.TriggeredContinuousController()  # get card handle
    control.configureMode = True  # go in configureMode; variables can be set without telling the card about it
    control.create_input(channel=channel)  # record on channel A
    control.setSampleRate(samplerate)  # record with 1e6 samples per second
    control.setTrigger(sourceOfJ="TRIG_EXTERNAL")  # use external signal for trigger
    control.setTriggerTimeout(0.1)  # set trigger time out
    control.setRecordsPerCapture(averagedRecords)
    control.configureMode = False  # leave configureMode; start_capture will run functions that configure the card
    control.start_capture()
    control.readData()
    times = control.getTimesOfRecord()  # get the time of each sample in one record
    records = control.getDataRecordWise(channel)  # get the data in a list of records
    records = np.array(records)
    average = np.average(records, 0)
    # plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(times, average)
    ax.set_ylabel("voltage [V]")
    ax.set_xlabel("time [s]")
    fig.canvas.set_window_title("Acquired Records Averaged")
    plt.show()

if __name__ == "__main__":
    main()
