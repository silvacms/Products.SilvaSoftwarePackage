# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Silva import SilvaPermissions
from Products.Silva import mangle

from five import grok
from zope import component
from zope.event import notify

from silva.core import conf as silvaconf
from silva.core.conf.utils import ISilvaFactoryDispatcher
from silva.core.interfaces import IAddableContents, ContentCreatedEvent
from silva.core.interfaces import IFile, ILink
from silva.core.services.interfaces import IMetadataService
from silva.core.views import views as silvaviews
from zeam.form import silva as silvaforms

from . import interfaces
from .SilvaSoftwareContent import SilvaSoftwareContent

VERSION = re.compile('^[0-9]+(\.[0-9]+)*(dev-r[0-9]+)?((a|b|c|rc)[0-9]*)?$')
def test_version_string(version):
    """test whether the version conforms to the required format.
    """
    if not VERSION.search(version):
        raise ValueError(u'{} is not a proper version!'.format(version))


class SilvaSoftwareRelease(SilvaSoftwareContent):
    security = ClassSecurityInfo()
    meta_type = 'Silva Software Release'
    grok.implements(interfaces.ISilvaSoftwareRelease)

    silvaconf.factory('manage_addSilvaSoftwareRelease')
    silvaconf.icon('SilvaSoftwareRelease.png')
    silvaconf.priority(9)

    def get_silva_addables_allowed_in_container(self):
        return IAddableContents(self).get_all_addables(IFile)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_files')
    def get_files(self):
        return self.get_non_publishables(IFile)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_remote_files')
    def get_remote_files(self):
        return self.get_ordered_publishables(ILink)

InitializeClass(SilvaSoftwareRelease)


class ReleaseAddForm(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwareRelease)
    grok.name('Silva Software Release')


def manage_addSilvaSoftwareRelease(container, version, title=None,
                                   no_default_content=False):
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
    notify(ContentCreatedEvent(release, no_default_content=no_default_content))
    return release


class ReleaseView(silvaviews.View):
    """Display a release.
    """
    grok.context(interfaces.ISilvaSoftwareRelease)

    def update(self):
        self.files = []
        locale = self.request.locale
        format = locale.dates.getFormatter('dateTime', 'medium').format
        self.have_size = False
        for entry in self.content.get_remote_files():
            target = entry.get_viewable()
            if target is None:
                continue
            mod_date = target.get_modification_datetime()
            self.files.append(
                {'name': entry.getId(),
                 'url': target.get_url(),
                 'date': format(mod_date.asdatetime()),
                 'size': '-'})
        for entry in self.content.get_files():
            mod_date = entry.get_modification_datetime()
            size = entry.get_file_size()
            self.have_size = True
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

