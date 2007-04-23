Copyright (c) 2002-2007 Infrae. All rights reserved.
See also LICENSE.txt

Meta::

  Valid for:  SilvaSoftwarePackage 0.5, SilvaSoftwarePackage 0.6
  Author:     Guido Wesdorp plus the usual suspects
  Email:      info@infrae.com

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

    Requirements:

        Silva 1.0+ and it's requirements.

    Installation:

        Installation is a matter of unpacking the tarball into Zope's Products
        directory, restarting Zope and pressing the 'Install' button in the
        SilvaSoftwarePackage box in 'service_extensions' in the Silva root.

  Using:

    First create a SilvaSoftwarePackage and edit it's default document (this
    will be the 'frontpage' of the software package, so it should contain some
    general information about the piece of software). Add a (number of)
    SilvaSoftwareRelease(s) to the package, those will contain different
    versions of the package. Edit the default documents in those, they should
    contain information more specific to the release. Add a (number of)
    SilvaSoftwareFile object(s) to the release, this/these will be the actual
    downloadable file(s). When done, publish the default documents and the
    software package is publically viewable.

    As you will notice both the SilvaSoftwarePackage and SilvaSoftwareRelease
    objects can contain other documents and asset objects (files etc.), this
    allows you to build a more complex public view: you can add licenses,
    screenshots etc.  to the package/release this way. Also this way you can
    add a new document if you, for some reason, removed the original one.  Note
    that SilvaFile and SilvaAsset objects will not be shown in the table of
    downloadable files: this will only display the SilvaSoftwareFile type
    objects in the release.

    To publish a SilvaSoftwarePackage or a SilvaSoftwareRelease you will have
    to publish the default document. If this document is not published or
    deleted, the package will not be viewable by the public.

  Questions and remarks:

    If you have any questions or remarks about this product, please send an
    email to info@infrae.com.

We hope you enjoy the product!

   The Infrae team
