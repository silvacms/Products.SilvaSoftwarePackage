# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from pkg_resources import parse_version
import logging
import os.path

from five import grok
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.traversing.browser import absoluteURL
from zope import component

from Products.Silva.Publication import Publication
from Products.Silva.ExtensionRegistry import meta_types_for_interface
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaSoftwarePackage import interfaces
from Products.SilvaSoftwarePackage import rst_utils

from silva.core import conf as silvaconf
from silva.core.interfaces import ILink, IFile
from silva.core.interfaces.adapters import IPublicationWorkflow
from zeam.form import silva as silvaforms
from silva.core.views import views as silvaviews

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
        content.manage_addProduct['silva.app.document'].manage_addDocument(
            'index', content.get_title())
        index = getattr(content, 'index')
        IPublicationWorkflow(index).publish()


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

    def _get_package(self, description=None):
        package_name = self.request['name']
        package_version = self.request['version']

        if package_name.startswith('Products.'):
            package_name = package_name[9:]

        # By default the release uploaded is the last version of the package
        is_last_version = True

        #catalog = component.getUtility(ICatalogService)
        catalog = self.context.service_catalog
        query = {'meta_type': 'Silva Software Package',
                 'id': package_name,
                 'path': '/'.join(self.context.getPhysicalPath())}
        package_brains = catalog(query)
        if len(package_brains) == 1:
            package = package_brains[0].getObject()

            # Check if it is really the last version we know of
            last_packages_version = package.objectIds(meta_types_for_interface(IFile))
            if last_packages_version:
                last_packages_version = map(
                    parse_version, last_packages_version)
                last_packages_version.sort()
                if parse_version(package_version) < last_packages_version[-1]:
                    is_last_version = False
        else:
            logger.debug(u'Create package %s' % package_name)
            factory = self.context.manage_addProduct['SilvaSoftwarePackage']
            factory.manage_addSilvaSoftwarePackage(package_name, package_name)
            package = getattr(self.context, package_name)


        if (description is not None and is_last_version and
            not interfaces.ISilvaNoAutomaticUpdate.providedBy(package)):
            description = rst_utils.get_description(description)
            index = package.index
            IPublicationWorkflow(index).new_version()
            version_index = index.get_editable()
            version_index.body.save_raw_text(description.as_html(True))
            IPublicationWorkflow(index).publish()

        return (package, package_name, package_version)

    def _get_release(self, package, package_version):
        release = getattr(package, package_version, None)
        if release is None:
            logger.debug(u'Create release %s' % package_version)
            factory = package.manage_addProduct['SilvaSoftwarePackage']
            factory.manage_addSilvaSoftwareRelease(package_version)
            release = getattr(package, package_version)
        return release

    def render(self):
        description = None
        if self.request.form.has_key('description'):
            description = rst_utils.rst_parser(
                self.request['description'].split('\n'))

        package, package_name, package_version = self._get_package(description)
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
                      'shorttitle': package_version}

        metadata = component.getUtility(IMetadataService)
        binding = metadata.getMetadata(release)
        binding.setValues('silva-extra', release_info, reindex=1)
        binding.setValues('silva-content', title_info, reindex=1)
        release.sec_update_last_author_info()

        if description is not None:
            changes = rst_utils.get_last_changes(description)

            index = release.index
            IPublicationWorkflow(index).new_version()
            version_index = index.get_editable()
            if changes is not None:
                version_index.body.save_raw_text(changes.as_html(False))
            binding = metadata.getMetadata(version_index)
            binding.setValues('silva-extra', release_info, reindex=1)
            binding.setValues('silva-content', title_info, reindex=1)
            IPublicationWorkflow(index).publish()
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
        status = u'Uploaded'
        package, package_name, package_version = self._get_package()
        release = self._get_release(package, package_version)
        filename = self.request['content'].filename

        archive = getattr(release, filename, None)
        if archive is not None:
            release.manage_delObjects([filename])
            status = u'Replaced'

        factory = release.manage_addProduct['Silva']
        factory.manage_addFile(filename, filename, self.request['content'])
        self.response.setStatus(200)
        return status


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



