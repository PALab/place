"""Access to the picomotor controller."""
from time import sleep
from socket import socket

PX = '2'
PY = '1'

AXIS_DISPLACEMENT = 'SN'
FOLLOWING_ERROR = 'FE'
HOME_POSITION = 'DH'
VELOCITY = 'VA'

MAX_32BIT_INT = 2**31 - 1
MIN_32BIT_INT = -(2**31)

class PMot:
    """The picomotor controller class."""
    def __init__(self):
        self.controller = socket()

    def connect(self, ip_address, port):
        """Establish connection with picomotor controller.

        :raises IOError: if there is no response from the server
        """
        self.controller.connect((ip_address, port))
        self.controller.settimeout(10)
        self.controller.recv(2048)

    def close(self):
        """Close connection to PicoMotor Controller"""
        self.controller.close()

    def set_attribute(self, motor_num, attribute, value=''):
        """Set information in the New Focus controller.

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: str

        :param attribute: the attribute to send to the controller
        :type attribute: str

        :param value: the value to set
        :type value: str

        :raises ValueError: if passed an invalid motor number
        """
        if motor_num == '0':
            self.controller.send((attribute + value + '\r').encode())
        elif motor_num == '1' or motor_num == '2':
            self.controller.send((motor_num + attribute + value + '\r').encode())
        else:
            raise ValueError('Invalid motor number')

    def set_axis_displacement(self, motor_num, value):
        """Set axis displacement units

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: str

        :param value: the value to set (must be 0 or 1)
        :type value: int

        :raises ValueError: if value is not 0 or 1
        """
        if value == 1 or value == 0:
            self.set_attribute(motor_num, AXIS_DISPLACEMENT, str(value))
        else:
            raise ValueError('Invalid value')

    def set_following_error(self, motor_num, threshold):
        """Set maximum following error threshold

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: str

        :param threshold: the following error threshold to set
        :type threshold: int

        :raises ValueError: if passed an invalid position
        """
        if 0 <= threshold <= MAX_32BIT_INT:
            self.set_attribute(motor_num, FOLLOWING_ERROR, str(threshold))
        else:
            raise ValueError('Invalid threshold value')

    def set_home_position(self, motor_num, position=0):
        """Set home position

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: str

        :param position: the home position to set
        :type position: int

        :raises ValueError: if passed an invalid position
        """
        if MIN_32BIT_INT <= position <= MAX_32BIT_INT:
            self.set_attribute(motor_num, HOME_POSITION, str(position))
        else:
            raise ValueError('Invalid position')

    def set_velocity(self, motor_num, velocity):
        """Set velocity

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: str

        :param velocity: the velocity (1-2000)
        :type velocity: int

        :raises ValueError: if passed an invalid velocity value
        """
        if 1 <= velocity <= 2000:
            self.set_attribute(motor_num, VELOCITY, str(velocity))
        else:
            raise ValueError('Invalid velocity: ' + str(velocity))


# Older functions

    def _get_id(self):
        """Get controller identification."""
        return self._get('0', '*IDN?')

    def _get_ac(self, motor_num):
        """Acceleration query."""
        return self._get(motor_num, 'AC?')

    def _get_cl(self, motor_num):
        """ Closed-loop control update interval query"""
        return self._get(motor_num, 'CL?')

    def _get_db(self, motor_num):
        """Get deadband value for an axis"""
        return self._get(motor_num, 'DB?')

    def _get_dh(self, motor_num):
        """Get home position (step).

        Default = 0. Values between -2147483648 and 2147483647
        """
        return self._get(motor_num, 'DH?')

    def _get_fe(self, motor_num):
        """Maximum following error threshold value for an axis"""
        return self._get(motor_num, 'FE?')

    def _get_md(self, motor_num):
        """Motion done status query"""
        return self._get(motor_num, 'MD?')

    def _get_mm(self, motor_num):
        """Closed-loop positioning status query"""
        return self._get(motor_num, 'MM?')

    def _get_mv(self, motor_num):
        """Get motion direction"""
        return self._get(motor_num, 'MV?')

    def _get_pa(self, motor_num):
        """Get motor target position, absolute motion"""
        return self._get(motor_num, 'PA?')

    def _get_ph(self, motor_num):
        """Hardware status query"""
        return self._get(motor_num, 'PH?')

    def _get_pr(self, motor_num):
        """Get target position, relative motion"""
        return self._get(motor_num, 'PR?')

    def _get_qm(self, motor_num):
        """Query type of motor"""
        return self._get(motor_num, 'QM?')

    def _get_sa(self, motor_num):
        """Controller address query"""
        return self._get(motor_num, 'SA?')

    def _get_sc(self):
        """Get controller address map"""
        return self._get('0', 'SC?')

    def _get_sd(self):
        """Scan done status query"""
        return self._get('0', 'SD?')

    def _get_sn(self):
        """Axis displacement units query"""
        return self._get('0', 'SN?')

    def _get_tb(self):
        """Get error message"""
        return self._get('0', 'TB?')

    def _get_te(self):
        """Error code query"""
        return self._get('0', 'TE?')

    def _get_tp(self, motor_num):
        """Get actual position, in number of steps from home"""
        return self._get(motor_num, 'TP?')

    def _get_va(self, motor_num):
        """Get velocity"""
        return self._get(motor_num, 'VA?')

    def _get_ve(self):
        """Get controller firmware version"""
        return self._get('0', 'VE?')

    def _get_zh(self):
        """Hardware configuraiton query"""
        return self._get('0', 'ZH?')

    def _get_zz(self):
        """Configuration register query"""
        return self._get('0', 'ZZ?')

    def _set_rcl(self, bin_):
        """Do a thing"""
        if bin_ == 1 or bin_ == 0:
            self.send_setting('0', '*RCL' + str(bin_))
        else:
            raise ValueError('Invalid command')

    def _get(self, motor_num, command):
        """Get information from the New Focus controller.

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: int

        :param command: the command to send to the controller
        :type command: str

        :returns: the decoded response
        :rtype: str

        :raises ValueError: if passed an invalid motor number
        """
        if motor_num == '0':
            self.controller.send((command + '\r').encode())
        elif motor_num == '1' or motor_num == '2':
            self.controller.send((motor_num + command + '\r').encode())
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

    def send_setting(self, motor_num, command):
        """Set information in the New Focus controller.

        :param motor_num: the motor (1 or 2) or the controller (0) to access
        :type motor_num: str

        :param command: the command to send to the controller
        :type command: str

        :raises ValueError: if passed an invalid motor number
        """
        if motor_num == '0':
            self.controller.send((command + '\r').encode())
        elif motor_num == '1' or motor_num == '2':
            self.controller.send((motor_num + command + '\r').encode())
        else:
            raise ValueError('Invalid motor number')


    def reset(self):
        """reset"""
        self.send_setting('0', '*RST')

    def _set_rst(self):
        """set rst"""
        self.send_setting('0', '*RST')

    def abort(self):
        """Abort motion"""
        self.send_setting('0', 'AB')

    def _set_ab(self):
        """set ab"""
        self.send_setting('0', 'AB')

    def _set_ac(self, motor_num, accel):
        """Acceleration query"""
        if accel > 0 and accel < 200000 and accel == int(accel):
            self.send_setting(motor_num, 'AC%s'%str(accel))
        else:
            raise ValueError('Invalid command')

    def set_cl(self, motor_num, interval):
        """Closed-loop control update interval set"""
        if interval > 0 and interval < 100000:
            self.send_setting(motor_num, 'CL%s'%str(interval))
        else:
            raise ValueError('Invalid command')

    def _set_db(self, motor_num, value):
        """Deadband set"""
        if value >= 0 and value <= 2147483647:
            self.send_setting(motor_num, 'DB%s'%str(value))
        else:
            raise ValueError('Invalid command')

    def _set_dh(self, motor_num, position=0):
        """Home position set"""
        if position == 'min':
            position = -2147483648
            self.send_setting(motor_num, 'DH%s'%str(position))
        elif position == 'max':
            position = 2147483648
            self.send_setting(motor_num, 'DH%s'%str(position))
        elif abs(position) <= 2147483648:
            self.send_setting(motor_num, 'DH%s'%str(position))
        else:
            raise ValueError('Invalid position')

    def _set_mc(self):
        """Motor check command"""
        self.send_setting('0', 'MC')

    def set_mm(self, motor_num, bin_value):
        """Enable/disable closed-loop positioning.

        bin_value 0 disable, 1 enable
        """
        if bin_value == 1 or bin_value == 0:
            self.send_setting(motor_num, 'MM%s'%str(bin_value))
        else:
            raise ValueError('Invalid command')

    def _set_mt(self, motor_num, direction):
        """Find hardware travel limit"""
        if direction == '+' or direction == '-':
            self.send_setting(motor_num, 'MT%s'%direction)
        else:
            raise ValueError('Invalid command')

    def _set_mv(self, motor_num, direction):
        """Indefinite move command"""
        if direction == '+' or direction == '-':
            self.send_setting(motor_num, 'MV' + direction)
        else:
            raise ValueError('Invalid command')

    def _set_mz(self, motor_num, direction):
        """Find nearest index search"""
        if direction == '+' or direction == '-':
            self.send_setting(motor_num, 'MZ' + direction)
        else:
            raise ValueError('Invalid command')

    def _set_or(self, motor_num):
        """Find Home search"""
        self.send_setting(motor_num, 'OR')

    def _set_pa(self, motor_num, position):
        """Move axis relative to home position (absolute)

        NOTE: DH is automatically set to 0 after controller reset or power cycle.
        """
        if abs(position) < 2147483648 and int(position) == position:
            self.send_setting(motor_num, 'PA%s'%str(position))
        else:
            raise ValueError('Invalid position: ' + str(position))

    def _set_pr(self, motor_num, value):
        """Relative move command"""
        if abs(value) < 2147483648:
            self.send_setting(motor_num, 'PR%s'%str(value))
        else:
            raise ValueError('Invalid command')

    def _set_qm(self, motor_num, value):
        """Motor type set command"""
        if value >= 0 and value <= 3 and int(value) == value:
            self.send_setting(motor_num, 'QM%s'%value)
        else:
            raise ValueError('Invalid command')

    def _set_rs(self):
        """Reset command"""
        self.send_setting('0', 'RS')

    def _set_sa(self, addr):
        """Set controller address"""
        if addr == int(addr) and addr > 0 and addr <= 31:
            self.send_setting('0', 'SA%s'%str(addr))
        else:
            raise ValueError('Invalid Command')

    def _set_sc(self, option):
        """Initiate scan process"""
        if option == int(option) and option >= 0 and option < 3:
            self.send_setting('0', 'SC%s'%str(option))

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
        self.send_setting('0', 'SM')

    def _set_st(self, motor_num):
        """Stop motion command"""
        self.send_setting(motor_num, 'ST')

    def _stop(self, motor_num):
        """Stop motion"""
        self.send_setting(motor_num, 'ST')

    def _set_xx(self):
        """Purge all user settings in controller memory"""
        self.send_setting('0', 'XX')

    def _set_zh(self, motor_num, status):
        """Set hardware configuration"""
        self.send_setting(motor_num, 'ZH%s'%status)

    def move_rel(self, motor_num, value):
        """Move relative to current position and check when done moving"""
        self._set_pr(motor_num, value)
        i = 0
        while True:
            if i < 2:
                sleep(2)
            else:
                sleep(1)
            err = self._get_tb()
            if not err:
                print('Communication with picomotors jeopardized')
            elif err[0] != '0':
                print(err)
            done = self._get_md(motor_num).rstrip()
            if not done:
                print('Communication with picomotors jeopardized')
                break
            elif done == '1':
                break

    def absolute_move(self, x_pos, y_pos):
        """Move absolute (relative to zero/home) and check when done moving"""
        x_int = int(x_pos)
        y_int = int(y_pos)
        if not (MIN_32BIT_INT <= x_int <= MAX_32BIT_INT and
                MIN_32BIT_INT <= y_int <= MAX_32BIT_INT):
            raise ValueError('invalid position: ({},{})'.format(x_pos, y_pos))

        self.controller.send(('{}TP?\n'.format(PX)).encode())
        curr_x = int(self.controller.recv(2048).decode())
        while curr_x != x_int:
            self.controller.send(('{}PA{}\n'.format(PX, x_int)).encode())
            sleep(0.25)
            self.controller.send(('{}MD?\n'.format(PX)).encode())
            response = int(self.controller.recv(2048).decode())
            while int(response) == 0:
                sleep(0.25)
                self.controller.send(('{}MD?\n'.format(PX)).encode())
                response = int(self.controller.recv(2048).decode())
            self.controller.send(('{}TP?\n'.format(PX)).encode())
            curr_x = int(self.controller.recv(2048).decode())

        self.controller.send(('{}TP?\n'.format(PY)).encode())
        curr_y = int(self.controller.recv(2048).decode())
        while curr_y != y_int:
            self.controller.send(('{}PA{}\n'.format(PY, y_int)).encode())
            sleep(0.25)
            self.controller.send(('{}MD?\n'.format(PY)).encode())
            response = int(self.controller.recv(2048).decode())
            while response == 0:
                sleep(0.25)
                self.controller.send(('{}MD?\n'.format(PY)).encode())
                response = int(self.controller.recv(2048).decode())
            self.controller.send(('{}TP?\n'.format(PY)).encode())
            curr_y = int(self.controller.recv(2048).decode())
        return curr_x, curr_y
