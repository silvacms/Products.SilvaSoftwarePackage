# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from pkg_resources import parse_version

from Products.Silva.Folder.order import OrderManager

from five import grok
from zope import interface, schema
from zope.traversing.browser import absoluteURL

from silva.core import conf as silvaconf
from silva.core.interfaces import IAsset, IAddableContents
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IPreviewLayer
from silva.core.smi.settings import Settings
from zeam.form import silva as silvaforms

from . import interfaces
from .SilvaSoftwareContent import SilvaSoftwareContent


class SilvaSoftwarePackage(SilvaSoftwareContent):
    """A package represent a software and contains releases.
    """
    meta_type = 'Silva Software Package'
    grok.implements(interfaces.ISilvaSoftwarePackage)

    silvaconf.icon('software_package.png')
    silvaconf.priority(9)

    is_package_deprecated = False
    package_version_matrix = u""

    def get_silva_addables_allowed_in_container(self):
        result = ['Silva Document', 'Silva Software Release']
        result.extend(IAddableContents(self).get_all_addables(IAsset))
        return result


class PackageOrderManager(OrderManager):
    """Packages keep their content in order.
    """
    grok.context(interfaces.ISilvaSoftwarePackage)

    def _get_id(self, content):
        return content.getId()

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


class IPackageSettings(interface.Interface):
    is_package_deprecated = schema.Bool(
        title=u"Is this package deprecated ?",
        description=u"A disclaimer will be presented on the package page " + \
            u"if this is checked",
        default=False)
    package_version_matrix = schema.Text(
        title=u"Version matrix for the package",
        required=False)


class PackageSettings(silvaforms.SMISubEditForm):
    grok.context(interfaces.ISilvaSoftwarePackage)
    grok.view(Settings)
    grok.order(5)

    label = u"Software package settings"
    fields = silvaforms.Fields(IPackageSettings)


class PackageView(silvaviews.View):
    grok.context(interfaces.ISilvaSoftwarePackage)

    def get_releases(self):
        self.deprecated = self.context.is_package_deprecated
        self.version_matrix = self.context.package_version_matrix
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

        def remote_detail(entry):
            viewable = entry.get_viewable()
            if viewable is not None:
                return {'name': entry.getId(),
                        'url': viewable.get_url()}
            return {'name': None, 'url': None}

        locale = self.request.locale
        format = locale.dates.getFormatter('dateTime', 'medium').format

        for entry in publishables:
            crea_date = entry.get_default().get_creation_datetime()
            files = filter(lambda info: info['name'] is not None,
                           map(remote_detail, entry.get_remote_files())) + \
                           map(file_detail, entry.get_files())
            releases.append({'name': self.content.get_title() + ' ' + entry.id,
                             'url': absoluteURL(entry, self.request),
                             'date': format(crea_date.asdatetime()),
                             'files': files})
        return releases

