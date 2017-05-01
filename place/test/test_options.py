"""Test PLACE options"""
from unittest import TestCase, main
from place.automate.scan.parameters import Parameters
from place.automate.scan.scan_helpers import options
from place.alazartech import atsapi as ats
from place.scripts.scan import SCAN_1D, SCAN_2D

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
        par.scan_type = SCAN_1D
        par.DIMENSIONS = 1
        self.assertEqual(options([('--scan', '1D')]), par)
        par.scan_type = SCAN_2D
        par.DIMENSIONS = 2
        self.assertEqual(options([('--scan', '2D')]), par)
        with self.assertRaises(ValueError):
            options([('--scan', 'invalid')])

        par = Parameters()
        par.trigger_source_id_1 = ats.TRIG_EXTERNAL
        self.assertEqual(
            options([('--trigger_source_id_1', 'TRIG_EXTERNAL')]), par
            )

        par = Parameters()
        par.trigger_source_id_1 = ats.TRIG_CHAN_A
        self.assertEqual(
            options([('--trigger_source_id_1', 'TRIG_CHAN_A')]), par
            )

        par = Parameters()
        par.trigger_source_id_1 = ats.TRIG_CHAN_B
        self.assertEqual(
            options([('--trigger_source_id_1', 'TRIG_CHAN_B')]), par
            )

        par = Parameters()
        self.assertEqual(par.autofocus, 'auto')
        self.assertEqual(options([('--autofocus', 'auto')]), par)
        par.autofocus = 'off'
        self.assertEqual(options([('--autofocus', 'off')]), par)
        par.autofocus = 'small'
        self.assertEqual(options([('--autofocus', 'small')]), par)
        par.autofocus = 'medium'
        self.assertEqual(options([('--autofocus', 'medium')]), par)
        par.autofocus = 'full'
        self.assertEqual(options([('--autofocus', 'full')]), par)
        with self.assertRaises(ValueError):
            options([('--autofocus', 'invalid')])

if __name__ == '__main__':
    main(verbosity=2, buffer=True)
