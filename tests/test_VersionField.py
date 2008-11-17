# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.4 $
import os, sys

from Products.Silva.tests import SilvaTestCase
from Products.SilvaSoftwarePackage.SilvaSoftwareRelease import test_version_string

from Testing import ZopeTestCase
from DateTime import DateTime

_user_name = ZopeTestCase._user_name

class SilvaSoftwarePackageTestCase(SilvaTestCase.SilvaTestCase):
    """Test software package functionality
    """

    def afterSetUp(self):
        ZopeTestCase.installProduct('SilvaSoftwarePackage')
        self.root.service_extensions.install('SilvaSoftwarePackage')
        self.softwarepackage = self.root.\
                manage_addProduct['SilvaSoftwarePackage'].\
                manage_addSilvaSoftwarePackage('sp', 'SP')

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

    def test_sort_by_version(self):
        sp = self.root.sp
        
        # second should always be higher
        versiontuples = [('0', '1'),
                            ('0.1a', '0.1b'),
                            ('0.1b', '0.1b2'),
                            ('1.3423.342342a1', '1.3423.342342a2'),
                            ('1.0a1', '1.0a2'),
                            ('1.0b2', '1.0rc1'),
                            ('1.0rc2', '1.0'),
                            ('1.0.0.0.1b1', '1.0.0.0.1b2'),
                            ('1.0.0.0.1a2', '1.0.0.0.1b1'),
                            ('1.0.0.0.1b2', '1.0.0.0.1rc1'),
                            ('1.0.0.0.1rc1', '1.0.0.0.1'),
                            ('1.0.2', '1.1b1'),
                            ('1.1b2', '1.1'),
                            ]
        
        for version1, version2 in versiontuples:
            sr1 = self._add_software_release(sp, version1)
            sr2 = self._add_software_release(sp, version2)
            try:
                self.assertEquals(sp._sort_by_version(sr1, sr2), 1)
            except AssertionError, e:
                self.fail('AssertionError: %s - (%s, %s)' % (e, version1, version2))
            sp.manage_delObjects([sr1.id, sr2.id])

    def test_get_releases(self):
        """found that test_sort_by_version had some problems, adding this 
            additional test"""
        sp = self.root.sp

        sr1 = self._add_and_publish_software_release(sp, '1.1')
        sr2 = self._add_and_publish_software_release(sp, '1.1b1')
        sr3 = self._add_and_publish_software_release(sp, '1.1rc1')
        sr4 = self._add_and_publish_software_release(sp, '1.1a1')
        sr5 = self._add_and_publish_software_release(sp, '1.1b2')
        objids = [o.id for o in sp.get_releases()] 
        expected = ['1.1', '1.1rc1', '1.1b2', '1.1b1', '1.1a1']
        self.assertEquals(objids, expected)

        input = ['1.1b2', '1.1b1', '1.1rc1', '1.1a1', '1.1']
        expected = ['1.1', '1.1rc1', '1.1b2', '1.1b1', '1.1a1']
        input.sort(sp._sort_by_version_helper)
        self.assert_(input, expected)
        
        input = ['1.1', '1.1a1', '1.1rc1', '1.1b1', '1.1b2']
        expected = ['1.1', '1.1rc1', '1.1b2', '1.1b1', '1.1a1']
        input.sort(sp._sort_by_version_helper)
        self.assert_(input, expected)

        input = ['1.1rc1', '1.1b2', '1.1b1', '1.1a1', '1.1']
        expected = ['1.1', '1.1rc1', '1.1b2', '1.1b1', '1.1a1']
        input.sort(sp._sort_by_version_helper)
        self.assert_(input, expected)
        
    def _add_software_release(self, sp, version):
        sp.manage_addProduct['SilvaSoftwarePackage'].\
            manage_addSilvaSoftwareRelease(version)
        sr = getattr(sp, version)
        return sr

    def _add_and_publish_software_release(self, sp, version):
        sr = self._add_software_release(sp, version)
        sr.get_default().set_unapproved_version_publication_datetime(DateTime())
        sr.get_default().approve_version()
        return sr
    
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaSoftwarePackageTestCase))
    return suite

