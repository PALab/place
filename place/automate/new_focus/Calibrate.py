from place.automate.new_focus.Picomotor_Driver import pMot
from place.automate.polytec.vibrometer import Polytec, PolytecSensorHead
from place.automate.scan.scanFunctions import initialize
import cPickle as pickle

"""
 Three scan area calibration methods are Corners, Center, and Double_Axes.
 Two conversion methods are returnConversion and getConversion. 

February 27, 2015
Evan Rust
"""

def Corners(x,y):
    # Calibrate scan 

    # Move motors to top-left of scan area
    print ('Position laser to bottom-right corner of scan area')
    Position(x,y)
    print 'Bottom-righ location set.'

    #Zero current position coordinates
    x.set_DH()
    y.set_DH()
    xi = int(x.get_DH())
    yi = int(y.get_DH())

    #Move motors to bottom-right of scan area
    print ('Position laser to top-left  corner of scan area')
    Position(x,y)
    xf = int(x.get_DH())
    yf = int(y.get_DH())
    print('Top-left location set.')

    # Adjust home position if final position < initial position
    if xf < 0:
        xf = xf*(-1)
        x.set_DH()
    if yf < 0:
        yf = yf*(-1)
        y.set_DH()     

    return xi, xf, yi, yf

  
def Center(x,y):
    # Calibrate scan area by selecting the center location.

    # Move motors to center position.
    print ('Position laser to center of scan area')
    Position(x,y)

    # Zero current position coordinates
    x.set_DH()
    y.set_DH()
    return

def Double_Axes(x, y):
    # Calibrate scan area by selecting min/max of x-axis, then min/max of y-axis.

    #Move motors to first x-axis location.
    print ('Position laser to left side of scan area.')
    Position(x,y)
    x.set_DH()
    xi = int(x.get_DH())

    #Move motors to second x-axis location.
    print ('Position laser to right side of scan area.')
    Position(x,y)
    xf = int(x.get_DH())
    
    # Move motors to first y-axis location.
    print ('Position laser to top side of scan area.')
    Position(x,y)
    y.set_DH()
    yi = int(y.get_DH())
    
    # Move motors to second y-axis locaiton.
    print ('Position laser to bottom side of scan area.')
    Position(x,y)
    yf = int(y.get_DH())

    # Adjust home position if final position < initial position
    if xf < 0:
        xf = xf*(-1)
        x.set_DH()
    if yf < 0:
        yf = yf*(-1)
        y.set_DH()     

    return xi, xf, yi, yf

def Position(x, y, inverse = False ):
    # Use Keyboard input to control motor positions
    # inverse = False for 1 mirror; inverse = True for 2 mirrors.
    if inverse == None:
        inverse = getInverse()
    print 'Use w, a, s, d to control position of mirror.'
    print 'Enter any key to stop motion.'
    print 'Use c to confirm position'
   
    if inverse == False:
        while True:
            command = raw_input()
            if command == 's':
                y.set_MV('+')
            elif command == 'a':
                x.set_MV('-')
            elif command == 'w':
                y.set_MV('-')
            elif command == 'd':
                x.set_MV('+')
            elif command == 'c':
                x.STOP()
                y.STOP()
                break
            elif len(command)>1:
                if command[0] == 'x':
                    try:
                        x.move_rel(int(command[1:]))
                    except ValueError:
                        pass
                elif command[0] == 'y':
                    try:
                        x.move_rel(int(command[1:]))
                    except ValueError:
                        pass
            else:
                y.STOP()
                x.STOP()

            error = x.get_TB()
            if error[0]!='0':
                print ('Error:' + error)
    else:
        while True:
            command = raw_input()
            if command == 'S':
                y.set_MV('+')
            elif command == 'A':
                x.set_MV('+')
            elif command == 'W':
                y.set_MV('-')
            elif command == 'D':
                x.set_MV('-')
            elif command == 'C':
                x.STOP()
                y.STOP()
                break
            elif len(command)>1:
                if command[0] == 'x':
                    try:
                        x.move_rel(int(command[1:]))
                    except ValueError:
                        pass
                elif command[0] == 'y':
                    try:
                        y.move_rel(int(command[1:]))
                    except ValueError:
                        pass
            else:
                y.STOP()
                x.STOP()

            error = x.get_TB()
            if error[0]!='0':
                print ('Error:' + error)     

    return

def returnConversion(xi, xf, yi, yf):
    # Return conversion constant c to calculate motor steps s from length on object L: s = c*L 
    # Requires user to input lengths between initial and final values of scan area.

    s1 = abs(xf - xi) #Total motor steps between points.

    # User input for length between points on x-axis
    while True:
        try:
            L1 = float(raw_input("Distance between x-axis positions in mm: "))
            break
        except ValueError:
            print "Invalid Input"
   
    cx = s1/L1  # Calculate conversion constant for x-axis

    s2 = abs(yf - yi) #Total motor steps between points.

    # User input for length between points on y-axis
    while True:
        try:
            L2 = float(raw_input("Distance between y-axis positions in mm: "))
            break
        except ValueError:
            print "Invalid Input"
   
    cy = s2/L2  # Calculate conversion constant for y-axis

    return cx, cy
    

def getConversion(x, y, focuslength=None, method='auto', inverse=None):
    """
    This function returns the conversion constant c to calculate motor steps s from length on object L.

    The equation to determine the conversion from motor steps to length in mm on objects surface is:
    s  = c*L = (L*f)/(d-a)
    
    s is motor steps
    L is length on object
    c is calibration constant
    f is factor for conversion (never changes)
    d is total distance from sensor head to object
    a is distance from sensor head to scanning mirror

    The focuslength should be converted to total distance using the get_distance(focus_length) function.
    """

    # Return conversion factor for distance on object surface to motor steps
    f = 11973
    c = 0
    file_location = "/usr/lib/python2.6/site-packages/PLACE/place/automate/new_focus/calibration.p"
    
    if method == 'manual':  
        # The manual conversion requires user to move motors to 2 locations and input the distance between those points.
        # There is an option for updating the calibration file, which is used with the 'auto' option.
        if inverse == None:
            inverse = getInverse()
        
        print "Calibrate along x-axis"
        print "Move motor to first calibration position"
        Position(x, y, inverse)
        location1 = float(x.get_DH())
        print "Move motor to second calibration position"
        Position(x, y, inverse)
        location2 = float(x.get_DH())
        
        s = abs(location2 - location1)
        while True:
            try:
                L = float(raw_input("Distance between positions in mm: "))
                break
            except ValueError:
                print "Invalid Input"
        c = s/L
        
        save = raw_input("Update calibration file? (y/n): ")
        if save == 'y':
            d = get_distance(focuslength)
            a = d-(f/c)
            with open(file_location,'wb') as q:
                pickle.dump(a, q)

    elif method == "auto":
        # The auto conversion method reads in the saved conversion values and uses the polytec sensor head to determine the conversion constant.
        # A manual calibration is required everytime the picomotor mirror base or laser source are moved, which updates the conversion file.
        d = get_distance(focuslength)
        print "Reading from calibration file. If scanning mirror base plate or sensor head have been moved from last calibration, lengths on object surface will be inaccurate."
        with open(file_location,'rb') as q:
            a = pickle.load(q)
        c = f/(d-a)       

    return c

def get_distance(focus_length):
    # Converts value of polytec focus to length between polytec sensor head and sample.
    # Equation was determined experimentally between values for P of 650 to 2100.
    P = float(focus_length)
    if P < 2100 and P > 650: 
        d = (1.706e-11)*(P**4) - (7.69e-8)*(P**3) + (1.351e-4)*(P**2) - (9.213e-2)*(P) + 60
    else:
        print "Focus length value out of range!"
        d = None
    return d

def getInverse():
    while True:
        mirror_num = raw_input("Inverse left-right controls? (y/n): ")
        if mirror_num == "n":
            inverse = False
            break
        elif mirror_num == "y":
            inverse = True
            break
        print "Invalid input"
    return inverse
