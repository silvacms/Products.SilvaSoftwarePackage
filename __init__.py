# Copyright (c) 2004 Guido Wesdorp. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py,v 1.2 2004/07/02 15:35:27 guido Exp $

from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.ImporterRegistry import importer_registry
import install

from Products.Silva.fssite import registerDirectory
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata

import SilvaSoftwarePackage
import SilvaSoftwareRelease
import SilvaSoftwareService
import SilvaSoftwareFile

from Products.Formulator.FieldRegistry import FieldRegistry
from VersionField import VersionField

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
    FieldRegistry.registerField(VersionField,
                                'www/StringField.gif')
    
    FieldRegistry.initializeFields()
