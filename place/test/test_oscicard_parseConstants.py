'''
Created on Jul 6, 2013

@author: henrik
'''
import unittest
from place.automate.osci_card.parseConstants import _isDefineStatement, _extractConstant
from place.automate.osci_card.parseConstants import *


class Test(unittest.TestCase):
        
    def test_isDefineStatement(self):
        self.assertTrue(_isDefineStatement("#definemaria"), "Define cannot be found")
        self.assertFalse(_isDefineStatement("ahllo #deinemaria"), "Define found in wrong place")

    def test_extractConstant(self):
        var, val = _extractConstant("#define hallo 234234UL")
        self.assertEqual("hallo",var, "wrong constant name")
        self.assertEqual(234234, val, "wrong value")
        self.assertRaises(ConstantParseError, _extractConstant, "#define hallo 2342 34")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
