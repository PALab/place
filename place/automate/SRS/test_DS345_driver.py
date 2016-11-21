import unittest

from subprocess import Popen, PIPE
from signal import SIGPIPE
from threading import Thread
import DS345_driver
import virtualDS345device
import os

class TestDS345Init(unittest.TestCase):

    def test0009_virtual_DS345_receives_message(self):
        vds = virtualDS345device.VirtualDS345()
        pty_name = vds.get_deviceName()
        vds.start()
        ds = DS345_driver.DS345(pty_name)
        msg = bytearray('hello',encoding='utf_8')
        ds.write(msg)
        resp = ds.read(size=5)
        ds.write(bytearray('!',encoding='utf_8'))
        vds.join()
        self.assertEqual(msg, resp)

    def test0008_virtual_DS345_stopping(self):
        vds = virtualDS345device.VirtualDS345()
        pty_name = vds.get_deviceName()
        vds.start()
        ds = DS345_driver.DS345(pty_name)
        ds.write(bytearray('!',encoding='utf_8'))
        vds.join()
        self.assertFalse(vds.isAlive())

    def test0007_virtual_DS345_starting(self):
        vds = virtualDS345device.VirtualDS345()
        pty_name = vds.get_deviceName()
        vds.start()
        self.assertTrue(vds.isAlive())

    def test0006_virtual_DS345_creation(self):
        vds = virtualDS345device.VirtualDS345()
        pty_name = vds.get_deviceName()
        self.assertFalse(vds.isAlive())

    def test0005_DS345_open_connection(self):

        ds = DS345_driver.DS345()
        ds.openConnection()

    def test0004_DS345_get_id(self):

        ds = DS345_driver.DS345()
        IDN = ds.getID()
        print(IDN)
        # we don't care what IDN is (or if we even get anything back)

    def test0003_init_DS345_unreadable(self):

        # find a file that is unreadable
        findcmd = ('find','/','!','(','-readable',')','-prune','-type','f','-print')
        headcmd = ('head','-n','1')
        find = Popen(findcmd, stdout=PIPE, close_fds=True)
        head = Popen(headcmd, stdin=find.stdout, stdout=PIPE, close_fds=True)
        find.stdout.close()
        unreadablefile = head.stdout.read().rstrip()
        head.stdout.close()
        find.terminate()
        head.terminate()
        # could be upgraded to PermissionError in Python 3.3 and newer
        self.assertRaises(OSError, DS345_driver.DS345, unreadablefile)

    def test0002_init_DS345_ttyS0(self):

        o = DS345_driver.DS345('/dev/ttyS0')
        self.assertIsInstance(o, DS345_driver.DS345)

    def test0001_unittest_operation(self):

        self.assertEqual(1,1)

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)

