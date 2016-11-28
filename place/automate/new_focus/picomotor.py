from __future__ import print_function
# pMot PicoMotor Python Class
#
# for New Focus 8743-CL Picomotor Controller/Driver
#
# See 8743-CL manual for more information on pMot function calls
# February 27, 2015
# Evan Rust, Jami Johnson

import socket
import sys
import time

class PMot(object):

    def __init__(self, IP='130.216.58.155',port=23): 
        '''
        motor_num = 0 for controller, motor_num = 1 or 2 for motors
        '''
        self.host = IP
        self.port = port
            
        
    def connect(self): 
        '''
        Open connection to PicoMotor Controller
        '''
        PMot.s = socket.socket()#socket.AF_INET,socket.SOCK_STREAM)
        
        try:
            self.s.connect((self.host,self.port))
        except:
            print ('Unable to connect to picomotor controller')
            sys.exit()   
        print('Connection to Picomotor Controller established at %s on port %s'%(self.host,str(self.port)))

        while True:
            data = self.s.recv(2048)
            if data:
                break
            else:
                'waiting for server response'

        return repr(data)
        
    def close(self): 
        '''
        Close connection to PicoMotor Controller
        '''
        self.s.close()
        print ('Connection to Picomotor Controller closed')
                
   
    def recv_timeout(self,timeout=0.5):
        '''
        http://code.activestate.com/recipes/408859/
        '''
        self.s.setblocking(0)
        total_data=[];data='';begin=time.time()
        while 1:
            #if you got some data, then break after wait sec
            if total_data and time.time()-begin>timeout:
                break
            #if you got no data at all, wait a little longer
            elif time.time()-begin>timeout*2:
                break
            try:
                data=self.s.recv(8192) # try self.recv_end
                if data:
                    total_data.append(data)
                    begin=time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        return ''.join(total_data)

    def get_MD_timeout(self,motor_num,timeout=0.5):
        self.s.send(('%s%s\r'%(str(motor_num),'MD')).encode())
        while True:
            data = self.recv_timeout(timeout)
            if data:
                break
            else:
                data = 1
                print('waiting for server')
        return str(data.decode())

    def get(self,motor_num,command):
        """
        \*IDN?
            Identification string query

        AC?
            Get acceleration

        CL?
            Get closed-loop update interval

        DB?
            Get deadband

        DH?
            Get home position

        FE?
            Get following error limit

        MD?
            Get motion done status

        MM?
            Get closed-loop control status

        MV?
            Get motion direction

        PA?
            Get destination position

        PH?
            Get hardware status

        PR?
            Get destination position

        QM?
            Get motor type

        SA?
            Get controller address

        SC?
            Get RS-485 network controller addresses

        SD?
            Get scan status

        SN?
            Get units

        TB?
            Get error message

        TE?
            Get error number

        TP?
            Get position

        VA?
            Get velocity

        VE?
            Firmware version string query

        ZH?
            Get hardware configuration

        ZZ?
            Get configuration register

        GATEWAY?
            Default gateway address query

        HOSTNAME?
            Hostname query

        IPADDR?
            IP address query

        IPMODE?
            IP mode query

        MACADDR?
            MAC address query

        NETMASK?
            Network mask address query
        """
        if motor_num == 0:
            self.s.send(('%s\r'%command).encode())
        else:
            self.s.send(('%s%s\r'%(str(motor_num),command)).encode())
        while True:
            data = self.s.recv(2048)
            if data:
                break
            else:
                print('waiting for server')
        return str(data.decode())
        
    
    def get_IDN(self):
        return self.get('*IDN?')

    def get_AC(self,motor_num):
        ''' Acceleration query.'''
        return self.get(motor_num,'AC?')

    def get_CL(self,motor_num):
        ''' Closed-loop control update interval query'''
        return self.get(motor_num,'CL?')

    def get_DB(self):
        '''Get deadband value for an axis'''
        return self.get(motor_num,'DB?')

    def get_DH(self,motor_num):
        '''Get home position (step). Default = 0.  Values between -2147483648 and 2147483647'''
        return self.get(motor_num,'DH?')

    def get_FE(self,motor_num):
        '''Maximum following error threshold value for an axis'''
        return self.get(motor_num,'FE?')

    def get_MD(self,motor_num):
        '''Motion done status query'''
        return self.get(motor_num,'MD?')
    
    def get_MM(self,motor_num):
        '''Closed-loop positioning status query'''
        return self.get(motor_num,'MM?')

    def get_MV(self,motor_num):
        '''Get motion direction'''
        return self.get(motor_num,'MV?')

    def get_PA(self,motor_num):
        '''Get motor target position, absolute motion'''
        return self.get(motor_num,'PA?')

    def get_PH(self,motor_num):
        '''Hardware status query'''
        return self.get(motor_num,'PH?')

    def get_PR(self,motor_num):
        '''Get target position, relative motion'''
        return self.get(motor_num,'PR?')

    def get_QM(self):
        '''Query type of motor'''
        return self.get(motor_num,'QM?')

    def get_SA(self,motor_num):
        '''Controller address query'''
        return self.get(motor_num,'SA?')

    def get_SC(self):
        '''Get controller address map'''
        return self.get(0,'SC?')

    def get_SD(self):
        '''Scan done status query'''
        return self.get(0,'SD?')

    def get_SN(self):
        '''Axis displacement units query'''
        return self.get(0,'SN?')

    def get_TB(self):
        '''Get error message'''
        return self.get(0,'TB?')

    def get_TE(self):
        '''Error code query'''
        return self.get(0,'TE?')

    def get_TP(self,motor_num):
        '''Get actual position, in number of steps from home'''
        return self.get(motor_num,'TP?')

    def get_VA(self,motor_num):
        '''Get velocity'''
        return self.get(motor_num,'VA?')

    def get_VE(self):
        '''Get controller firmware version'''
        return self.get(0,'VE?')

    def get_ZH(self):
        '''Hardware configuraiton query'''
        return self.get(0,'ZH?')

    def get_ZZ(self):
        '''Configuration register query'''
        return self.get(0,'ZZ?')

    def Set(self,motor_num,command):
        """
        \*RCL
            Recall parameters

        \*RST
            Reset intrument

        AB
            Abort motion

        AC
            Set acceleration

        CL
            Set closed-loop update interval

        DB
            Set deadband

        DH
            Define home position

        FE
            Set following error limit

        MC
            Motor check

        MM
            Enable closed-loop control

        MT
            Find travel limit position

        MV
            Move indefinitely

        MZ
            Find index position

        OR
            Find home position

        PA
            Move to a target position

        PR
            Move relative

        QM
            Set motor type

        RS
            Reset the controller

        SA
            Set controller address

        SC
            Scan RS-485 network

        SM
            Save to non-volatile memory

        SN
            Set units

        ST
            Stop motion

        VA
            Set velocity

        XX
            Purge memory

        ZH
            Set hardware configuration

        ZZ
            Set configuration register

        """
        if motor_num == 0:
            PMot.s.send(('%s\r'%command).encode())
        elif motor_num == 1 or motor_num == 2:
            PMot.s.send(('%s%s\r'%(str(motor_num),command)).encode())
        else:
            print ('Invalid motor number')

    def set_RCL(self,Bin):
        if Bin == 1 or Bin ==0:
            self.Set('*RCL%s'%str(Bin))
        else:
            print ('Invalid command')
            
    def RESET(self):
        self.Set(0,'*RST')

    def set_RST(self):
        self.Set(0,'*RST')

    def ABORT(self):
        '''Abort motion'''
        self.Set(0,'AB')

    def set_AB(self):
        self.Set(0,'AB')

    def set_AC(self,motor_num,accel):
        '''Acceleration query'''
        if accel>0 and accel<200000 and accel==int(accel):
            self.Set(motor_num,'AC%s'%str(accel))
        else:
            print ('Invalid command')

    def set_CL(self,motor_num,interval):
        '''Closed-loop control update interval set'''
        if interval>0 and interval<100000:
            self.Set(motor_num,'CL%s'%str(interval))
        else:
            print ('Invalid command')

    def set_DB(self,motor_num,value):
        '''Deadband set'''
        if value >= 0 and value <= 2147483647:
            self.Set(motor_num,'DB%s'%str(value))
        else:
            print ('Invalid command')

    def set_DH(self,motor_num,position=0):
        '''Home position set'''
        if position == 'min':
            position = -2147483648
            self.Set(motor_num,'DH%s'%str(position))
        elif position == 'max':
            position = 2147483648
            self.Set(motor_num,'DH%s'%str(position))
        elif abs(position)<=2147483648:
            self.Set(motor_num,'DH%s'%str(position))
            
        else:
            print ('Invalid position')

    def set_FE(self,motor_num,thresh):
        '''Set maximum following error threshold'''
        if thresh >= 0 and thresh <= 2147483647:
            self.Set(motor_num,'FE%s'%str(thresh))
        else:
            print ('Invalid command')

    def set_MC(self):
        '''Motor check command'''
        self.Set(0,'MC')

    def set_MM(self,motor_num,Bin):
        '''Enable'disable closed-loop positioning.  Bin = 0 disable, Bin = 1 enable'''
        if Bin == 1 or Bin ==0:
            self.Set(motor_num,'MM%s'%str(Bin))
        else:
            print ('Invalid command')

    def set_MT(self,motor_num,direction):
        '''Find hardware travel limit'''
        if direction == '+' or direction == '-':
            self.Set(motor_num,'MT%s'%direction)
        else:
            print ('Invalid command')

    def set_MV(self,motor_num,direction):
        '''Indefinite move command'''
        if direction == '+' or direction == '-':
            self.Set(motor_num,'MV%s'%direction)
        else:
            print ('Invalid command')

    def set_MZ(self,motor_num,direction):
        '''Find nearest index search'''
        if direction == '+' or direction == '-':
            self.Set(motor_num,'MZ%s'%direction)
        else:
            print ('Invalid command')

    def set_OR(self,motor_num):
        '''Find Home search'''
        self.Set(motor_num,'OR')

    def set_PA(self,motor_num,position):
        '''
        Move axis relative to home position (absolute)
        NOTE: DH is automatically set to 0 after controller reset or power cycle.
        '''
        if abs(position)<2147483648 and int(position)==position:
            self.Set(motor_num,'PA%s'%str(position))
        else:
            print ('Invalid command')

    def set_PR(self,motor_num,value):
        '''Relative move command'''
        if abs(value)<2147483648:
            self.Set(motor_num,'PR%s'%str(value))
        else:
            print()
            print ('Invalid command')

    def set_QM(self,motor_num,value):
        '''Motor type set command'''
        if value>=0 and value<=3 and int(value)==value:
            self.Set(motor_num,'QM%s'%value)
        else:
            print ('Invalid command')

    def set_RS(self):
        '''Reset command'''
        self.Set(0,'RS')

    def set_SA(self,addr):
        '''Set controller address'''
        if addr==int(addr) and addr>0 and addr<=31:
            self.Set(0,'SA%s'%str(addr))
        else:
            print ('Invalid Command')

    def set_SC(self,option):
        '''Initiate scan process'''
        if option==int(option) and option>=0 and option<3:
            self.Set(0,'SC%s'%str(option))

    def set_SM(self):
        '''Save settings command
        The SM command saves the following settings:
        Hostname (see HOSTNAME command)
        IP Mode (see IPMODE command)
        IP Address (see IPADDRESS command)
        Subnet mask address (see NETMASK command)
        Gateway address (see GATEWAY command)
        Configuration register (see ZZ command)
        Motor type (see QM command)
        Desired Velocity (see VA command)
        Desired Acceleration (see AC command)
        Closed-Loop interval (see CL command)
        Deadband (see DB command)
        Following Error (see FE command)
        Units (see SN commands)
        Hardware Configuration (see ZH command)
        '''
        self.Set(0,'SM')

    def set_SN(self,motor_num,Bin):
        '''Axis displacement units set'''
        if Bin == 1 or Bin ==0:
            self.Set(motor_num,'SN%s'%str(Bin))
        else:
            print ('Invalid command')

    def set_ST(self,motor_num):
        '''Stop motion command'''
        self.Set(motor_num,'ST')

    def STOP(self,motor_num):
        '''Stop motion'''
        self.Set(motor_num,'ST')

    def set_VA(self,motor_num,vel):
        '''Set velocity'''
        if vel>=1 and vel <=2000:
            self.Set(motor_num,'VA%s'%vel)

    def set_XX(self):
        '''Purge all user settings in controller memory'''
        self.Set(0,'XX')

    def set_ZH(self,motor_num,status):
        '''Set hardware configuration'''
        self.Set(motor_num,'ZH%s'%status)
        
    def move_rel(self,motor_num,value):
        '''Move relative to current position and check when done moving'''
        self.set_PR(motor_num,value)
        i=0
        while True:
            if i < 2:
                time.sleep(2)
            else:
                time.sleep(1)
            Err = self.get_TB()
            if not Err:
                print('Communication with picomotors jeopardized')
            elif Err[0]!='0':
                print (Err)
    
            done = self.get_MD(motor_num).rstrip()
            if not done:
                print('Communication with picomotors jeopardized')
                break
            elif done == '1':   
                break
            
    def move_abs(self,motor_num,pos):
        '''Move absolute (relative to zero/home) and check when done moving'''
        self.set_PA(motor_num,pos)
        i=0
        while True:
            if i < 5:
                time.sleep(15)
            else:
                time.sleep(2)
            Err = self.get_TB()
            if not Err:
                print('Communication with picomotors jeopardized')
                break
            elif Err[0]!='0':
                print (Err)
                
            done = self.get_MD(motor_num).rstrip()
            print('i=%s'%i)
            if not done:
                print('Communication with picomotors jeopardized')
                break
            elif done == '1':   
                break
            i+=1
 
    def Position(self, x, y, inverse = False,timeout=5 ):
        '''
        Use Keyboard input to control motor positions
        inverse = False for 1 mirror; inverse = True for 2 mirrors.
        '''

        try:
            # use raw_input for Python 2
            input = raw_input
        except NameError:
            pass

        if inverse == None:
            inverse = getInverse()
        print('Use w, a, s, d to control position of mirror.')
        print('Enter any key to stop motion.')
        print('Use c to confirm position')

        if inverse == False:
            while True:
                command = input()
                if command == 's':
                    self.set_MV(y,'+')
                elif command == 'a':
                    self.set_MV(x,'-')
                elif command == 'w':
                    self.set_MV(y,'-')
                elif command == 'd':
                    self.set_MV(x,'+')
                elif command == 'c':
                    self.STOP(x)
                    self.STOP(y)
                    break
                elif len(command)>1:
                    print('try again')
                else:
                    self.STOP(y)
                    self.STOP(x)

                Err = self.get_TB()
                if not Err:
                    print('Communication with picomotors jeopardized')
                    time.sleep(0.1)
                elif Err[0] != '0':
                    print('ERROR:', Err)
                    
                
        else:
            while True:
                command = input()
                if command == 'S':
                    self.set_MV(y,'+')
                elif command == 'A':
                    self.set_MV(x,'+')
                elif command == 'W':
                    self.set_MV(y,'-')
                elif command == 'D':
                    self.set_MV(x,'-')
                elif command == 'C':
                    self.STOP(x)
                    self.STOP(y)
                    break
                elif len(command)>1:
                    print('try again')
                else:
                    self.STOP(y)
                    self.STOP(x)

                Err = self.get_TB()
                if not Err:
                    print('Communication with picomotors jeopardized')
                    self.close()
                    time.sleep(10)
                    PMot(0,self.host,self.port)
                    self.connect()
                elif Err[0] != '0':
                    print('ERROR:', Err)
                    
        return

'''            
    # update these for new model!!
    def Scan_2D(Mx,My):
        step = 200
        grid_res = 5
        array = []

        for x_pos in range(0,grid_res+1,2):
            Mx.move_abs(x_pos*step)
            for y_pos in range(0,grid_res+1):
                My.move_abs(y_pos*step)
            #signal = something from LDV
                print 'x: %s y: %s '%(Mx.get_DH(),My.get_DH())
                array[str([x_pos,y_pos])]= signal

                x_pos += 1
                Mx.move_abs((x_pos)*step)
            for y_pos in range(grid_res,-1,-1):
                My.move_abs(y_pos*step)
            #signal = something from LDV
                print 'x: %s y: %s '%(Mx.get_DH(), My.get_DH())
                array[str([x_pos,y_pos])]= signal
        return array

    def Corners(self,x,y):
        
        Calibrate scan 
        '

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


    def Center(self,x,y):
        ''
        Calibrate scan area by selecting the center location.
        ''
        # Move motors to center position.
        print ('Position laser to center of scan area')
        Position(x,y)

        # Zero current position coordinates
        x.set_DH()
        y.set_DH()
        return

    def Double_Axes(self,x, y):
        ''
        Calibrate scan area by selecting min/max of x-axis, then min/max of y-axis.
        ''

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

    
    def returnConversion(self, xi, xf, yi, yf):
        ''
        Return conversion constant c to calculate motor steps s from length on object L: s = c*L 
        Requires user to input lengths between initial and final values of scan area.
        ''

        try:
            # use raw_input for Python 2
            input = raw_input
        except NameError:
            pass

        s1 = abs(xf - xi) #Total motor steps between points.

        # User input for length between points on x-axis
        while True:
            try:
                L1 = float(input("Distance between x-axis positions in mm: "))
                break
            except ValueError:
                print "Invalid Input"

        cx = s1/L1  # Calculate conversion constant for x-axis

        s2 = abs(yf - yi) #Total motor steps between points.

        # User input for length between points on y-axis
        while True:
            try:
                L2 = float(input("Distance between y-axis positions in mm: "))
                break
            except ValueError:
                print "Invalid Input"

        cy = s2/L2  # Calculate conversion constant for y-axis

        return cx, cy


    def getConversion(self, x, y, focuslength=None, method='auto', inverse=None):
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

        try:
            # use raw_input for Python 2
            input = raw_input
        except NameError:
            pass

        # Return conversion factor for distance on object surface to motor steps
        f = 11973
        c = 0
        file_location = "/usr/local/PLACE/place/automate/new_focus/calibration.p"

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
                    L = float(input("Distance between positions in mm: "))
                    break
                except ValueError:
                    print "Invalid Input"
            c = s/L

            save = input("Update calibration file? (y/n): ")
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

    def get_distance(self, focus_length):
        ''
        Converts value of polytec focus to length between polytec sensor head and sample.
        Equation was determined experimentally between values for P of 650 to 2100.
        Returns distance in mm.
        ''
        P = float(focus_length)
        if P < 2100 and P > 650: 
            d = (1.706e-11)*(P**4) - (7.69e-8)*(P**3) + (1.351e-4)*(P**2) - (9.213e-2)*(P) + 60
        else:
            print "Focus length value out of range!"
            d = None
        return d*10

    def getInverse(self):
        try:
            # use raw_input for Python 2
            input = raw_input
        except NameError:
            pass

        while True:
            mirror_num = input("Inverse left-right controls? (y/n): ")
            if mirror_num == "n":
                inverse = False
                break
            elif mirror_num == "y":
                inverse = True
                break
            print "Invalid input"
        return inverse
'''
