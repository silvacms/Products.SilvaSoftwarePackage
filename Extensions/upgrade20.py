# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaSoftwarePackage.SilvaSoftwareCenter import \
    SilvaSoftwareCenter
from Products.Silva.helpers import SwitchClass
import silva.core.interfaces

TYPE_CHANGED = {
    'Silva Software File': 'Silva File',
    'Silva 3rd Party Software Package': 'Silva Software Package',
    'Silva 3rd Party Extension Page': 'Silva Software Center',
    'Silva 3rd Party Software Release': 'Silva Software Release'}


def fix_meta_type(container):
    """Fix indexed meta_type in containers.
    """
    for content in container._objects:
        if content['meta_type'] in TYPE_CHANGED:
            content['meta_type'] = TYPE_CHANGED[content['meta_type']]
            container._p_changed = True
        obj = getattr(container, content['id'])
        if silva.core.interfaces.IContainer.providedBy(obj):
            fix_meta_type(obj)


def upgrade(root):
    """Upgrade a Silva Root to SilvaSoftwarePackage 2.0.
    """
    assert silva.core.interfaces.IRoot.providedBy(root)
    fix_meta_type(root)
    if hasattr(root, 'service_software'):
        root.manage_delObjects(['service_software',])


def convert_to_center(publication):
    """Convert a publication to a center.
    """
    assert not silva.core.interfaces.IRoot.providedBy(publication)
    assert silva.core.interfaces.IPublication.providedBy(publication)
    SwitchClass(SilvaSoftwareCenter).upgrade(publication)
