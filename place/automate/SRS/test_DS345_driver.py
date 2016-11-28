import os
import unittest

from subprocess import Popen, PIPE
from signal import SIGPIPE
from threading import Thread

from .DS345_driver import DS345
from .virtualDS345device import VirtualDS345

class TestDS345Init(unittest.TestCase):

    # called before each test
    def setUp(self):
        # setup a virtual function generator
        self.virtual_fgen = VirtualDS345()
        self.pty_name = self.virtual_fgen.get_deviceName()
        self.virtual_fgen.start()

        # setup our connection to the device
        self.ds345 = DS345(self.pty_name)

    def test0001_DS345_get_id(self):
        self.assertEqual(self.ds345.getID(), b'VirtualDS345')

    def test0002_DS345_get_settings_default(self):
        print(self.ds345.getID(), b'Settings: 0')
        self.assertEqual(self.ds345.getSettings(), b'Settings: 0')

    def test0003_DS345_get_settings_8(self):
        self.assertEqual(self.ds345.getSettings(8), b'Settings: 8')

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)

