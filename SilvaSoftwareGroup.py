# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.Publication import Publication
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope.traversing.browser import absoluteURL

from silva.core import conf as silvaconf
from silva.core.interfaces import ILink
from silva.core.views import z3cforms


class SilvaSoftwareGroup(Publication):
    meta_type = 'Silva Software Group'
    grok.implements(interfaces.ISilvaSoftwareGroup)

    silvaconf.icon('software_group.png')
    silvaconf.priority(8)

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Document',
                'Silva Link',
                'Silva Software Group',
                'Silva Software Package',]


class GroupAdd(z3cforms.AddForm):

    silvaconf.context(interfaces.ISilvaSoftwareGroup)
    silvaconf.name('Silva Software Group')



class GroupPreview(grok.View):

    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.name('group_preview')

    def update(self):
        self.packages = []
        for package in self.context.get_ordered_publishables():
            if (not interfaces.ISilvaSoftwareRelease.providedBy(package) or
                not ILink.providedBy(package)):
                continue
            if not package.is_published():
                continue
            if ILink.providedBy(package):
                url = package.get_url()
            else:
                url = absoluteURL(package, self.context)
            self.packages.append(
                {'name': package.get_title(),
                 'url': url})
