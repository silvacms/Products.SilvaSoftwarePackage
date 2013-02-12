
from five import grok
from Products.Silva.Folder import Folder
from Acquisition import aq_base


class SilvaSoftwareContent(Folder):
    grok.baseclass()

    def fulltext(self):
        text = super(SilvaSoftwareContent, self).fulltext()
        default = self.get_default()
        if default is not None and hasattr(aq_base(default), 'fulltext'):
            text.extend(default.fulltext())
        return text
