from setuptools import setup, find_packages
import os

version = '1.6'

setup(name='imio.pm.ws',
      version=version,
      description="WebServices for PloneMeeting",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      keywords='',
      author='',
      author_email='',
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
