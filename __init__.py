# Copyright (c) 2004 Guido Wesdorp. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py,v 1.1 2004/06/29 16:41:01 guido Exp $

from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.ImporterRegistry import importer_registry
import install

from Products.Silva.fssite import registerDirectory
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata

import SilvaSoftwarePackage
import SilvaSoftwareRelease

from Products.Formulator.FieldRegistry import FieldRegistry
from VersionField import VersionField

def initialize(context):
    extensionRegistry.register(
        'SilvaSoftwarePackage', 'Silva Software Package', context, 
        [SilvaSoftwareRelease, SilvaSoftwarePackage], install, 
        depends_on='SilvaDocument')
        
    registerDirectory('views', globals())
    FieldRegistry.registerField(VersionField,
                                'www/StringField.gif')
    
    FieldRegistry.initializeFields()
