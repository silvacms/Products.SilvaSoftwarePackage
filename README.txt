Copyright (c) 2002-2004 Infrae. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:  SilvaSoftwarePackage 0.1
  Author:     Guido Wesdorp
  Email:      guido@infrae.com
  CVS:        $Revision: 1.1 $

  SilvaSoftwarePackage:

    This is a Silva extension product that provides a small set of objects to
    present software releases to the public. There are two main objects:
    SilvaSoftwarePackage and SilvaSoftwareRelease. SilvaSoftwarePackage is a
    container that can (only) contain SilvaSoftwareReleases, SilvaDocument
    objects and Asset objects. There's an 'index' document to provide some
    description about the software package, the public view will show this
    index together with an ordered (by version) list of SilvaSoftwareReleases
    contained in the SilvaSoftwarePackage. SilvaSoftwareRelease is also a
    container object, but instead it can only contain Document objects and
    Asset objects. There's also an index document that will be displayed on
    public view, here some changelog and such can be displayed, together with
    the File Asset objects contained in the SilvaSoftwareRelease.

  Installing:

    Installation is a matter of unpacking the tarball into Zope's Products
    directory, restarting Zope and pressing the 'Install' button in the
    SilvaSoftwarePackage box in 'service_extensions' in the Silva root.

  Questions and remarks:

    If you have any questions or remarks about this product, please send an
    email to guido@infrae.com.

We hope you enjoy the product!

  the Infrae team
