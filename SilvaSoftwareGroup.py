# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.Folder import Folder
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope import component
from zope.traversing.browser import absoluteURL

from silva.core import conf as silvaconf
from silva.core.interfaces import ILink, IFeedEntry, IFeedEntryProvider
from zeam.form import silva as silvaforms


class SilvaSoftwareGroup(Folder):
    meta_type = 'Silva Software Group'
    grok.implements(interfaces.ISilvaSoftwareGroup)

    silvaconf.icon('software_group.png')
    silvaconf.priority(8)

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Document',
                'Silva Link',
                'Silva Software Group',
                'Silva Software Package',]


class GroupAdd(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.name('Silva Software Group')



class GroupPreview(grok.View):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.name('group_preview')

    def update(self):
        self.packages = []
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


class ReleaseFeedEntry(object):
    grok.implements(IFeedEntry)

    def __init__(self, context):
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
        # !@$!@$!$@!$!??????
        return self.release.absolute_url()

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


class GroupFeedEntryProvider(grok.Adapter):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.provides(IFeedEntryProvider)
    grok.implements(IFeedEntryProvider)

    def entries(self):
        catalog = self.context.service_catalog
        query = {'meta_type': 'Silva Software Release',
                 'path': '/'.join(self.context.getPhysicalPath())}
        for brain in catalog(query):
            yield ReleaseFeedEntry(brain.getObject())
