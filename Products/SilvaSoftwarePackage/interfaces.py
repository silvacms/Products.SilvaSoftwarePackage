# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.interfaces import IPublication, IFolder
from silva.core.layout.interfaces import ICustomizableTag


class ISilvaNoAutomaticUpdate(ICustomizableTag):
    """Don't automatically update the description
    """


class ISilvaSoftwareContent(IFolder):
    """This is a content from the Silva Software center.
    """


class ISilvaSoftwareGroup(ISilvaSoftwareContent):
    """A group of packages.
    """

class ISilvaSoftwareRemoteGroup(ISilvaSoftwareGroup):
    """A group of packages that is defined on a different server.
    """


class ISilvaSoftwareCenter(ISilvaSoftwareGroup, IPublication):
    """A Silva software center.
    """


class ISilvaSoftwarePackage(ISilvaSoftwareContent):
    """A Silva Software Package is a collection of
    SilvaSoftwareReleases.
    """

    def get_releases(published=1):
        """Returns a list of available releases.

           If published is true, it will only return published
           releases.
        """

    def get_software_file_paths():
        """Returns a list of all contained SilvaSoftwareFile objects.
        """


class ISilvaSoftwareRelease(ISilvaSoftwareContent):
    """A set of SilvaSoftwareFile objects and some documentation.
    """

    def get_files():
        """Returns a list of contained File.
        """

