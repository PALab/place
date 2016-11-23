# This is a virtual emulator of a DS345 function generator.
from __future__ import print_function

import sys, pty, os
from threading import Thread

class VirtualDS345(Thread):

    def __init__(self):

        self.master, slave = pty.openpty()

        self.slave_tty_name  = os.ttyname(slave)

        Thread.__init__(self)
        self.daemon = True

    def get_deviceName(self):
        return self.slave_tty_name

    def run(self):

        while True:
            dat = os.read(self.master,1000)
            
            if dat == b'*IDN? \n':
                os.write(self.master, b'VirtualDS345\n')
            elif dat.startswith(b'*RCL'):
                msg = b''.join([b'Settings: ', dat[5:6], b'\n'])
                os.write(self.master, msg)
            elif dat == b'echo\n':
                os.write(self.master, b'echo\n')
            elif dat == b'exit\n':
                return
            else:
                pass

