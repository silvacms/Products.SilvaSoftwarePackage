# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.traversing.browser import absoluteURL


from Products.Silva.Publication import Publication
from Products.SilvaSoftwarePackage import interfaces

from silva.core import conf as silvaconf
from silva.core.interfaces import ILink
from silva.core.views import z3cforms
from silva.core.views import views as silvaviews

from five import grok
import os.path

import DateTime


class SilvaSoftwareCenter(Publication):
    meta_type = 'Silva Software Center'
    grok.implements(interfaces.ISilvaSoftwareCenter)

    silvaconf.icon('software_group.png')
    silvaconf.priority(9)

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Software Group', 'Silva Software Package',]


@grok.subscribe(interfaces.ISilvaSoftwareContent, IObjectCreatedEvent)
def addDefaultDocument(content, event):
    if event.object is not content:
        return
    if not hasattr(content, 'index'):
        content.manage_addProduct['SilvaDocument'].manage_addDocument(
            'index', content.get_title())
        index = getattr(content, 'index')
        index.set_unapproved_version_publication_datetime(DateTime.DateTime())
        index.approve_version()


class CenterAdd(z3cforms.AddForm):

    silvaconf.context(interfaces.ISilvaSoftwareCenter)
    silvaconf.name('Silva Software Center')


class CenterView(silvaviews.View):

    silvaconf.context(interfaces.ISilvaSoftwareGroup)

    def update(self):
        self.groups = []
        self.packages = []
        for content in self.context.get_ordered_publishables():
            if not (interfaces.ISilvaSoftwareGroup.providedBy(content) or
                    interfaces.ISilvaSoftwarePackage.providedBy(content) or
                    ILink.providedBy(content)):
                continue
            if not content.is_published():
                continue
            if interfaces.ISilvaSoftwareGroup.providedBy(content):
                self.groups.append(content)
            else:
                if ILink.providedBy(content):
                    url = content.get_viewable().get_url()
                else:
                    url = absoluteURL(content, self.request)
                self.packages.append({'name': content.get_title(), 'url': url})


class CenterRegister(grok.View):
    """Register support for distutils.
    """

    grok.context(interfaces.ISilvaSoftwareCenter)
    grok.require('silva.ChangeSilvaContent')
    grok.name('submit')


    def _get_package(self):
        package_name = self.request['name']
        package_version = self.request['version']

        if package_name.startswith('Products.'):
            package_name = package_name[9:]

        # TODO: Replace this with a catalog query
        package = getattr(self.context, package_name, None)
        if package is None:
            factory = self.context.manage_addProduct['SilvaSoftwarePackage']
            package_title = package_name.replace('.', ' ')
            factory.manage_addSilvaSoftwarePackage(package_name, package_title)
            package = getattr(self.context, package_name)
            package.sec_update_last_author_info()

        return (package, package_name, package_version)

    def _get_release(self, package, package_version):
        release = getattr(package, package_version, None)
        if release is None:
            factory = package.manage_addProduct['SilvaSoftwarePackage']
            factory.manage_addSilvaSoftwareRelease(package_version)
            release = getattr(package, package_version)
            release.sec_update_last_author_info()
        return release

    def render(self):
        package, package_name, package_version = self._get_package()

        release = getattr(package, package_version, None)
        if release is not None:
            self.response.setStatus(409) # Conflict
            return u'Already registered'

        release = self._get_release(package, package_version)

        binding = self.context.service_metadata.getMetadata(release)
        binding.setValues('silva-extra',
                          {'contactname': self.request['author'],
                           'contactemail': self.request['author_email'],
                           'keywords': self.request['keywords'],
                           'subject': self.request['summary']})

        self.response.setStatus(200)
        return u'Registered'


class CenterUpload(CenterRegister):
    """Upload support for distutils.
    """

    grok.context(interfaces.ISilvaSoftwareCenter)
    grok.require('silva.ChangeSilvaContent')
    grok.name('file_upload')

    def render(self):
        package, package_name, package_version = self._get_package()
        release = self._get_release(package, package_version)
        filename = self.request['content'].filename

        archive = getattr(release, filename, None)
        if archive is not None:
            self.response.setStatus(409) # Conflict
            return u'Already uploaded'

        factory = release.manage_addProduct['Silva']
        factory.manage_addFile(filename, filename, self.request['content'])
        release_file = getattr(release, filename)
        release_file.sec_update_last_author_info()

        self.response.setStatus(200)
        return u'Uploaded'


VALID_SIMPLE_FILES_EXT = ['.gz', '.tgz', '.zip', '.egg', '.zexp']

class CenterSimple(grok.View):
    """Simple view listing package of the center.
    """

    grok.context(interfaces.ISilvaSoftwareCenter)
    grok.name('simple')

    def get_releases(self):
        query = {'meta_type': 'Silva File',
                 'path': '/'.join(self.context.getPhysicalPath())}
        for brain in self.context.service_catalog(query):
            name, ext = os.path.splitext(brain.id)
            if ext in VALID_SIMPLE_FILES_EXT:
                yield {'name': brain.id,
                       'url': brain.getURL()}



