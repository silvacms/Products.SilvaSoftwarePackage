
from Products.SilvaSoftwarePackage.SilvaSoftwareGroup import SilvaSoftwareGroup
from Products.SilvaSoftwarePackage import interfaces

from five import grok
from zope import schema
from silva.core.conf.interfaces import ITitledContent
from silva.core.smi.settings import Settings
from zeam.form import silva as silvaforms


class SilvaSoftwareRemoteGroup(SilvaSoftwareGroup):
    meta_type = 'Silva Software Remote Group'
    grok.implements(interfaces.ISilvaSoftwareRemoteGroup)

    group_url = u''



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
        self.send_message('Software synchronized.')
        return silvaforms.SUCCESS
