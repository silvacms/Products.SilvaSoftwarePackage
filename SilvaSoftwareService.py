# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit

import fcntl
from DateTime import DateTime

class Permissions:
    view_software_data = 'View Silva software data'
    edit_software_services = 'Edit Silva Software Services'

class SilvaSoftwareService(SimpleItem):
    """A service that provides some logging functionality
        and some views on the log
    """

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Service'

    manage_options = (
                      {'label': 'Edit', 'action': 'edit_tab'},
                      ) + SimpleItem.manage_options

    manage_main = edit_tab = PageTemplateFile('www/softwareServiceEditTab',
                                              globals(), __name__='edit_tab')

    def __init__(self, id, title, logfile_path):
        self.id = id
        self.title = title
        self.logfile_path = logfile_path

    security.declareProtected(Permissions.edit_software_services,
                                'get_logfile_path')
    def get_logfile_path(self):
        """returns the path to the logfile"""
        return self.logfile_path

    security.declareProtected(Permissions.edit_software_services,
                                'set_logfile_path')
    def set_logfile_path(self, logfile_path):
        """sets the path to the logfile"""
        self.logfile_path = logfile_path

    security.declareProtected(Permissions.edit_software_services,
                                'log_software_download')
    def log_software_download(self, path):
        """log a software download
        
            path is the physical path to the file
        """
        request = self.REQUEST
        if type(path) == type(()):
            path = '/'.join(path)
        time = DateTime().rfc822()
        client = request['REMOTE_ADDR']
        if request.has_key('REMOTE_HOST'):
            client = request['REMOTE_HOST']
        user = request['AUTHENTICATED_USER'].getUserName()
        logline = '%s - %s (%s) %s\n' % (time, client, user, path)
        print 'going to write to software log:', logline
        try:
            fp = open(self.logfile_path, 'a')
        except IOError:
            fp = open(self.logfile_path, 'w')
        fcntl.flock(fp, fcntl.LOCK_EX)
        try:
            fp.write(logline)
        finally:
            fcntl.flock(fp, fcntl.LOCK_UN)

    security.declareProtected(Permissions.edit_software_services,
                                'manage_edit')
    def manage_edit(self, title, logfile_path):
        """update from the edit tab"""
        self.title = title
        self.logfile_path = logfile_path
        return self.edit_tab(manage_tabs_message='Data updated')

InitializeClass(SilvaSoftwareService)

manage_addSilvaSoftwareServiceForm = PageTemplateFile(
        'www/softwareServiceAdd', globals(),
        __name__ = 'manage_addSilvaSoftwareServiceForm')

def manage_addSilvaSoftwareService(self, id, title, logfile_path, REQUEST=None):
    """Add service to folder
    """
    # add actual object
    id = self._setObject(id, SilvaSoftwareService(id, title, logfile_path))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''
