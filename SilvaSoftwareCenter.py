# Copyright (c) 2004-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from zope.app.container.interfaces import IObjectAddedEvent

from Products.Silva.Publication import Publication
from Products.SilvaSoftwarePackage.interfaces import \
    ISilvaSoftwareCenter, ISilvaSoftwarePackage

from silva.core import conf as silvaconf
from silva.core.views import z3cforms
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IPreviewLayer

from five import grok



class SilvaSoftwareCenter(Publication):
    security = ClassSecurityInfo()
    meta_type = 'Silva Software Center'
    implements(ISilvaSoftwareCenter)

    silvaconf.icon('software_package.png')
    silvaconf.priority(9)

    def get_silva_addables_allowed_in_publication(self):
        return ['Silva Software Package']

InitializeClass(SilvaSoftwareCenter)


@silvaconf.subscribe(ISilvaSoftwareCenter, IObjectAddedEvent)
def addDefaultDocument(center, event):
    if event.oldParent is None:
        center.manage_addProduct['SilvaDocument'].manage_addDocument(
            'index', center.get_title())


class CenterAdd(z3cforms.AddForm):

    silvaconf.context(ISilvaSoftwareCenter)
    silvaconf.name('Silva Software Center')


class CenterView(silvaviews.View):

    silvaconf.context(ISilvaSoftwareCenter)

    def get_packages(self):

        publishables = self.content.get_ordered_publishables()
        publishables = [obj for obj in publishables
                        if ISilvaSoftwarePackage.providedBy(obj)]

        if not IPreviewLayer.providedBy(self.request):
            publishables = [obj for obj in publishables
                            if obj.get_default().get_public_version()]

        for entry in publishables:
            yield {'name': entry.get_title(),
                   'url': entry.absolute_url()}


class CenterRegister(grok.View):
    """Register support for distutils.
    """

    grok.context(ISilvaSoftwareCenter)
    #grok.require('silva.ChangeSilvaContent')
    grok.name('submit')


    def _get_package(self):
        package_name = self.request['name']
        package_version = self.request['version']

        if package_name.startswith('Products.'):
            package_name = package_name[9:]

        package = getattr(self.context, package_name, None)
        if package is None:
            factory = self.context.manage_addProduct['SilvaSoftwarePackage']
            package_title = package_name.replace('.', ' ')
            factory.manage_addSilvaSoftwarePackage(package_name, package_title)
            package = getattr(self.context, package_name)

        return (package, package_name, package_version)

    def _get_release(self, package, package_version):
        release = getattr(package, package_version, None)
        if release is None:
            factory = package.manage_addProduct['SilvaSoftwarePackage']
            factory.manage_addSilvaSoftwareRelease(package_version)
            release = getattr(package, package_version)
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

    grok.context(ISilvaSoftwareCenter)
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

        self.response.setStatus(200)
        return u'Uploaded'


class CenterSimple(grok.View):
    """Simple view listing package of the center.
    """

    grok.context(ISilvaSoftwareCenter)
    grok.name('simple')

    def get_releases(self):
        query = {'meta_type': 'Silva File',
                 'path': '/'.join(self.context.getPhysicalPath())}
        for brain in self.context.service_catalog(query):
            yield {'name': brain.id,
                   'url': brain.getURL()}



