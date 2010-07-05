# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.upgrade.upgrade import BaseUpgrader

VERSION_A1='2.3a1'


class RootUpgrader(BaseUpgrader):

    def upgrade(self, root):
        reg = root.service_view_registry
        reg.unregister('add', 'Silva 3rd Party Extension Page')
        reg.unregister('add', 'Silva 3rd Party Software Package')
        reg.unregister('add', 'Silva 3rd Party Software Release')
        reg.unregister('add', 'Silva Software File')
        reg.unregister('add', 'Silva Software Package')
        reg.unregister('edit', 'Silva 3rd Party Extension Page')
        reg.unregister('edit', 'Silva 3rd Party Software Package')
        reg.unregister('edit', 'Silva 3rd Party Software Release')
        reg.unregister('edit', 'Silva Software File')
        reg.unregister('public', 'Silva 3rd Party Extension Page')
        reg.unregister('public', 'Silva 3rd Party Software Package')
        reg.unregister('public', 'Silva 3rd Party Software Release')
        reg.unregister('public', 'Silva Software File')
        reg.unregister('public', 'Silva Software Package')
        reg.unregister('public', 'Silva Software Release')
        return root

root_upgrader = RootUpgrader(VERSION_A1, 'Silva Root')

