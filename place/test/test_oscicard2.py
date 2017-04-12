''' Basic testing for AlazarTech card '''
from unittest import TestCase
import unittest

from place.automate.osci_card.utility import getNamesOfConstantsThatStartWith

class TestOsciCardUtilities(TestCase):
    ''' Test class '''

    # called before each test
    def setUp(self):
        pass

    def test0001_constants_starting(self):
        ''' ensures we can get constants starting with a specific value '''
        self.assertEqual(len(getNamesOfConstantsThatStartWith('POWER')), 2)

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
