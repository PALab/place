"""Test PLACE options"""
from unittest import TestCase, main
from place.automate.scan.parameters import Parameters
from place.automate.scan.scan_helpers import options

class TestOptions(TestCase):
    """Test the command-line argument parsing."""
    def test_empty_options(self):
        """Providing no options should return the defaults."""
        self.assertEqual(options([]), Parameters())

    def test_basic_options(self):
        """Test single options"""
        par = Parameters()
        par.FILENAME = 'testname.h5'
        self.assertEqual(options([('--n', 'testname')]), par)

        par = Parameters()
        par.FILENAME2 = 'testname.h5'
        self.assertEqual(options([('--n2', 'testname')]), par)

        par = Parameters()
        par.SCAN = '1D'
        par.DIMENSIONS = 1
        self.assertEqual(options([('--scan', '1D')]), par)

        par = Parameters()
        par.SCAN = '2D'
        par.DIMENSIONS = 2
        self.assertEqual(options([('--scan', '2D')]), par)

if __name__ == '__main__':
    main(verbosity=2, buffer=True)
