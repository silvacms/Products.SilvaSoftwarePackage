from setuptools import setup, find_packages
import os
import os.path

version = '2.0dev'

def read(filename, prefix=os.path.join("Products","SilvaSoftwarePackage")):
    f = open(os.path.join(prefix, filename), 'r')
    try:
        return f.read()
    finally:
        f.close()


setup(name='Products.SilvaSoftwarePackage',
      version=version,
      description="SilvaSoftwarePackage provides a small set of objects to present software releases to the public",
      long_description=read("README.txt"),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Communications :: File Sharing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Packaging",
        ],
      keywords='silva software package release eggshop',
      author='Guido Wesdorp plus the usual suspects',
      author_email='info@infrae.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'Products.Silva',
          'Products.SilvaDocument',
          'silva.core.conf',
          ],
      entry_points = """
      [zodbupdate]
      renames = Products.SilvaSoftwarePackage:CLASS_CHANGES
      """
      )
