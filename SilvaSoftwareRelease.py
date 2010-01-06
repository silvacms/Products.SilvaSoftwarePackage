# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from zope.interface import implements
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle
from Products.Silva.Publication import Publication
from Products.Silva.ExtensionRegistry import extensionRegistry
from interfaces import ISilvaSoftwareRelease

module_security = ModuleSecurityInfo(
    'Products.SilvaSoftwarePackage.SilvaSoftwareRelease')

import re
import DateTime

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import IAsset, IFile

module_security.declareProtected(SilvaPermissions.ReadSilvaContent,
                                    'test_version_string')
_version_reg = re.compile('^[0-9]+(\.[0-9]+)*(dev-r[0-9]+)?((a|b|rc)[0-9]*)?$')
def test_version_string(version):
    """test whether the version conforms to the required format"""
    if not _version_reg.search(version):
        raise TypeError, 'Version string has incorrect format!'

class SilvaSoftwareRelease(Publication):
    """Silva Software Release"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Release'
    implements(ISilvaSoftwareRelease)

    silvaconf.factory('manage_addSilvaSoftwareRelease')
    silvaconf.icon('software_release.png')
    silvaconf.priority(9)

    def get_silva_addables_allowed_in_container(self):

        allowed = super(SilvaSoftwareRelease, self).\
                  get_silva_addables_allowed_in_container()
        addables = extensionRegistry.get_addables()
        result = []

        for addable in addables:
            if (addable['name'] in allowed and
                IAsset.implementedBy(addable['instance'])):
                result.append(addable['name'])
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_files')
    def get_files(self):

        ret = []
        for obj in self.objectValues():
            if IFile.providedBy(obj):
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

    # add index document
    object.manage_addProduct['SilvaDocument'].manage_addDocument(
                                                    'index', version)
    index = getattr(object, 'index')
    index.set_unapproved_version_publication_datetime(DateTime.DateTime())
    index.approve_version()

    add_and_edit(self, version, REQUEST)
    return ''

class ReleaseView(silvaviews.View):

    silvaconf.context(ISilvaSoftwareRelease)

    def get_files(self):
        for entry in self.content.get_files():
            mod_date = entry.get_modification_datetime()
            size = entry.get_file_size()
            yield {'name': entry.get_filename(),
                   'url': entry.absolute_url(),
                   'date': mangle.DateTime(mod_date).toStr(),
                   'size': mangle.Bytes(size)}

