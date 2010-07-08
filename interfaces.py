# Copyright (c) 2009-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import interfaces


class ISilvaSoftwareContent(interfaces.IFolder):
    """This is a content from the Silva Software center.
    """


class ISilvaSoftwareGroup(ISilvaSoftwareContent):
    """A group of packages.
    """


class ISilvaSoftwareCenter(ISilvaSoftwareGroup, interfaces.IPublication):
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

