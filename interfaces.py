from zope.interface import Interface
from Products.Silva.interfaces import IAsset

class ISilvaSoftwarePackage(Interface):
    """A Silva Software Package is a collection of SilvaSoftwareReleases"""

    def get_releases(published=1):
        """Returns a list of available releases

            if published is true, it will only return published releases
        """

    def get_software_file_paths():
        """Returns a list of all contained SilvaSoftwareFile objects"""

class ISilvaSoftwareRelease(Interface):
    """A set of SilvaSoftwareFile objects and some documentation"""

    def get_files():
        """Returns a list of contained SilvaSoftwareFile objects"""

class ISilvaSoftwareFile(IAsset):
    """A Silva Software File is a mixin for File objects

        It makes the file object send a notification to a service
        somewhere so that can keep track of a logfile (and show some
        statistics etc.)
    """

    def index_html(view_path):
        """download the file

            will do logging before the file is forwarded
        """
