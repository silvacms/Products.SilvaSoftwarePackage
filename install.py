# Copyright (c) 2004 Guido Wesdorp. All rights reserved.
# See also LICENSE.txt
# $Id: install.py,v 1.1 2004/06/29 16:41:01 guido Exp $
"""Install for Silva Blog
"""

from Products.Silva.install import add_fss_directory_view
from Products.SilvaSoftwarePackage import SilvaSoftwarePackage
from Products.SilvaSoftwarePackage import SilvaSoftwareRelease

def install(root):
    # create the core views from filesystem
    add_fss_directory_view(root.service_views,
                           'SilvaSoftwarePackage', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)

    # security
    root.manage_permission('Add Silva Software Packages',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])
    root.manage_permission('Add Silva Software Releases',
                           ['Author', 'Editor', 'ChiefEditor', 'Manager'])

    configureAddables(root)
    configureMetadata(root)

def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['SilvaSoftwarePackage'])
    
def is_installed(root):
    return hasattr(root.service_views, 'SilvaSoftwarePackage')

def registerViews(reg):
    """Register core views on registry.
    """
    # edit
    reg.register('edit', 'Silva Software Package', 
                    ['edit', 'Container', 'SilvaSoftwarePackage'])
    reg.register('edit', 'Silva Software Release', 
                    ['edit', 'Container', 'SilvaSoftwareRelease'])
    # public
    reg.register('public', 'Silva Software Package', 
                    ['public', 'SilvaSoftwarePackage'])
    reg.register('public', 'Silva Software Release', 
                    ['public', 'SilvaSoftwareRelease'])
    # add
    reg.register('add', 'Silva Software Package', 
                    ['add', 'SilvaSoftwarePackage'])
    reg.register('add', 'Silva Software Release', 
                    ['add', 'SilvaSoftwareRelease'])
    
def unregisterViews(reg):
    for meta_type in ['Silva Software Package', 
                        'Silva Software Release']:
        reg.unregister('edit', meta_type)
        reg.unregister('public', meta_type)
        reg.unregister('add', meta_type)

def configureAddables(root):
    """Make sure the articles aren't addable in the root"""
    current_addables = root.get_silva_addables_allowed_in_publication()
    new_addables = []
    for a in current_addables:
        if a != 'Silva Software Release':
            new_addables.append(a)
    if 'Silva Software Package' not in new_addables:
        new_addables.append('Silva Software Package')
    root.set_silva_addables_allowed_in_publication(new_addables)

def configureMetadata(root):
    from os import path
    from Globals import package_home
    
    # load up the default metadata
    ssp_home = package_home(globals())
    ssp_docs = path.join(ssp_home, 'doc')

    collection = root.service_metadata.getCollection()
    if 'silva-software' in collection.objectIds():
        collection.manage_delObjects(['silva-software'])

    xml_file = path.join(ssp_docs, 'silva-software.xml')
    fh = open(xml_file, 'r')        
    collection.importSet(fh)

    # (re) set the default type mapping
    mapping = root.service_metadata.getTypeMapping()
    default = ''
    tm = (
        {'type':'Silva Software Release',   'chain':'silva-content, silva-extra, silva-software'},
        {'type':'Silva Software Package',           'chain':'silva-content, silva-extra'},
        )
    mapping.editMappings(default, tm)

    # initialize the default set if not already initialized
    for set in collection.getMetadataSets():
        if not set.isInitialized():
            set.initialize()

