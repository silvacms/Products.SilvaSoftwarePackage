# Copyright (c) 2004-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from zope.app.container.interfaces import IObjectAddedEvent

from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit
from Products.Silva.Publication import Publication
from Products.Silva import mangle
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.SilvaSoftwarePackage.interfaces import \
    ISilvaSoftwarePackage, ISilvaSoftwareRelease

import re
import DateTime
from pkg_resources import parse_version

from silva.core import conf as silvaconf
from silva.core.views import z3cforms
from silva.core.views import views as silvaviews
from silva.core.interfaces import IAsset

from silva.core.views.interfaces import IPreviewLayer

class SilvaSoftwarePackage(Publication):
    """Silva Software Package"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Package'
    implements(ISilvaSoftwarePackage)

    silvaconf.icon('software_package.png')
    silvaconf.priority(9)

    def get_silva_addables_allowed_in_publication(self):

        allowed = super(SilvaSoftwarePackage, self).\
                  get_silva_addables_allowed_in_publication()
        addables = extensionRegistry.get_addables()
        result = ['Silva Document', 'Silva Software Release']

        for addable in addables:
            if (addable['name'] in allowed and
                IAsset.implementedBy(addable['instance'])):
                result.append(addable['name'])
        return result


InitializeClass(SilvaSoftwarePackage)


@silvaconf.subscribe(ISilvaSoftwarePackage, IObjectAddedEvent)
def addDefaultDocument(package, event):
    if event.oldParent is None:
        package.manage_addProduct['SilvaDocument'].manage_addDocument(
            'index', package.get_title())
        index = getattr(package, 'index')
        index.set_unapproved_version_publication_datetime(DateTime.DateTime())
        index.approve_version()



class PackageAdd(z3cforms.AddForm):

    silvaconf.context(ISilvaSoftwarePackage)
    silvaconf.name('Silva Software Package')


class PackageView(silvaviews.View):

    silvaconf.context(ISilvaSoftwarePackage)

    def get_releases(self):

        publishables = self.content.get_ordered_publishables()
        publishables = [obj for obj in publishables
                        if ISilvaSoftwareRelease.providedBy(obj)]

        if not IPreviewLayer.providedBy(self.request):
            publishables = [obj for obj in publishables
                            if obj.get_default().get_public_version()]

        def sort_by_version(a, b):
            return -cmp(parse_version(a.id), parse_version(b.id))

        publishables.sort(sort_by_version)

        def file_detail(entry):
            return {'name': entry.get_filename(),
                    'url': entry.absolute_url()}

        for entry in publishables:
            crea_date = entry.get_default().get_creation_datetime()
            files = map(file_detail, entry.get_files())
            yield {'name': self.content.get_title() + ' ' + entry.id,
                   'url': entry.absolute_url(),
                   'date': mangle.DateTime(crea_date).toStr(),
                   'files': files}

