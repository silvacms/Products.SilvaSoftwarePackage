# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaSoftwarePackage.SilvaSoftwareRelease import \
    test_version_string

import unittest

class VersionTestCase(unittest.TestCase):

    def test_version_string(self):
        """test whether the version string test works.
        """

        tests = {'1.0': 0,
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
                 'a1': 1}

        for test, shouldfail in tests.items():
            if shouldfail:
                self.assertRaises(TypeError, test_version_string, test)
            else:
                try:
                    test_version_string(test)
                except TypeError, e:
                    self.fail(e)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionTestCase))
    return suite
