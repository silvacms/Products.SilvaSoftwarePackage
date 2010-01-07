# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.Publication import Publication
from Products.SilvaSoftwarePackage import interfaces

from silva.core import conf as silvaconf
from silva.core.views import z3cforms

from five import grok


class SilvaSoftwareGroup(Publication):
    meta_type = 'Silva Software Group'
    grok.implements(interfaces.ISilvaSoftwareGroup)

    silvaconf.icon('software_package.png')
    silvaconf.priority(8)

    def get_silva_addables_allowed_in_container(self):
        return ['Silva Software Package',]


class GroupAdd(z3cforms.AddForm):

    silvaconf.context(interfaces.ISilvaSoftwareGroup)
    silvaconf.name('Silva Software Group')


