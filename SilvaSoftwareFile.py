# Zope
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from webdav.WriteLockInterface import WriteLockInterface
# Silva
from Products.Silva import mangle
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva import SilvaPermissions
from Products.Silva.File import ZODBFile, FileSystemFile
from Products.Silva.interfaces import IFile, IAsset
from Products.Silva.helpers import add_and_edit

class SilvaSoftwareFile(SilvaObject):
    security = ClassSecurityInfo()
    meta_type = 'Silva Software File'
    __implements__ = (WriteLockInterface, IFile)

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
        self.service_software.log_software_download(self.getPhysicalPath())
        self.REQUEST.RESPONSE.setHeader('Location', self.absolute_url())
        return ''

InitializeClass(SilvaSoftwareFile)

class ZODBSoftwareFile(ZODBFile, SilvaSoftwareFile):
    """File object that has some extra features"""

    index_html = SilvaSoftwareFile.index_html
    
InitializeClass(ZODBSoftwareFile)

class FileSystemSoftwareFile(FileSystemFile, SilvaSoftwareFile):
    """File object that has some extra features"""

    index_html = SilvaSoftwareFile.index_html

InitializeClass(FileSystemSoftwareFile)

manage_addSilvaSoftwareFileForm = PageTemplateFile(
    "www/softwareFileAdd", globals(), __name__='manage_addSilvaSoftwareFileForm')

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
        object = FileSystemSoftwareFile(id, title, file, 
            service_files.filesystem_path())
    else:
        object = ZODBSoftwareFile(id, title, file)
    self._setObject(id, object)
    object = getattr(self, id)
    object.set_title(title)
    return object
