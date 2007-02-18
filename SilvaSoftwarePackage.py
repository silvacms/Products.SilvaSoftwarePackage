# Copyright (c) 2004 Guido Wesdorp. All rights reserved.
# See also LICENSE.txt
# $Id: SilvaSoftwarePackage.py,v 1.8 2005/03/14 11:22:58 guido Exp $
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implements
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva.Publication import Publication
from Products.Silva.interfaces import IContainer, IPublication, IAsset
from Products.Silva import mangle
from DateTime import DateTime
from Products.Silva.ExtensionRegistry import extensionRegistry

from Products.ProxyIndex.ProxyIndex import RecordStyle
from Products.SilvaSoftwarePackage.interfaces import \
    ISilvaSoftwarePackage, ISilvaSoftwareFile

import re

icon = "www/software_package.png"
addable_priority = 9

class SilvaSoftwarePackage(Publication):
    """Silva Software Package"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Package'
    implements(ISilvaSoftwarePackage)

    def __init__(self, id):
        Publication.__init__(self, id)
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_releases')
    def get_releases(self, published=1):
        """get all (published) software releases contained"""
        ret = []
        publishables = self.get_ordered_publishables()
        publishables = [obj for obj in publishables 
                          if obj.meta_type == 'Silva Software Release']
        publishables.sort(self._sort_by_version)
        if published:
            publishables = [obj for obj in publishables
                              if obj.get_default().get_public_version()]
        publishables.sort(self._sort_by_version)
        return publishables
    
    def get_silva_addables_allowed_in_publication(self):
        """return a list of allowed meta types in this type of object"""
        root = self.get_root()
        addables = extensionRegistry.get_addables()
        result = ['Silva Document', 'Silva Software Release']
        for addable in addables:
            if (addable.has_key('instance') and
                    IAsset.implementedBy(addable['instance']) and
                    not ISilvaSoftwareFile.implementedBy(addable['instance']) and
                    self.service_view_registry.has_view('add', 
                        addable['name'])):
                result.append(addable['name'])
        return result

    _numreg = re.compile('^[0-9]+$')
    _lastbitreg = re.compile('^([0-9]*)([a-z]*)([0-9]*?)$')
    def _sort_by_version(self, a, b):
        """comparison function for sorting a list of Release objects"""
        return self._sort_by_version_helper(a.id, b.id)

    def _sort_by_version_helper(self, aver, bver):
        # first split the versions into tuples and compare the numbers
        atup = aver.split('.')
        btup = bver.split('.')
        i = 0
        for i in range(len(atup)):
            if len(btup) <= i:
                return -1
            if (not self._numreg.search(atup[i]) or
                    not self._numreg.search(btup[i])):
                break
            if int(atup[i]) > int(btup[i]):
                return -1
            elif int(atup[i]) < int(btup[i]):
                return 1
        # now check for the complex bit at the end
        match = self._lastbitreg.search(atup[i])
        if not match:
            raise Exception, 'Version not valid: %s' % aver
        anum = match.group(1)
        atype = match.group(2).strip()
        aver = match.group(3)
        match = self._lastbitreg.search(btup[i])
        if not match:
            raise Exception, 'Version not valid: %s' % bver
        bnum = match.group(1)
        btype = match.group(2).strip()
        bver = match.group(3)
        if anum > bnum:
            return -1
        elif bnum > anum:
            return 1
        if atype:
            if not btype:
                return 1
            # it seems we can just do a string compare here, 'a' < 'b' < 'rc'
            if atype > btype:
                return -1
            elif btype > atype:
                return 1
        elif not atype and btype:
            return -1
        if aver or bver:
            if aver and not bver:
                return -1
            if bver and not aver:
                return 1
            if aver < bver:
                return 1
            if bver < aver:
                return -1
        return 0

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'get_software_file_paths')
    def get_software_file_paths(self):
        """Get all contained software files"""
        query = {'meta_type': 'Silva Software File',
                    'path': '/'.join(self.getPhysicalPath())}
        result = self.service_catalog(query)
        result = [b.getPath() for b in result]
        return result

InitializeClass(SilvaSoftwarePackage)

def manage_addSilvaSoftwarePackage(self, id, title, REQUEST=None):
    if not mangle.Id(self, id).isValid():
        return
    o = SilvaSoftwarePackage(id)
    self._setObject(id, o)
    object = getattr(self, id)
    object.set_title(title)
    object.manage_addProduct['SilvaDocument'].manage_addDocument(
                                                    'index', title)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addSilvaSoftwarePackageForm = PageTemplateFile(
                                "www/silvaSoftwarePackageAdd", 
                                globals(),
                                __name__='manage_addSilvaSoftwarePackageForm')

registerTypeForMetadata(SilvaSoftwarePackage.meta_type)
