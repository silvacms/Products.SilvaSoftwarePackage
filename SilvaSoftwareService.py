# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit
from DateTime import DateTime
from Products.Silva import SilvaPermissions

import fcntl
import re

class Permissions:
    view_software_data = 'View Silva software data'
    edit_software_services = 'Edit Silva Software Services'

class StatsEntry:
    """Simple struct-like object to store one item in the log"""
    path = None
    url = None
    date = None
    client = None
    host = None
    user = None

class SilvaSoftwareService(SimpleItem):
    """A service that provides some logging functionality
        and some views on the log
    """

    security = ClassSecurityInfo()
    meta_type = 'Silva Software Service'

    manage_options = (
                      {'label': 'Edit', 'action': 'edit_tab'},
                      {'label': 'View log', 'action': 'view_tab'},
                      {'label': 'View stats', 'action': 'stats_tab'},
                      ) + SimpleItem.manage_options

    manage_main = edit_tab = PageTemplateFile('www/softwareServiceEditTab',
                                              globals(), __name__='edit_tab')

    view_tab = PageTemplateFile('www/softwareServiceViewTab',
                                              globals(), __name__='view_tab')

    stats_tab = PageTemplateFile('www/softwareServiceStatsTab',
                                              globals(), __name__='stats_tab')

    def __init__(self, id, title, logfile_path):
        self.id = id
        self.title = title
        self.logfile_path = logfile_path
        self._seek = 0
        self._stats_by_path = {}

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
    def log_software_download(self, obj):
        """log a software download
        
            path is the physical path to the file
        """
        request = self.REQUEST
        path = '/'.join(obj.getPhysicalPath())
        url = obj.absolute_url()
        time = DateTime().rfc822()
        clientaddr = request['REMOTE_ADDR']
        clienthost = request['REMOTE_HOST']
        user = request['AUTHENTICATED_USER'].getUserName()
        logline = '%s - %s (%s) - %s - %s (%s)\n' % (
                        time, clientaddr, clienthost, user, path, url
                    )
        try:
            fp = open(self.logfile_path, 'a')
        except IOError:
            fp = open(self.logfile_path, 'w')
        fileno = fp.fileno()
        fcntl.flock(fileno, fcntl.LOCK_EX)
        try:
            fp.write(logline)
        finally:
            fcntl.flock(fileno, fcntl.LOCK_UN)

    security.declareProtected(Permissions.edit_software_services,
                                'view_log')
    def view_log(self, REQUEST):
        """returns the full log data
        
            Don't use this from a Python script, since then it will read the
            whole log into memory. Always call it TTW so it can stream.
        """
        if REQUEST is not None:
            fp = open(self.logfile_path)
            blocksize = 2<<16
            while 1:
                block = fp.read(blocksize)
                REQUEST.RESPONSE.write(block)
                if len(block) < blocksize:
                    break
            fp.close()
            return ''
        else:
            return open(self.logfile_path).read()

    security.declareProtected(Permissions.edit_software_services,
                                'manage_edit')
    def manage_edit(self, title, logfile_path):
        """update from the edit tab"""
        self.title = title
        self.logfile_path = logfile_path
        return self.edit_tab(manage_tabs_message='Data updated')

    reg_line = re.compile(r'^([^-]+) - ([0-9\.]+) \(([^\)]*)\) - ([^-]*) - ([^\ ]+) \((.*)\)$')
    security.declareProtected(Permissions.edit_software_services,
                                'parse_logfile')
    def parse_logfile(self, restart=0):
        """parse a logfile

            THIS SHOULD BE USED WITH CARE!!!
        """
        if restart:
            self._seek = 0
            self._stats_by_path = {}
        fp = open(self.logfile_path)
        fp.seek(self._seek)
        while 1:
            line = fp.readline()
            if not line:
                break
            self._seek += len(line)
            match = self.reg_line.match(line)
            if not match:
                raise ValueError, line
            time, ip, address, user, path, abspath = match.groups()

            # store all the new values in a record, create key where
            # needed
            record = self._stats_by_path.get(path, {})
            if not record.has_key('times'):
                record['times'] = []
            record['times'].append(time)
            record['total'] = record.get('total', 0) + 1
            ips = record.get('ips', {})
            ips[ip] = ips.get(ip, 0) + 1
            record['ips'] = ips
            abspaths = record.get('abspaths', {})
            abspaths[abspath] = abspaths.get(abspath, 0) + 1
            record['abspaths'] = abspaths
            
            # now replace the current record with the new one or add it
            self._stats_by_path[path] = record

        self._p_changed = 1

        return self.stats_tab()

    security.declareProtected(Permissions.edit_software_services,
                                'get_paths')
    def get_paths(self):
        """returns all the paths for which stats are available"""
        return self._stats_by_path.keys()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'stats_by_path')
    def stats_by_path(self, path):
        """Return the stats of a single file"""
        return self._stats_by_path.get(path, {})

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
