"""Access to the picomotor controller."""
from time import sleep
from socket import socket

class PMot:
    """The picomotor controller class."""
    def __init__(self):
        self.controller = socket()

    def connect(self, ip_address, port):
        """Establish connection with picomotor controller.

        :raises IOError: if there is no response from the server
        """
        self.controller.connect(ip_address, port)
        for _ in range(300):
            data = self.controller.recv(2048)
            if data:
                break
            sleep(0.1)
        else:
            raise IOError('no response from picomotor server')

    def get_id(self):
        """Get controller identification."""
        return self._get(0, '*IDN?')

    def get_ac(self, motor_num):
        """Acceleration query."""
        return self._get(motor_num, 'AC?')

    def get_cl(self, motor_num):
        """ Closed-loop control update interval query"""
        return self._get(motor_num, 'CL?')

    def get_db(self, motor_num):
        """Get deadband value for an axis"""
        return self._get(motor_num, 'DB?')

    def get_dh(self, motor_num):
        """Get home position (step).

        Default = 0. Values between -2147483648 and 2147483647
        """
        return self._get(motor_num, 'DH?')

    def get_fe(self, motor_num):
        """Maximum following error threshold value for an axis"""
        return self._get(motor_num, 'FE?')

    def get_md(self, motor_num):
        """Motion done status query"""
        return self._get(motor_num, 'MD?')

    def get_mm(self, motor_num):
        """Closed-loop positioning status query"""
        return self._get(motor_num, 'MM?')

    def get_mv(self, motor_num):
        """Get motion direction"""
        return self._get(motor_num, 'MV?')

    def get_pa(self, motor_num):
        """Get motor target position, absolute motion"""
        return self._get(motor_num, 'PA?')

    def get_ph(self, motor_num):
        """Hardware status query"""
        return self._get(motor_num, 'PH?')

    def get_pr(self, motor_num):
        """Get target position, relative motion"""
        return self._get(motor_num, 'PR?')

    def get_qm(self, motor_num):
        """Query type of motor"""
        return self._get(motor_num, 'QM?')

    def get_sa(self, motor_num):
        """Controller address query"""
        return self._get(motor_num, 'SA?')

    def get_sc(self):
        """Get controller address map"""
        return self._get(0, 'SC?')

    def get_sd(self):
        """Scan done status query"""
        return self._get(0, 'SD?')

    def get_sn(self):
        """Axis displacement units query"""
        return self._get(0, 'SN?')

    def get_tb(self):
        """Get error message"""
        return self._get(0, 'TB?')

    def get_te(self):
        """Error code query"""
        return self._get(0, 'TE?')

    def get_tp(self, motor_num):
        """Get actual position, in number of steps from home"""
        return self._get(motor_num, 'TP?')

    def get_va(self, motor_num):
        """Get velocity"""
        return self._get(motor_num, 'VA?')

    def get_ve(self):
        """Get controller firmware version"""
        return self._get(0, 'VE?')

    def get_zh(self):
        """Hardware configuraiton query"""
        return self._get(0, 'ZH?')

    def get_zz(self):
        """Configuration register query"""
        return self._get(0, 'ZZ?')

    def set_rcl(self, bin_):
        """Do a thing"""
        if bin_ == 1 or bin_ == 0:
            self._set(0, '*RCL' + str(bin_))
        else:
            raise ValueError('Invalid command')

    def _get(self, motor_num, command):
        """Get information from the New Focus controller.

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: int

        :param command: the command to send to the controller
        :type command: str

        :raises ValueError: if passed an invalid motor number
        """
        if motor_num == 0:
            self.controller.send((command + '\r').encode())
        elif motor_num == 1 or motor_num == 2:
            self.controller.send((str(motor_num) + command + '\r').encode())
        else:
            raise ValueError('Invalid motor number')
        for _ in range(300):
            data = self.controller.recv(2048)
            if data:
                break
            sleep(0.1)
        else:
            print('waiting for server')
        return str(data.decode())

    def _set(self, motor_num, command):
        """Set information in the New Focus controller.

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: int

        :param command: the command to send to the controller
        :type command: str

        :raises ValueError: if passed an invalid motor number
        """
        if motor_num == 0:
            self.controller.send((command + '\r').encode())
        elif motor_num == 1 or motor_num == 2:
            self.controller.send((str(motor_num) + command + '\r').encode())
        else:
            raise ValueError('Invalid motor number')


    def reset(self):
        """reset"""
        self._set(0, '*RST')

    def set_rst(self):
        """set rst"""
        self._set(0, '*RST')

    def abort(self):
        """Abort motion"""
        self._set(0, 'AB')

    def set_ab(self):
        """set ab"""
        self._set(0, 'AB')

    def set_ac(self, motor_num, accel):
        """Acceleration query"""
        if accel > 0 and accel < 200000 and accel == int(accel):
            self._set(motor_num, 'AC%s'%str(accel))
        else:
            raise ValueError('Invalid command')

    def set_cl(self, motor_num, interval):
        """Closed-loop control update interval set"""
        if interval > 0 and interval < 100000:
            self._set(motor_num, 'CL%s'%str(interval))
        else:
            raise ValueError('Invalid command')

    def set_db(self, motor_num, value):
        """Deadband set"""
        if value >= 0 and value <= 2147483647:
            self._set(motor_num, 'DB%s'%str(value))
        else:
            raise ValueError('Invalid command')

    def set_dh(self, motor_num, position=0):
        """Home position set"""
        if position == 'min':
            position = -2147483648
            self._set(motor_num, 'DH%s'%str(position))
        elif position == 'max':
            position = 2147483648
            self._set(motor_num, 'DH%s'%str(position))
        elif abs(position) <= 2147483648:
            self._set(motor_num, 'DH%s'%str(position))
        else:
            raise ValueError('Invalid position')

    def set_fe(self, motor_num, thresh):
        """Set maximum following error threshold"""
        if thresh >= 0 and thresh <= 2147483647:
            self._set(motor_num, 'FE%s'%str(thresh))
        else:
            raise ValueError('Invalid command')

    def set_mc(self):
        """Motor check command"""
        self._set(0, 'MC')

    def set_mm(self, motor_num, bin_):
        """Enable'disable closed-loop positioning.  bin_ = 0 disable, bin_ = 1 enable"""
        if bin_ == 1 or bin_ == 0:
            self._set(motor_num, 'MM%s'%str(bin_))
        else:
            raise ValueError('Invalid command')

    def set_mt(self, motor_num, direction):
        """Find hardware travel limit"""
        if direction == '+' or direction == '-':
            self._set(motor_num, 'MT%s'%direction)
        else:
            raise ValueError('Invalid command')

    def set_mv(self, motor_num, direction):
        """Indefinite move command"""
        if direction == '+' or direction == '-':
            self._set(motor_num, 'MV%s'%direction)
        else:
            raise ValueError('Invalid command')

    def set_mz(self, motor_num, direction):
        """Find nearest index search"""
        if direction == '+' or direction == '-':
            self._set(motor_num, 'MZ%s'%direction)
        else:
            raise ValueError('Invalid command')

    def set_or(self, motor_num):
        """Find Home search"""
        self._set(motor_num, 'OR')

    def set_pa(self, motor_num, position):
        """
        Move axis relative to home position (absolute)
        NOTE: DH is automatically set to 0 after controller reset or power cycle.
        """
        if abs(position) < 2147483648 and int(position) == position:
            self._set(motor_num, 'PA%s'%str(position))
        else:
            raise ValueError('Invalid command')

    def set_pr(self, motor_num, value):
        """Relative move command"""
        if abs(value) < 2147483648:
            self._set(motor_num, 'PR%s'%str(value))
        else:
            raise ValueError('Invalid command')

    def set_qm(self, motor_num, value):
        """Motor type set command"""
        if value >= 0 and value <= 3 and int(value) == value:
            self._set(motor_num, 'QM%s'%value)
        else:
            raise ValueError('Invalid command')

    def set_rs(self):
        """Reset command"""
        self._set(0, 'RS')

    def set_sa(self, addr):
        """Set controller address"""
        if addr == int(addr) and addr > 0 and addr <= 31:
            self._set(0, 'SA%s'%str(addr))
        else:
            raise ValueError('Invalid Command')

    def set_sc(self, option):
        """Initiate scan process"""
        if option == int(option) and option >= 0 and option < 3:
            self._set(0, 'SC%s'%str(option))

    def set_sm(self):
        """Save settings command

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
        """
        self._set(0, 'SM')

    def set_sn(self, motor_num, bin_):
        """Axis displacement units set"""
        if bin_ == 1 or bin_ == 0:
            self._set(motor_num, 'SN%s'%str(bin_))
        else:
            raise ValueError('Invalid command')

    def set_st(self, motor_num):
        """Stop motion command"""
        self._set(motor_num, 'ST')

    def stop(self, motor_num):
        """Stop motion"""
        self._set(motor_num, 'ST')

    def set_va(self, motor_num, vel):
        """Set velocity"""
        if vel >= 1 and vel <= 2000:
            self._set(motor_num, 'VA%s'%vel)

    def set_xx(self):
        """Purge all user settings in controller memory"""
        self._set(0, 'XX')

    def set_zh(self, motor_num, status):
        """Set hardware configuration"""
        self._set(motor_num, 'ZH%s'%status)

    def move_rel(self, motor_num, value):
        """Move relative to current position and check when done moving"""
        self.set_pr(motor_num, value)
        i = 0
        while True:
            if i < 2:
                sleep(2)
            else:
                sleep(1)
            err = self.get_tb()
            if not err:
                print('Communication with picomotors jeopardized')
            elif err[0] != '0':
                print(err)
            done = self.get_md(motor_num).rstrip()
            if not done:
                print('Communication with picomotors jeopardized')
                break
            elif done == '1':
                break

    def move_abs(self, motor_num, pos):
        """Move absolute (relative to zero/home) and check when done moving"""
        self.set_pa(motor_num, pos)
        i = 0
        while True:
            if i < 5:
                sleep(15)
            else:
                sleep(2)
            err = self.get_tb()
            if not err:
                print('Communication with picomotors jeopardized')
                break
            elif err[0] != '0':
                print(err)
            done = self.get_md(motor_num).rstrip()
            print('i=%s'%i)
            if not done:
                print('Communication with picomotors jeopardized')
                break
            elif done == '1':
                break
            i += 1
