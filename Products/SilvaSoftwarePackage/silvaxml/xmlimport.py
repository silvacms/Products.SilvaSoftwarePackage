
from five import grok
from Products.SilvaSoftwarePackage.silvaxml import NS_PACKAGE_URI
from silva.core import conf as silvaconf
from silva.core.xml import handlers


silvaconf.namespace(NS_PACKAGE_URI)


class CenterHandler(handlers.SilvaHandler):
    grok.name('center')

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['SilvaSoftwarePackage']
        factory.manage_addSilvaSoftwareCenter(
            identifier, '', no_default_content=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PACKAGE_URI, 'center'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_PACKAGE_URI, 'center'):
            self.storeMetadata()
            self.notifyImport()


class GroupHandler(handlers.SilvaHandler):
    grok.name('group')

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['SilvaSoftwarePackage']
        factory.manage_addSilvaSoftwareGroup(
            identifier, '', no_default_content=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PACKAGE_URI, 'group'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_PACKAGE_URI, 'group'):
            self.storeMetadata()
            self.notifyImport()


class PackageHandler(handlers.SilvaHandler):
    grok.name('package')

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['SilvaSoftwarePackage']
        factory.manage_addSilvaSoftwarePackage(
            identifier, '', no_default_content=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PACKAGE_URI, 'package'):
            package = self.createContent(attrs)
            package.is_package_deprecated = attrs.get(
                (NS_PACKAGE_URI, 'deprecated'), 'no') == 'yes'

    def endElementNS(self, name, qname):
        if name == (NS_PACKAGE_URI, 'package'):
            self.storeMetadata()
            self.notifyImport()


class ReleaseHandler(handlers.SilvaHandler):
    grok.name('release')

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['SilvaSoftwarePackage']
        factory.manage_addSilvaSoftwareRelease(
            identifier, '', no_default_content=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PACKAGE_URI, 'release'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_PACKAGE_URI, 'release'):
            self.storeMetadata()
            self.notifyImport()
