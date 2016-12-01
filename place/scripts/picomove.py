'''
Function to  move picomotor mirrors.

-h, --help       prints doc string
--vel            choose velocity from 0 to 1700 (integer)
                 Default: 500

Example:

picomove --vel 1500

@author: Jami Johnson
June 29, 2015
'''
from __future__ import print_function
from place.automate.scan.scanFunctions import Initialize
from place.automate.new_focus.picomotor import PMot
import getopt
import sys

def main():
    vel = 500
    try:
        opts,args = getopt.getopt(sys.argv[1:], 'h',['help','vel='])
    except getopt.error as msg:
        print(msg)
        print('for help use --help')
        sys.exit(2)
    for o, a in opts:
        if o in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        if o in ('-v','--vel'):
            vel = int(a)
            print('velocity = %s'%vel)
            
    PMot().connect()
        
    PMot().set_VA(1,vel)
    PMot().set_VA(2,vel)
    #par = Initialize().picomotor_controller('130.216.58.155',23,par)
    PMot().Position(2,1, inverse=False)
    PMot().close()
    return

if __name__ == "__main__":
    main()
