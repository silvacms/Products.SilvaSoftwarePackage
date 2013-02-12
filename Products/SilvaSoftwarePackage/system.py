
import logging
import transaction

from silva.core.services.interfaces import ICatalogService
from silva.system.utils.script import NEED_SILVA_SESSION
from zope.component import getUtility
from zope.publisher.browser import TestRequest

logger = logging.getLogger('Products.SilvaSoftwarePackage')


class UpdateRemoteGroupCommand(object):
    flags = NEED_SILVA_SESSION

    def get_options(self, factory):
        parser = factory(
            'software_update',
            help="manage silva software")
        parser.add_argument(
            "-u", "--username",
            help="username to login in order to convert files")
        parser.add_argument(
            "paths", nargs="+",
            help="path to Silva sites to work on")
        parser.set_defaults(plugin=self)

    def run(self, root, options):
        catalog = getUtility(ICatalogService)
        for brain in catalog(meta_type=['Silva Software Remote Group']):
            group = brain.getObject()
            try:
                group.synchronize(TestRequest())
            except ValueError:
                logger.error(
                    'Failed to synchronise group at %s.', brain.getPath())
            else:
                logger.info(
                    'Group %s synchronized.', brain.getPath())
        transaction.commit()

