# Copyright (c) 2004 Guido Wesdorp. All rights reserved.
# See also LICENSE.txt
# $Id: SilvaSoftwarePackage.py,v 1.2 2004/07/28 17:29:41 guido Exp $
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.Publication import Publication
from Products.Silva.interfaces import IContainer, IPublication, IAsset
from Products.Silva import mangle
from DateTime import DateTime
from Products.Silva.ExtensionRegistry import extensionRegistry

from Products.ProxyIndex.ProxyIndex import RecordStyle

import re

icon = "www/silvageneric.gif"

class SilvaSoftwarePackage(Publication):
    """Silva Software Package"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Package'
    __implements__ = (IContainer, IPublication)

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
        return publishables
    
    def get_silva_addables_allowed_in_publication(self):
        """return a list of allowed meta types in this type of object"""
        root = self.get_root()
        addables = extensionRegistry.get_addables()
        result = ['Silva Document', 'Silva Software Release']
        for addable in addables:
            if (addable.has_key('instance') and
                    IAsset.isImplementedByInstancesOf(addable['instance']) and
                    self.service_view_registry.has_view('add', 
                        addable['name'])):
                result.append(addable['name'])
        return result

    _numreg = re.compile('^[0-9]+$')
    _lastbitreg = re.compile('^([0-9]*)([a-z]*)([0-9]*)$')
    def _sort_by_version(self, a, b):
        """comparison function for sorting a list of Release objects"""
        abinding = self.service_metadata.getMetadata(a)
        bbinding = self.service_metadata.getMetadata(b)
        aver = abinding.get('silva-software', 'releaseversion')
        bver = bbinding.get('silva-software', 'releaseversion')
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
        if self._numreg.search(atup[i]) and not self._numreg.search(btup[i]):
            return -1
        elif self._numreg.search(btup[i]) and not self._numreg.search(atup[i]):
            return 1
        match = self._lastbitreg.search(atup[i])
        anum = match.group(1)
        atype = match.group(2)
        aver = match.group(3)
        match = self._lastbitreg.search(btup[i])
        bnum = match.group(1)
        btype = match.group(2)
        bver = match.group(3)
        if anum > bnum:
            return -1
        elif bnum > anum:
            return 1
        if atype:
            if not btype:
                return -1
            # it seems we can just do a string compare here, 'a' < 'b' < 'rc'
            if atype > btype:
                return -1
            elif btype > atype:
                return 1
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
                                'get_software_files')
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
