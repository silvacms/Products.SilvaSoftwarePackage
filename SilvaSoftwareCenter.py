# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.traversing.browser import absoluteURL
from zope import component

from Products.Silva.Publication import Publication
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaSoftwarePackage import interfaces

from silva.core import conf as silvaconf
from silva.core.interfaces import ILink
from zeam.form import silva as silvaforms
from silva.core.views import views as silvaviews

from docutils.core import publish_parts
import logging
import os.path
import DateTime

logger = logging.getLogger('silva software center')


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
    if not hasattr(content.aq_base, 'index'):
        content.manage_addProduct['SilvaDocument'].manage_addDocument(
            'index', content.get_title())
        index = getattr(content, 'index')
        index.set_unapproved_version_publication_datetime(DateTime.DateTime())
        index.approve_version()


class CenterAdd(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwareCenter)
    grok.name('Silva Software Center')


class CenterView(silvaviews.View):
    grok.context(interfaces.ISilvaSoftwareGroup)

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

        #catalog = component.getUtility(ICatalogService)
        catalog = self.context.service_catalog
        query = {'meta_type': 'Silva Software Package',
                 'id': package_name,
                 'path': '/'.join(self.context.getPhysicalPath())}
        package_brains = catalog(query)
        if len(package_brains) == 1:
            package = package_brains[0].getObject()
        else:
            logger.debug(u'Create package %s' % package_name)
            factory = self.context.manage_addProduct['SilvaSoftwarePackage']
            factory.manage_addSilvaSoftwarePackage(package_name, package_name)
            package = getattr(self.context, package_name)
            package.sec_update_last_author_info()

        return (package, package_name, package_version)

    def _get_release(self, package, package_version):
        release = getattr(package, package_version, None)
        if release is None:
            logger.debug(u'Create release %s' % package_version)
            factory = package.manage_addProduct['SilvaSoftwarePackage']
            factory.manage_addSilvaSoftwareRelease(package_version)
            release = getattr(package, package_version)
            release.sec_update_last_author_info()
        return release

    def render(self):
        package, package_name, package_version = self._get_package()

        release = getattr(package, package_version, None)
        if release is not None:
            logger.info(u'Release %s of %s already registered' %
                        (package_version, package_name))

        release = self._get_release(package, package_version)
        release_info = {'contactname': self.request.get('author', ''),
                        'contactemail': self.request.get('author_email', ''),
                        'keywords': self.request.get('keywords', ''),
                        'subject': self.request.get('summary', '')}
        title_info = {'maintitle': u'%s %s' % (package_name, package_version),
                      'shorttitle': package_name}

        metadata = component.getUtility(IMetadataService)
        binding = metadata.getMetadata(release)
        binding.setValues('silva-extra', release_info, reindex=1)
        binding.setValues('silva-content', title_info, reindex=1)
        release.sec_update_last_author_info()

        if self.request.form.has_key('description'):
            description = publish_parts(
                self.request['description'],
                parser_name='restructuredtext',
                writer_name='html')['whole']

            index = release.index
            index.create_copy()
            index.editor_storage(description, editor='kupu')
            binding = metadata.getMetadata(index.get_editable())
            binding.setValues('silva-extra', release_info, reindex=1)
            binding.setValues('silva-content', title_info, reindex=1)
            index.sec_update_last_author_info()
            index.set_unapproved_version_publication_datetime(
                DateTime.DateTime())
            index.approve_version()
        else:
            logger.info(u'No description available for %s %s' %
                        (package_name, package_version))

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
                 'path': '/'.join(self.context.getPhysicalPath()),
                 'sort_on': 'id'}
        #catalog = component.getUtility(ICatalogService)
        catalog = self.context.service_catalog
        for brain in catalog(query):
            name, ext = os.path.splitext(brain.id)
            if ext in VALID_SIMPLE_FILES_EXT:
                yield {'name': brain.id,
                       'url': brain.getURL()}



