
import urllib2
import json

from Products.SilvaSoftwarePackage.SilvaSoftwareGroup import SilvaSoftwareGroup
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope import schema
from silva.core.interfaces import IPublicationWorkflow
from silva.core.conf.interfaces import ITitledContent
from silva.core.smi.settings import Settings
from zeam.form import silva as silvaforms


class SilvaSoftwareRemoteGroup(SilvaSoftwareGroup):
    meta_type = 'Silva Software Remote Group'
    grok.implements(interfaces.ISilvaSoftwareRemoteGroup)

    group_url = u''

    def synchronize(self):
        try:
            incoming = urllib2.urlopen(self.group_url)
        except:
            raise ValueError('Error querying the incoming server.')

        for package_json in json.loads(incoming.read()):
            factory = self.manage_addProduct['SilvaSoftwarePackage']
            factory.manage_addSilvaSoftwarePackage(
                str(package_json['identifier']), package_json['identifier'])
            package = self._getOb(package_json['identifier'])
            for release_json in package_json['releases']:
                factory = package.manage_addProduct['SilvaSoftwarePackage']
                factory.manage_addSilvaSoftwareRelease(
                    str(release_json['identifier']), release_json['identifier'])
                release = package._getOb(release_json['identifier'])
                for file_json in release_json['files']:
                    factory = release.manage_addProduct['Silva']
                    factory.manage_addLink(
                        file_json['identifier'],
                        file_json['title'],
                        url=file_json['url'])
                    file_link = release._getOb(file_json['identifier'])
                    IPublicationWorkflow(file_link).publish()


class IRemoteGroupFields(ITitledContent):
    group_url = schema.URI(
        title=u'Remote group URI',
        required=True)


class GroupRemoteAdd(silvaforms.SMIAddForm):
    grok.context(interfaces.ISilvaSoftwareRemoteGroup)
    grok.name('Silva Software Remote Group')

    fields = silvaforms.Fields(IRemoteGroupFields)


class GroupRemoteSettings(silvaforms.SMISubEditForm):
    grok.context(interfaces.ISilvaSoftwareGroup)
    grok.view(Settings)
    grok.order(4)

    label = u"Software remote group settings"
    actions = silvaforms.Actions(silvaforms.SMISubEditForm.actions)
    fields = silvaforms.Fields(IRemoteGroupFields).omit('id', 'title')

    @silvaforms.action('Synchronize')
    def synchronize(self):
        try:
            self.context.synchronize()
        except ValueError, error:
            raise silvaforms.ActionError(error.args[0])
        self.send_message('Software synchronized.')
        return silvaforms.SUCCESS
