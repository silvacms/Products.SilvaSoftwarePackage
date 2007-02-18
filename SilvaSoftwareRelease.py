# Copyright (c) 2004 Guido Wesdorp. All rights reserved.
# See also LICENSE.txt
# $Id: SilvaSoftwareRelease.py,v 1.7 2005/03/14 11:22:58 guido Exp $
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implements
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle
from Products.Silva.Publication import Publication
from Products.Silva.interfaces import IPublication, IContainer, IAsset
from DateTime import DateTime
from Products.Silva.ExtensionRegistry import extensionRegistry
from interfaces import ISilvaSoftwareFile, ISilvaSoftwareRelease

module_security = ModuleSecurityInfo(
    'Products.SilvaSoftwarePackage.SilvaSoftwareRelease')

import re

icon = "www/software_release.png"
addable_priority = 9

module_security.declareProtected(SilvaPermissions.ReadSilvaContent,
                                    'test_version_string')
_version_reg = re.compile('^[0-9]+(\.[0-9]+)*(\.[0-9]+)?((a|b|rc)[0-9]*)?$')
def test_version_string(version):
    """test whether the version conforms to the required format"""
    if not _version_reg.search(version):
        raise TypeError, 'Version string has incorrect format!'

class SilvaSoftwareRelease(Publication):
    """Silva Software Release"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Release'
    implements(ISilvaSoftwareRelease)

    def __init__(self, id):
        SilvaSoftwareRelease.inheritedAttribute('__init__')(self, id)

    def get_silva_addables_allowed_in_publication(self):
        """return a list of allowed meta types in this type of object"""
        root = self.get_root()
        addables = extensionRegistry.get_addables()
        result = ['Silva Document']
        for addable in addables:
            if (addable.has_key('instance') and
                    IAsset.implementedBy(addable['instance']) and
                    self.service_view_registry.has_view('add', 
                        addable['name'])):
                result.append(addable['name'])
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_files')
    def get_files(self):
        """returns a list with all the contained files"""
        ret = []
        for obj in self.objectValues():
            if ISilvaSoftwareFile.providedBy(obj):
                ret.append(obj)
        ret.sort(lambda a, b: cmp(a.id, b.id))
        return ret

    def is_transparent(self):
        """returns 1 to make this software package's contents show up
            in tab_status of the package it's in"""
        return 1

InitializeClass(SilvaSoftwareRelease)

def manage_addSilvaSoftwareRelease(self, version, REQUEST=None):
    if not mangle.Id(self, version).isValid():
        return

    # see whether the id is correct for usage as version
    test_version_string(version)
        
    o = SilvaSoftwareRelease(version)
    self._setObject(version, o)
    object = getattr(self, version)
    object.set_title(version)
    
    binding = self.service_metadata.getMetadata(object)
    
    # add index document
    object.manage_addProduct['SilvaDocument'].manage_addDocument(
                                                    'index', version)

    add_and_edit(self, version, REQUEST)
    return ''

manage_addSilvaSoftwareReleaseForm = PageTemplateFile(
                "www/silvaSoftwareReleaseAdd", globals(), 
                __name__ = 'manage_addSilvaSoftwareReleaseForm')

registerTypeForMetadata(SilvaSoftwareRelease.meta_type)
