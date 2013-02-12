
import io
import urllib2
import json

from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.Silva import SilvaPermissions
from Products.SilvaSoftwarePackage.SilvaSoftwareGroup import SilvaSoftwareGroup
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope import schema
from silva.core.interfaces import IPublicationWorkflow
from silva.core.conf.interfaces import ITitledContent
from silva.core.smi.settings import Settings
from silva.core.xml import Importer
from zeam.form import silva as silvaforms


class Synchronizer(object):

    def __init__(self, request):
        self.request = request

    def build(self, origin, adder, items):
        """Helper to build the containers.
        """
        request = self.request
        existing = origin.objectIds()
        # Add items, one by one.
        for item in items:
            identifier = item.get('identifier', '')
            assert len(identifier), 'Invalid json structure'
            if identifier not in existing:
                adder(str(identifier), identifier, no_default_content=True)
            content = origin._getOb(identifier)
            importer = Importer(origin, request, {'update_content': True})
            importer.importStream(io.BytesIO(item['export'].encode('utf-8')))
            # Add index document if needed.
            if 'index' in item and item['index']:
                if content.get_default() is None:
                    factory = content.manage_addProduct['silva.app.document']
                    factory.manage_addDocument(
                        'index', identifier, no_default_version=True)
                importer = Importer(content, request, {'update_content': True})
                importer.importStream(io.BytesIO(item['index'].encode('utf-8')))
            yield content, item

    def __call__(self, origin, items):
        add_package = origin.manage_addProduct['SilvaSoftwarePackage'] \
            .manage_addSilvaSoftwarePackage
        for package, package_json in self.build(
            origin, add_package, items):
            add_release = package.manage_addProduct['SilvaSoftwarePackage'] \
                .manage_addSilvaSoftwareRelease
            for release, release_json in self.build(
                package, add_release, package_json['releases']):
                add_file = release.manage_addProduct['Silva'].manage_addLink
                existing_files = release.objectIds()
                for file_json in release_json['files']:
                    if file_json['identifier'] in existing_files:
                        continue
                    add_file(
                        str(file_json['identifier']),
                        file_json['title'],
                        url=file_json['url'])
                    file_link = release._getOb(file_json['identifier'])
                    IPublicationWorkflow(file_link).publish()


class SilvaSoftwareRemoteGroup(SilvaSoftwareGroup):
    meta_type = 'Silva Software Remote Group'
    grok.implements(interfaces.ISilvaSoftwareRemoteGroup)

    security = ClassSecurityInfo()
    group_url = u''

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'synchronize')
    def synchronize(self, request):
        """Synchronize software packages with the ones contained in a
        remote group.
        """
        try:
            incoming = urllib2.urlopen(self.group_url)
        except:
            raise ValueError('Error querying the incoming server.')

        synchronizer = Synchronizer(request)
        synchronizer(self, json.loads(incoming.read()))

InitializeClass(SilvaSoftwareRemoteGroup)


class IRemoteGroupFields(ITitledContent):
    group_url = schema.URI(
        title=u'Remote group URI',
        required=True)


class GroupRemoteAdd(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwareRemoteGroup)
    grok.name('Silva Software Remote Group')

    fields = silvaforms.Fields(IRemoteGroupFields)


class GroupRemoteSettings(silvaforms.SMISubEditForm):
    grok.context(interfaces.ISilvaSoftwareRemoteGroup)
    grok.view(Settings)
    grok.order(4)

    label = u"Software remote group settings"
    actions = silvaforms.Actions(silvaforms.SMISubEditForm.actions)
    fields = silvaforms.Fields(IRemoteGroupFields).omit('id', 'title')

    @silvaforms.action('Synchronize')
    def synchronize(self):
        try:
            self.context.synchronize(self.request)
        except ValueError, error:
            raise silvaforms.ActionError(error.args[0])
        self.send_message('Software synchronized.')
        return silvaforms.SUCCESS
