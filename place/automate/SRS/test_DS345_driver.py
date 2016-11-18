import unittest

from subprocess import Popen, PIPE
from signal import SIGPIPE
import DS345_driver

class TestDS345Init(unittest.TestCase):

    def test_unittest_operation(self):
        self.assertEqual(1,1)

    def test_init_DS345_ttyS0(self):

        o = DS345_driver.DS345('/dev/ttyS0')
        self.assertIsInstance(o, DS345_driver.DS345)

    def test_init_DS345_unreadable(self):

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

    def test_DS345_get_id(self):

        ds = DS345_driver.DS345()
        IDN = ds.getID()
        print(IDN)
        # we don't care what IDN is (or if we even get anything back)

    def test_DS345_open_connection(self):

        ds = DS345_driver.DS345()
        ds.openConnection()

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)

