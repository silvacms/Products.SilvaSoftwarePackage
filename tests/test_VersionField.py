# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import ZopeTestCase
from Products.SilvaSoftwarePackage.VersionField import test_version_string

class VersionFieldTestCase(ZopeTestCase):
    """Test simple membership.
    """

    def test_test_version_string(self):
        """test whether the version string test works"""
        # mapping from test to whether it should fail or not
        testmapping = {'1.0': 0,
                        '1.3.0.2.4.1.2': 0,
                        '21132234.324423.232314.32124': 0,
                        '1.3a1': 0,
                        '11231.3243.2342.432234.23234.321321321a2423432': 0,
                        '1.3b1': 0,
                        '1.3c1': 1, # no 'gamma' releases
                        '1.3rc1': 0,
                        '1.3rc323432342': 0,
                        '1.2a1.2': 1,
                        '1.3..3': 1,
                        '24.a1': 1,
                        'a1': 1,
                        }
        for test, shouldfail in testmapping.items():
            if shouldfail:
                self.assertRaises(TypeError, test_version_string, test)
            else:
                try:
                    test_version_string(test)
                except TypeError, e:
                    self.fail(e)
    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SimpleMembershipTestCase))
        return suite

