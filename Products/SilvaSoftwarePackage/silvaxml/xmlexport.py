
from five import grok
from zope.interface import Interface
from Products.SilvaSoftwarePackage import interfaces
from Products.SilvaSoftwarePackage.silvaxml import NS_PACKAGE_URI
from silva.core.xml import producers


class GroupProducer(producers.SilvaContainerProducer):
    grok.adapts(interfaces.ISilvaSoftwareGroup, Interface)

    def sax(self):
        self.startElementNS(NS_PACKAGE_URI, 'group', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_PACKAGE_URI, 'group')


class ReleaseProducer(producers.SilvaContainerProducer):
    grok.adapts(interfaces.ISilvaSoftwareRelease, Interface)

    def sax(self):
        self.startElementNS(NS_PACKAGE_URI, 'release', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElementNS(NS_PACKAGE_URI, 'release')

