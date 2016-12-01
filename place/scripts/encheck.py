'''
Program to run and test energy of Spectra-Physics Quanta-Ray INDI laser.

-h, --help       prints doc string

Program will prompt for confirmation that user wishes to control the
laser with PLACE. Then, the laser will turn on and the user will be
prompted for confirmation to turn the laser on REP. The laser power
will initially be set to 0 percent. Then the user can type a value
between 0 and 100 to choose the percent power of the laser to fire at
or choose *stop* to turn the laser off.

WARNING
-------

As soon as a numerical value between 0 and 100 is chosen the laser
will fire!

**MAKE SURE** that the energy meter, beam dump, or sample is in the path
and you are fully aware of the path of the beam.

**NOTE** The master power on the laser must be *on*, the key turned, and
the *computer* switch selected on the power supply of the laser in order
for this program to work.

@author: Jami L Johnson
May 30, 2016
'''
from __future__ import print_function
from place.automate.scan.scanFunctions import Initialize
from place.automate.quanta_ray.QRay_driver import QuantaRay
import getopt
import sys
from time import sleep

def main():
    par = {}
    instruments = ['INDI']
    par['ENERGY']=0
    par['AVERAGES'] = 100

    try:
        opts,args = getopt.getopt(sys.argv[1:], 'h',['help','en='])
    except getopt.error as msg:
        print(msg)
        print('for help use --help')
        sys.exit(2)
    for o, a in opts:
        if o in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)

    laser_check = raw_input('You have chosen to control the INDI laser with PLACE. Do you wish to continue? (yes/N) \n')
    if laser_check == 'yes':
        traceTime = Initialize().quanta_ray(0, par)
    else:
        QuantaRay().closeConnection()
        exit()
    laser_check = raw_input('Turn laser on REP? (yes/N) \n')
    if laser_check == 'yes':
        QuantaRay().set('REP')
        sleep(1)
        QuantaRay().getStatus() # keep watchdog happy
    else:
        print('Turning laser off ...')
        QuantaRay().off()
        QuantaRay().closeConnection()
        exit()

    print("Type percent of maximum lamp energy to change energy of source laser or 'stop' to turn off laser scan \n")
    while True:
        cmd = raw_input()
        if cmd != 'stop':
            if float(cmd) >= 0 and float(cmd) < 100:
                QuantaRay().setOscPower(float(cmd))
                print('Percent power changed to %s \n'%cmd)
                QuantaRay().setWatchdog(100)
            elif float(cmd) < 0 or float(cmd) > 100:
                print('Choose power between 0 and 100 percent.')
                QuantaRay().setWatchdog(100)
            else:
                print("Invalid, enter power between 0 and 100 percent or 'stop' to turn of laser")
        elif cmd == 'stop':
            QuantaRay().set('SING')
            QuantaRay().off()
            QuantaRay().closeConnection()
            break
    return

if __name__ == "__main__":
    main()

