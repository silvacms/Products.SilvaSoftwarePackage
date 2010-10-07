# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller

silvaconf.extensionName('SilvaSoftwarePackage')
silvaconf.extensionTitle('Silva Software Package')
silvaconf.extensionDepends('SilvaDocument')

class SilvaSoftwarePackageInstaller(DefaultInstaller):

    def isGloballyAddable(self, content):
        if content['name'] in ['Silva Software Release',
                               'Silva Software Package']:
            return False
        return super(SilvaSoftwarePackageInstaller,
                     self).isGloballyAddable(content)


    def registerViews(self, reg):
        """Register core views on registry.
        """
        # edit
        reg.register('edit', 'Silva Software Package',
                     ['edit', 'Container', 'SilvaSoftwarePackage'])
        reg.register('edit', 'Silva Software Release',
                     ['edit', 'Container', 'SilvaSoftwareRelease'])

    def unregisterViews(self, reg):
        for meta_type in ['Silva Software Package',
                          'Silva Software Release',]:
            reg.unregister('edit', meta_type)

    def customizeInstall(self, root):
        # security
        root.manage_permission('Add Silva Software Packages',
                               ['Author', 'Editor', 'ChiefEditor', 'Manager'])
        root.manage_permission('Add Silva Software Releases',
                               ['Author', 'Editor', 'ChiefEditor', 'Manager'])


class ISilvaSoftwarePackageExtension(Interface):
    pass


install = SilvaSoftwarePackageInstaller(
    'SilvaSoftwarePackage', ISilvaSoftwarePackageExtension)


CLASS_CHANGES = {
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
