# Copyright (c) 2004 Guido Wesdorp. All rights reserved.
# See also LICENSE.txt
# $Id: SilvaSoftwareRelease.py,v 1.4 2004/08/17 12:27:50 roman Exp $
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle
from Products.Silva.Publication import Publication
from Products.Silva.interfaces import IPublication, IContainer, IAsset
from DateTime import DateTime
from Products.Silva.ExtensionRegistry import extensionRegistry
from interfaces import ISilvaSoftwareFile

icon = "www/software_release.png"

class SilvaSoftwareRelease(Publication):
    """Silva Software Release"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Release'
    __implements__ = (IPublication, IContainer)

    def __init__(self, id):
        SilvaSoftwareRelease.inheritedAttribute('__init__')(self, id)

    def get_silva_addables_allowed_in_publication(self):
        """return a list of allowed meta types in this type of object"""
        root = self.get_root()
        addables = extensionRegistry.get_addables()
        result = ['Silva Document']
        for addable in addables:
            if (addable.has_key('instance') and
                    IAsset.isImplementedByInstancesOf(addable['instance']) and
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
            if ISilvaSoftwareFile.isImplementedBy(obj):
                ret.append(obj)
        return ret

    def is_transparent(self):
        """returns 1 to make this software package's contents show up
            in tab_status of the package it's in"""
        return 1

InitializeClass(SilvaSoftwareRelease)

def manage_addSilvaSoftwareRelease(self, id, title, version, REQUEST=None):
    if not mangle.Id(self, id).isValid():
        return
    o = SilvaSoftwareRelease(id)
    self._setObject(id, o)
    object = getattr(self, id)
    object.set_title(title)
    
    binding = self.service_metadata.getMetadata(object)
    errors = binding.setValues('silva-software', {'releaseversion': version.encode('UTF-8')})
    if errors is not None:
        raise TypeError, errors['releaseversion']

    # add index document
    object.manage_addProduct['SilvaDocument'].manage_addDocument('index', title)

    add_and_edit(self, id, REQUEST)
    return ''

manage_addSilvaSoftwareReleaseForm = PageTemplateFile("www/silvaSoftwareReleaseAdd", 
                globals(), __name__ = 'manage_addSilvaSoftwareReleaseForm')

registerTypeForMetadata(SilvaSoftwareRelease.meta_type)
