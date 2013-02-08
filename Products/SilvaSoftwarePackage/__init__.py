# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller

silvaconf.extension_name('SilvaSoftwarePackage')
silvaconf.extension_title('Silva Software Package')
silvaconf.extension_depends('SilvaDocument')


class SilvaSoftwarePackageInstaller(DefaultInstaller):
    not_globally_addables = ['Silva Software Release',
                             'Silva Software Package',
                             'Silva Software Group',
                             'Silva Software Remote Group']


class IExtension(Interface):
    pass


install = SilvaSoftwarePackageInstaller(
    'SilvaSoftwarePackage', IExtension)


CLASS_CHANGES = {
    'Products.SilvaSoftwarePackage ISilvaSoftwarePackageExtension':
        'Products.SilvaSoftwarePackage IExtension',
    'Products.Silva3PSP.Silva3PExtensionPage Silva3PExtensionPage':
        'Products.SilvaSoftwarePackage.SilvaSoftwareCenter SilvaSoftwareCenter',
    'Products.Silva3PSP.Silva3PSoftwarePackage Silva3PSoftwarePackage':
        'Products.SilvaSoftwarePackage.SilvaSoftwarePackage SilvaSoftwarePackage',
    'Products.Silva3PSP.Silva3PSoftwareRelease Silva3PSoftwareRelease':
        'Products.SilvaSoftwarePackage.SilvaSoftwareRelease SilvaSoftwareRelease',
    'Products.SilvaSoftwarePackage.SilvaSoftwareFile FileSystemSoftwareFile':
        'Products.Silva.File FileSystemFile',
    'Products.SilvaSoftwarePackage.SilvaSoftwareFile ZODBSoftwareFile':
        'Products.Silva.File ZODBFile',
    }
