# Copyright (c) 2004-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva import interfaces

class ISilvaSoftwarePackage(interfaces.IPublication):
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

class ISilvaSoftwareRelease(interfaces.IPublication):
    """A set of SilvaSoftwareFile objects and some documentation.
    """

    def get_files():
        """Returns a list of contained File.
        """

class ISilvaSoftwareCenter(interfaces.IPublication):
    """A Silva software center.
    """

    
