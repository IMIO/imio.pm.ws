from setuptools import setup, find_packages
import os

version = '3.9'

setup(name='imio.pm.ws',
      version=version,
      description="WebServices for PloneMeeting",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("CHANGES.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 6 - Mature",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
        ],
      keywords='',
      author='Gauthier Bastien',
      author_email='gauthier@imio.be',
      url='http://svn.communesplone.org/svn/communesplone/imio.pm.ws/',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['imio', 'imio.pm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'lxml',
          'z3c.soap',
          'BeautifulSoup',
          'python-magic',
          'ZSI',
          'archetypes.schemaextender',
          'Products.PloneMeeting'
          # -*- optional SOAP clients for tests (see docs/README.txt) -*-
          #'SOAPpy',
          #'suds',
      ],
      dependency_links = ['http://sourceforge.net/projects/pywebsvcs/files/ZSI/ZSI-2.0/ZSI-2.0.tar.gz/download'],
      extras_require={'test': ['Products.PloneMeeting [test]']},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
