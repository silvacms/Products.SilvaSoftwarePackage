# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import json

from five import grok
from zope import component
from zope import schema
from zope.interface import Interface
from zope.traversing.browser import absoluteURL

from silva.core import conf as silvaconf
from silva.core.interfaces import ILink, IFile, IFeedEntry, IFeedEntryProvider
from silva.core.services.interfaces import IMetadataService
from silva.core.smi.settings import Settings
from silva.core.xml.xmlexport import Exporter
from zeam.form import silva as silvaforms

from . import interfaces
from .SilvaSoftwareContent import SilvaSoftwareContent


class SilvaSoftwareGroup(SilvaSoftwareContent):
    meta_type = 'Silva Software Group'
    grok.implements(interfaces.ISilvaSoftwareGroup)

    silvaconf.icon('software_group.png')
    silvaconf.priority(8)

    group_tag = u""
    is_group_archive = False

    def fulltext(self):
        text = super(SilvaSoftwareGroup, self).fulltext()
        default = self.get_default()
        if default is not None and hasattr(default, 'fulltext'):
            text.extend(default.fulltext())
        return text

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Document',
                'Silva Link',
                'Silva Software Group',
                'Silva Software Package',]


class GroupAdd(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.name('Silva Software Group')


class IGroupSettings(Interface):
    is_group_archive = schema.Bool(
        title=u"Is this group an archive ?",
        description=u"The group will be listed in the archive section",
        default=False)
    group_tag = schema.TextLine(
        title=u"Group tag",
        description=u"Mutliple groups will be presented together if " +\
            u"they share the same tag",
        required=False)


class GroupSettings(silvaforms.SMISubEditForm):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.view(Settings)
    grok.order(5)

    label = u"Software group settings"
    fields = silvaforms.Fields(IGroupSettings)


class GroupPreview(grok.View):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.name('group_preview')

    def update(self):
        self.is_archive = self.context.is_group_archive
        self.packages = []
        if not self.is_archive:
            for content in self.context.get_ordered_publishables():
                if not (interfaces.ISilvaSoftwarePackage.providedBy(content) or
                        ILink.providedBy(content)):
                    continue
                if not content.is_published():
                    continue
                if ILink.providedBy(content):
                    url = content.get_viewable().get_url()
                else:
                    url = absoluteURL(content, self.request)
                self.packages.append({'name': content.get_title(), 'url': url})



class GroupExport(grok.View):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.name('group_export.json')

    def export(self, container):
        export = Exporter(container, self.request, {'only_container': True})
        default = container.get_default()
        if default is not None:
            default = Exporter(default, self.request, {'external_rendering': True})
        return {
            'identifier': container.getId(),
            'index': default is not None and default.getString() or None,
            'export': export.getString()}

    def update(self):
        self.data = []
        for package in self.context.get_ordered_publishables(
            interfaces.ISilvaSoftwarePackage):
            package_json = self.export(package)
            package_json['releases'] = releases_json = []
            for release in package.get_ordered_publishables(
                interfaces.ISilvaSoftwareRelease):
                release_json = self.export(release)
                releases_json.append(release_json)
                release_json['files'] = files_json = []
                for release_file in release.get_non_publishables(IFile):
                    files_json.append({
                            'identifier': release_file.getId(),
                            'title': release_file.get_title(),
                            'url': absoluteURL(release_file, self.request)})
            self.data.append(package_json)

    def render(self):
        self.response.setHeader('Content-Type', 'application/json')
        return json.dumps(self.data)


class ReleaseFeedEntry(object):
    grok.implements(IFeedEntry)

    def __init__(self, context, request):
        self.request = request
        self.package = context.aq_parent
        self.release = context
        service_metadata = component.getUtility(IMetadataService)
        self.metadata = service_metadata.getMetadata(self.release)

    def id(self):
        return self.url()

    def title(self):
        return u'%s %s' % (
            self.package.get_title(),
            self.release.getId())

    def subject(self):
        return None

    def html_description(self):
        return self.description()

    def description(self):
        return self.metadata.get('silva-extra', 'subject')

    def url(self):
        return absoluteURL(self.release, self.request)

    def authors(self):
        contact = self.metadata.get('silva-extra', 'contactname')
        if contact is not None:
            return [contact,]
        return []

    def date_updated(self):
        return self.metadata.get('silva-extra', 'modificationtime')

    def date_published(self):
        return self.metadata.get('silva-extra', 'creationtime')

    def keywords(self):
        keywords = self.metadata.get('silva-extra', 'keywords')
        return [k for k in keywords.split() if k]


class GroupFeedEntryProvider(grok.MultiAdapter):
    grok.adapts(interfaces.ISilvaSoftwareGroup, Interface)
    grok.provides(IFeedEntryProvider)
    grok.implements(IFeedEntryProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def entries(self):
        catalog = self.context.service_catalog
        query = {'meta_type': 'Silva Software Release',
                 'path': '/'.join(self.context.getPhysicalPath())}
        for brain in catalog(query):
            yield ReleaseFeedEntry(brain.getObject(), self.request)
