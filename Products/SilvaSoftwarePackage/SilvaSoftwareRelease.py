# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.Silva.Folder import Folder
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import IFile, IAddableContents
from silva.core.conf.utils import ISilvaFactoryDispatcher
from zeam.form import silva as silvaforms


VERSION = re.compile('^[0-9]+(\.[0-9]+)*(dev-r[0-9]+)?((a|b|c|rc)[0-9]*)?$')
def test_version_string(version):
    """test whether the version conforms to the required format.
    """
    if not VERSION.search(version):
        raise ValueError(u'Id is not a proper version!')


class SilvaSoftwareRelease(Folder):
    security = ClassSecurityInfo()
    meta_type = 'Silva Software Release'
    grok.implements(interfaces.ISilvaSoftwareRelease)

    silvaconf.factory('manage_addSilvaSoftwareRelease')
    silvaconf.icon('software_release.png')
    silvaconf.priority(9)

    def get_silva_addables_allowed_in_container(self):
        return IAddableContents(self).get_all_addables(IFile)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_files')
    def get_files(self):
        ret = []
        for obj in self.objectValues():
            if IFile.providedBy(obj):
                ret.append(obj)
        ret.sort(lambda a, b: cmp(a.id, b.id))
        return ret

InitializeClass(SilvaSoftwareRelease)


class ReleaseAddForm(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwareRelease)
    grok.name('Silva Software Release')


def manage_addSilvaSoftwareRelease(container, version, title=None):
    if ISilvaFactoryDispatcher.providedBy(container):
        container = container.Destination()

    if not mangle.Id(container, version).isValid():
        return

    # see whether the id is correct for usage as version
    test_version_string(version)

    release = SilvaSoftwareRelease(version)
    container._setObject(version, release)
    release = getattr(container, version)
    release.set_title(version)
    notify(ObjectCreatedEvent(release))
    return release


class ReleaseView(silvaviews.View):
    """Display a release.
    """
    grok.context(interfaces.ISilvaSoftwareRelease)

    def update(self):
        self.files = []
        locale = self.request.locale
        format = locale.dates.getFormatter('dateTime', 'medium').format
        for entry in self.content.get_files():
            mod_date = entry.get_modification_datetime()
            size = entry.get_file_size()
            self.files.append(
                {'name': entry.get_filename(),
                 'url': entry.absolute_url(),
                 'date': format(mod_date.asdatetime()),
                 'size': mangle.Bytes(size)})
        metadata = component.getUtility(IMetadataService)
        binding = metadata.getMetadata(self.context)
        self.contact_name = binding.get('silva-extra', 'contactname')
        self.contact_email = binding.get('silva-extra', 'contactemail')
        if self.contact_email:
            self.contact_email = self.contact_email.replace(u'@', u' at ')

