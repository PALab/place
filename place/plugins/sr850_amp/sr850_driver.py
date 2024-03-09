"""Basic driver functions for the SR850"""
from time import sleep
import serial

class SR850Driver:
    """Lower level access to the lock-in amp settings"""

    def __init__(self, serial_port):
        self._serial_port = serial_port

    def _set(self, cmd):
        """Sets a value on the amplifier

        :param cmd: the command to send to the amplifier
        :type cmd: str
        """
        with serial.Serial(self._serial_port,
                           baudrate=9600,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_TWO,
                           timeout=1) as connection:
            connection.write(bytes(cmd + '\r', 'ascii'))
            sleep(0.1)

    def _query(self, cmd):
        """Request a value from the amplifier

        :param cmd: the command to send to the amplifier
        :type cmd: str

        :returns: the response from the amplifier
        :rtype: str
        """
        with serial.Serial(self._serial_port,
                           baudrate=9600,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_TWO) as connection:
            connection.write(bytes(cmd + '\r', 'ascii'))
            sleep(0.1)
            return connection.read_until().decode('ascii').strip()
