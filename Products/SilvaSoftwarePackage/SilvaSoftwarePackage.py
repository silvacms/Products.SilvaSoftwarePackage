# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from pkg_resources import parse_version

from Products.Silva.Folder import Folder
from Products.Silva import mangle
from Products.Silva.Folder.order import OrderManager
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope.traversing.browser import absoluteURL

from silva.core import conf as silvaconf
from silva.core.interfaces import IAsset, IAddableContents
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IPreviewLayer
from zeam.form import silva as silvaforms


class SilvaSoftwarePackage(Folder):
    """A package represent a software and contains releases.
    """
    meta_type = 'Silva Software Package'
    grok.implements(interfaces.ISilvaSoftwarePackage)

    silvaconf.icon('software_package.png')
    silvaconf.priority(9)

    def get_silva_addables_allowed_in_container(self):
        result = ['Silva Document', 'Silva Software Release']
        result.extend(IAddableContents(self).get_all_addables(IAsset))
        return result


class PackageOrderManager(OrderManager):
    """Packages keep their content in order.
    """
    grok.context(interfaces.ISilvaSoftwarePackage)

    def add(self, content):
        if super(PackageOrderManager, self).add(content):
            self.order.sort(key=parse_version)
            return True
        return False

    def move(self, content, position):
        return False


class PackageAdd(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwarePackage)
    grok.name('Silva Software Package')


class PackageView(silvaviews.View):
    grok.context(interfaces.ISilvaSoftwarePackage)

    def get_releases(self):
        releases = []
        publishables = self.content.get_ordered_publishables()
        publishables = [obj for obj in publishables
                        if interfaces.ISilvaSoftwareRelease.providedBy(obj)]

        if not IPreviewLayer.providedBy(self.request):
            publishables = [obj for obj in publishables
                            if obj.get_default().get_public_version()]

        def sort_by_version(a, b):
            return -cmp(parse_version(a.id), parse_version(b.id))

        publishables.sort(sort_by_version)

        def file_detail(entry):
            return {'name': entry.get_filename(),
                    'url': absoluteURL(entry, self.request)}

        for entry in publishables:
            crea_date = entry.get_default().get_creation_datetime()
            files = map(file_detail, entry.get_files())
            releases.append({'name': self.content.get_title() + ' ' + entry.id,
                             'url': absoluteURL(entry, self.request),
                             'date': mangle.DateTime(crea_date).toStr(),
                             'files': files})
        return releases

