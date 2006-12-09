# Copyright (c) 2004-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py,v 1.3 2004/10/12 15:18:54 guido Exp $

from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.ImporterRegistry import importer_registry
import install

from Products.Silva.fssite import registerDirectory
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata

import SilvaSoftwarePackage
import SilvaSoftwareRelease
import SilvaSoftwareService
import SilvaSoftwareFile

def initialize(context):
    extensionRegistry.register(
        'SilvaSoftwarePackage', 'Silva Software Package', context, 
        [SilvaSoftwareRelease, SilvaSoftwarePackage, SilvaSoftwareFile], install, 
        depends_on='SilvaDocument')
        
    context.registerClass(
        SilvaSoftwareService.SilvaSoftwareService,
        constructors = (SilvaSoftwareService.manage_addSilvaSoftwareServiceForm,
                        SilvaSoftwareService.manage_addSilvaSoftwareService),
        )

    registerDirectory('views', globals())

from AccessControl import allow_module

allow_module('Products.SilvaSoftwarePackage.SilvaSoftwareRelease')
