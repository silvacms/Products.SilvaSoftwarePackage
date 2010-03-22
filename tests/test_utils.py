# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaSoftwarePackage.utils import rst_titles_parser
from Products.SilvaSoftwarePackage.utils import line_is_rst_title_marking
from Products.SilvaSoftwarePackage.SilvaSoftwareRelease import \
    test_version_string

import unittest


class RSTParserTestCase(unittest.TestCase):
    """Test the RST Title parser.
    """

    def test_line_is_rst_title_marker(self):
        """Test that line_is_rst_title_marker identifies correct lines
        used to mark an upper line as a title.
        """
        self.assertEqual(line_is_rst_title_marking(''), False)
        self.assertEqual(line_is_rst_title_marking('   '), False)
        self.assertEqual(line_is_rst_title_marking(' hello world'), False)
        self.assertEqual(line_is_rst_title_marking('hello world '), False)
        self.assertEqual(line_is_rst_title_marking('````````'), True)
        self.assertEqual(line_is_rst_title_marking('````````  '), True)
        self.assertEqual(line_is_rst_title_marking('  ````````  '), False)
        self.assertEqual(line_is_rst_title_marking('===---==='), False)
        self.assertEqual(line_is_rst_title_marking('========='), True)
        self.assertEqual(line_is_rst_title_marking('aaaaaaaaaaa\n'), True)

    def test_empty_lines(self):
        self.assertEqual(rst_titles_parser([]), None)

    def test_no_title_lines(self):
        self.assertEqual(rst_titles_parser([
                    '',
                    'Hello world',
                    'I am happy now\n',
                    '']), None)

    def test_one_title_lines(self):
        self.assertEqual(str(rst_titles_parser([
                    '',
                    'Hello world',
                    '=========== ',
                    'I am happy now\n',
                    ''])), 'Hello world')


class UtilsTestCase(unittest.TestCase):

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
    suite.addTest(unittest.makeSuite(UtilsTestCase))
    suite.addTest(unittest.makeSuite(RSTParserTestCase))
    return suite
