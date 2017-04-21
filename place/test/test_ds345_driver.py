""" Basic testing for DS345 """
import unittest

from place.automate.SRS.ds345_driver import DS345
from place.test.virtualDS345device import VirtualDS345

class TestDS345Init(unittest.TestCase):
    """ Test class """

    # called before each test
    def setUp(self):
        # setup a virtual function generator
        self.virtual_fgen = VirtualDS345()
        self.pty_name = self.virtual_fgen.get_deviceName()
        self.virtual_fgen.start()

        # setup our connection to the device
        self.ds345 = DS345(self.pty_name)

    def test0001_ds345_get_id(self):
        """ test basic communication """
        self.assertEqual(self.ds345.get_id(), 'VirtualDS345')

    def test0002_ds345_get_default(self):
        """ test retrieval of default settings """
        print(self.ds345.get_id(), b'Settings: 0')
        self.assertEqual(self.ds345.getSettings(), 'Settings: 0')

    def test0003_ds345_get_settings_8(self):
        """ test retrieval of specified settings """
        self.assertEqual(self.ds345.getSettings(8), 'Settings: 8')

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
