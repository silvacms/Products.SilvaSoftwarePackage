====================
SilvaSoftwarePackage
====================

This is a Silva extension product that provides a small set of objects
to present software releases to the public. There are two main
objects: SilvaSoftwarePackage and
SilvaSoftwareRelease. SilvaSoftwarePackage is a container that can
(only) contain SilvaSoftwareReleases, SilvaDocument objects and Asset
objects. There's an 'index' document to provide some description about
the software package, the public view will show this index together
with an ordered (by version) list of SilvaSoftwareReleases contained
in the SilvaSoftwarePackage. SilvaSoftwareRelease is also a container
object, but instead it can only contain Document objects and Asset
objects. There's also an index document that will be displayed on
public view, here some changelog and such can be displayed, together
with the File Asset objects contained in the SilvaSoftwareRelease.

Code repository
===============

You can find the code of this extension in Git:
https://github.com/silvacms/Products.SilvaSoftwarePackage
