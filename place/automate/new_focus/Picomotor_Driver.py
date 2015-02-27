# pMot PicoMotor Python Class
#
# for New Focus 8743-CL Picomotor Controller/Driver
#
# See 8743-CL manual for more information on pMot function calls
# February 27, 2015
# Evan Rust
 
import socket
import sys
import time

class pMot(object):

    def __init__(self, motor_num, IP = '130.216.58.155'): #motor_num = 0 for controller, motor_num = 1 or 2 for motors
        self.motor_num = motor_num
        if motor_num==0:
            pMot.port = 23
            pMot.host = IP
            pMot.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            
        ###Connection Commands###
        """
        connect()
        close()
        """
        
    def connect(self): #Open connection to PicoMotor Controller

        try:
            pMot.s.connect((pMot.host,pMot.port))
        except:
            print ('Unable to connect to picomotor controller')
            sys.exit()   
        print ('Connection to Picomotor Controller establed at ' + pMot.host + " on port " + str(pMot.port))
        data = pMot.s.recv(2048)
        return repr(data)
        
    def close(self): #Close connection to PicoMotor Controller
        pMot.s.close()
        print ('Connection to Picomotor Controller closed')

    ###Get Commands###
        """
        *IDN?   Identification string query
        AC?     Get acceleration
        CL?     Get closed-loop update interval
        DB?     Get deadband
        DH?     Get home position
        FE?     Get following error limit
        MD?     Get motion done status
        MM?     Get closed-loop control status
        MV?     Get motion direction
        PA?     Get destination position
        PH?     Get hardware status
        PR?     Get destination position
        QM?     Get motor type
        SA?     Get controller address
        SC?     Get RS-485 network controller addresses
        SD?     Get scan status
        SN?     Get units
        TB?     Get error message
        TE?     Get error number
        TP?     Get position
        VA?     Get velocity
        VE?     Firmware version string query
        ZH?     Get hardware configuration
        ZZ?     Get configuration register

        GATEWAY?    Default gateway address query
        HOSTNAME?   Hostname query
        IPADDR?     IP address query
        IPMODE?     IP mode query
        MACADDR?    MAC address query
        NETMASK?    Network mask address query
        """

    def get(self,command):
        if self.motor_num == 1 or self.motor_num == 2:
            pMot.s.sendall((str(self.motor_num)+command+'\r').encode())
            data = pMot.s.recv(2048)        
            return str(data.decode().strip())
        else:
            print ('Invalid motor number')
            return

    def get__(self,command):
        pMot.s.sendall((command+'\r').encode())
        data = pMot.s.recv(2048)
        return str(data.decode().strip())

    def get_IDN(self):
        return self.get__('*IDN?')

    def get_AC(self):
        return self.get('AC?')

    def get_CL(self):
        return self.get('CL?')

    def get_DB(self):
        return self.get('DB?')

    def get_DH(self):
        return self.get('DH?')

    def get_FE(self):
        return self.get('FE?')

    def get_MD(self):
        return self.get('MD?')
    
    def get_MM(self):
        return self.get('MM?')

    def get_MV(self):
        return self.get('MV?')

    def get_PA(self):
        return self.get('PA?')

    def get_PH(self):
        return self.get__('PH?')

    def get_PR(self):
        return self.get('PR?')

    def get_QM(self):
        return self.get('QM?')

    def get_SA(self):
        return self.get__('SA?')

    def get_SC(self):
        return self.get__('SC?')

    def get_SD(self):
        return self.get__('SD?')

    def get_SN(self):
        return self.get('SN?')

    def get_TB(self):
        return self.get__('TB?')

    def get_TE(self):
        return self.get__('TE?')

    def get_TP(self):
        return self.get('TP?')

    def get_VA(self):
        return self.get('VA?')

    def get_VE(self):
        return self.get__('VE?')

    def get_ZH(self):
        return self.get('CL?')

    def get_ZZ(self):
        return self.get__('ZZ?')


    ### Set Commands ###
    """
    *RCL    Recall parameters
    *RST    Reset intrument
    AB      Abort motion
    AC      Set acceleration
    CL      Set closed-loop update interval
    DB      Set deadband
    DH      Define home position
    FE      Set following error limit
    MC      Motor check
    MM      Enable closed-loop control
    MT      Find travel limit position
    MV      Move indefinitely
    MZ      Find index position
    OR      Find home position
    PA      Move to a target position
    PR      Move relative
    QM      Set motor type
    RS      Reset the controller
    SA      Set controller address
    SC      Scan RS-485 network
    SM      Save to non-volatile memory
    SN      Set units
    ST      Stop motion
    VA      Set velocity
    XX      Purge memory
    ZH      Set hardware configuration
    ZZ      Set configuration register    
    """

    def Set(self,command):
        if self.motor_num == 1 or self.motor_num == 2:
            pMot.s.sendall((str(self.motor_num)+command+'\r').encode())
        else:
            print ('Invalid motor number')

    def Set__(self,command):
        pMot.s.sendall((command+'\r').encode())

    def set_RCL(self,Bin):
        if Bin == 1 or Bin ==0:
            self.Set__('*RCL'+str(Bin))
        else:
            print ('Invalid command')
            
    def RESET(self):
        self.Set__('*RST')

    def set_RST(self):
        self.Set__('*RST')

    def ABORT(self):
        self.Set__('AB')

    def set_AB(self):
        self.Set__('AB')

    def set_AC(self,accel):
        if accel>0 and accel<200000 and accel==int(accel):
            self.Set('AC'+str(accel))
        else:
            print ('Invalid command')

    def set_CL(self,interval):
        if interval>0 and interval<100000:
            self.Set('CL'+str(interval))
        else:
            print ('Invalid command')

    def set_DB(self,value):
        if value >= 0 and value <= 2147483647:
            self.Set('DB'+str(value))
        else:
            print ('Invalid command')

    def set_DH(self,position=0):
        if abs(position)<2147483648 and int(position)==position:
            self.Set('DH'+str(position))
        else:
            print ('Invalid command')

    def set_FE(self,thresh):
        if value >= 0 and value <= 2147483647:
            self.Set('FE'+str(thresh))
        else:
            print ('Invalid command')

    def set_MC(self):
        self.Set__('MC')

    def set_MM(self,Bin):
        if Bin == 1 or Bin ==0:
            self.Set__('MM'+str(Bin))
        else:
            print ('Invalid command')

    def set_MT(self,direction):
        if direction == '+' or direction == '-':
            self.Set('MT'+direction)
        else:
            print ('Invalid command')

    def set_MV(self,direction):
        if direction == '+' or direction == '-':
            self.Set('MV'+direction)
        else:
            print ('Invalid command')

    def set_MZ(self,direction):
        if direction == '+' or direction == '-':
            self.Set('MZ'+direction)
        else:
            print ('Invalid command')

    def set_OR(self):
        self.Set('OR')

    def set_PA(self,position):
        if abs(position)<2147483648 and int(position)==position:
            self.Set('PA'+str(position))
        else:
            print ('Invalid command')

    def set_PR(self,value):
        if abs(value)<2147483648 and int(value)==value:
            self.Set('PR'+str(value))
        else:
            print ('Invalid command')

    def set_QM(self,value):
        if value>=0 and value<=3 and int(value)==value:
            self.Set('QM'+value)
        else:
            print ('Invalid command')

    def set_RS(self):
        self.Set__('RS')

    def set_SA(self,addr):
        if addr==int(addr) and addr>0 and addr<=31:
            self.Set('SA'+str(addr))
        else:
            print ('Invalid Command')

    def set_SC(self,option):
        if option==int(option) and option>=0 and option<3:
            self.Set__('SC'+str(option))

    def set_SM(self):
        self.Set__('SM')

    def set_SN(self,Bin):
        if Bin == 1 or Bin ==0:
            self.Set__('SN'+str(Bin))
        else:
            print ('Invalid command')

    def set_ST(self):
        self.Set('ST')

    def STOP(self):
        self.Set('ST')

    def set_VA(self,vel):
        if vel>=1 and vel <=2000:
            self.Set('VA'+str(vel))

    def set_XX(self):
        self.Set__('XX')




    ### PLACE Commands###

    def move_cont(self,direction):
        self.set_MV(direction)
        
    def move_rel(self,num):
        self.set_PR(num)
        while True:
            time.sleep(0.2)
            Err = self.get_TB()
            if Err[0]!='0':
                print (Err)
            if self.get_MD()=='1':
                break
            
    def move_abs(self,num):
        self.set_PA(num)
        while True:
            print 'debug 1'
            time.sleep(0.2)
            Err = self.get_TB()
            if Err[0]!='0':
                print 'debug 2'
                print (Err)
            if self.get_MD()=='1':
                print 'debug 3'
                break
            

#########################
def Scan_2D(Mx,My):
    step = 200
    grid_res = 5
    array = []

    for x_pos in range(0,grid_res+1,2):
        Mx.move_abs(x_pos*step)
        for y_pos in range(0,grid_res+1):
            My.move_abs(y_pos*step)
            #signal = something from LDV
            print('x: ' + Mx.get_DH() + 'y: ' + My.get_DH())
            array[str([x_pos,y_pos])]= signal

        x_pos += 1
        Mx.move_abs((x_pos)*step)
        for y_pos in range(grid_res,-1,-1):
            My.move_abs(y_pos*step)
            #signal = something from LDV
            print ('x: ' + Mx.get_DH() + 'y: ' + My.get_DH())
            array[str([x_pos,y_pos])]= signal
    return array


