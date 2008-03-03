# Zope
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from webdav.WriteLockInterface import WriteLockInterface
from zope.interface import implements
# Silva
from Products.Silva import mangle
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva import SilvaPermissions
from Products.Silva.File import ZODBFile, FileSystemFile
from Products.Silva.interfaces import IFile, IAsset
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.Silva.helpers import add_and_edit
from interfaces import ISilvaSoftwareFile

class SilvaSoftwareFile(SilvaObject):
    security = ClassSecurityInfo()
    meta_type = 'Silva Software File'
    implements(ISilvaSoftwareFile)

    security.declareProtected(SilvaPermissions.View, 'index_html')
    def index_html(self, *args, **kwargs):
        """view (download) the file data"""
        self._log_download()
        request = self.REQUEST
        request.RESPONSE.setHeader(
            'Content-Disposition', 'inline;filename=%s' % (self.get_filename()))
        return self._index_html_helper(request)

    def _log_download(self):
        """download the file, log with the software service"""
        self.service_software.log_software_download(self)
        self.REQUEST.RESPONSE.setHeader('Location', self.absolute_url())
        return ''

InitializeClass(SilvaSoftwareFile)

class ZODBSoftwareFile(ZODBFile, SilvaSoftwareFile):
    """File object that has some extra features"""

    implements(ISilvaSoftwareFile)
    meta_type = 'Silva Software File'

    index_html = SilvaSoftwareFile.index_html
    
InitializeClass(ZODBSoftwareFile)

class FileSystemSoftwareFile(FileSystemFile, SilvaSoftwareFile):
    """File object that has some extra features"""

    implements(ISilvaSoftwareFile)
    meta_type = 'Silva Software File'

    index_html = SilvaSoftwareFile.index_html

InitializeClass(FileSystemSoftwareFile)

def manage_addSilvaSoftwareFile(self, id, title, file):
    """Add a SilvaSoftwareFile
    """
    id = mangle.Id(self, id, file=file, interface=IAsset)
    id.cook()
    if not id.isValid():
        return 
    id = str(id)

    # Switch storage type:
    service_files = getattr(self.get_root(), 'service_files', None)
    assert service_files is not None, "There is no service_files. " \
        "Refresh your silva root."
    if service_files.useFSStorage():        
        object = FileSystemSoftwareFile(id)
    else:
        object = ZODBSoftwareFile(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    object.set_title(title)
    object._set_file_data_helper(file)
    return object
