# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle
from Products.Silva.Folder import Folder
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaDocument.Document import DocumentHTML
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import IAsset, IFile

import re


module_security = ModuleSecurityInfo(
    'Products.SilvaSoftwarePackage.SilvaSoftwareRelease')
module_security.declareProtected(
    SilvaPermissions.ReadSilvaContent, 'test_version_string')
_version_reg = re.compile('^[0-9]+(\.[0-9]+)*(dev-r[0-9]+)?((a|b|rc)[0-9]*)?$')
def test_version_string(version):
    """test whether the version conforms to the required format.
    """
    if not _version_reg.search(version):
        raise TypeError, 'Version string has incorrect format!'


class SilvaSoftwareRelease(Folder):

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Release'
    grok.implements(interfaces.ISilvaSoftwareRelease)

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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_files')
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


def manage_addSilvaSoftwareRelease(container, version, REQUEST=None):
    if not mangle.Id(container, version).isValid():
        return

    # see whether the id is correct for usage as version
    test_version_string(version)

    release = SilvaSoftwareRelease(version)
    container._setObject(version, release)
    release = getattr(container, version)
    release.set_title(version)
    notify(ObjectCreatedEvent(release))
    add_and_edit(container, version, REQUEST)
    return release


class ReleaseView(silvaviews.View):
    """Display a release.
    """
    grok.context(interfaces.ISilvaSoftwareRelease)

    def update(self):
        self.files = []
        for entry in self.content.get_files():
            mod_date = entry.get_modification_datetime()
            size = entry.get_file_size()
            self.files.append(
                {'name': entry.get_filename(),
                 'url': entry.absolute_url(),
                 'date': mangle.DateTime(mod_date).toStr(),
                 'size': mangle.Bytes(size)})
        metadata = component.getUtility(IMetadataService)
        binding = metadata.getMetadata(self.context)
        self.contact_name = binding.get('silva-extra', 'contactname')
        self.contact_email = binding.get('silva-extra', 'contactemail')
        if self.contact_email:
            self.contact_email = self.contact_email.replace(u'@', u' at ')

        description = self.context.get_default()
        if description is not None:
            description = description.get_viewable()
            if description is not None:
                description = DocumentHTML.transform(description, self.request)
        self.description = description
