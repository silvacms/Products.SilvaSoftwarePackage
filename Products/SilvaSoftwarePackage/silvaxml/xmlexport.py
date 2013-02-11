
from Products.SilvaSoftwarePackage import interfaces
from Products.SilvaSoftwarePackage.silvaxml import NS_PACKAGE_URI
from five import grok
from silva.core.xml import producers
from zope.interface import Interface


class CenterProducer(producers.SilvaContainerProducer):
    grok.adapts(interfaces.ISilvaSoftwareCenter, Interface)

    def sax(self):
        self.startElementNS(NS_PACKAGE_URI, 'center', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_PACKAGE_URI, 'center')


class GroupProducer(producers.SilvaContainerProducer):
    grok.adapts(interfaces.ISilvaSoftwareGroup, Interface)

    def sax(self):
        self.startElementNS(NS_PACKAGE_URI, 'group', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_PACKAGE_URI, 'group')


class RemoteGroupProducer(producers.SilvaContainerProducer):
    grok.adapts(interfaces.ISilvaSoftwareRemoteGroup, Interface)

    def sax(self):
        options = {
            'id': self.context.id,
            'url': self.context.group_url}
        self.startElementNS(NS_PACKAGE_URI, 'remote_group', options)
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_PACKAGE_URI, 'remote_group')


class PackageProducer(producers.SilvaContainerProducer):
    grok.adapts(interfaces.ISilvaSoftwarePackage, Interface)

    def sax(self):
        options = {
            'id': self.context.id,
            'deprecated': self.context.is_package_deprecated and 'yes' or 'no'}
        self.startElementNS(NS_PACKAGE_URI, 'package', options)
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_PACKAGE_URI, 'package')


class ReleaseProducer(producers.SilvaContainerProducer):
    grok.adapts(interfaces.ISilvaSoftwareRelease, Interface)

    def sax(self):
        self.startElementNS(NS_PACKAGE_URI, 'release', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_PACKAGE_URI, 'release')

