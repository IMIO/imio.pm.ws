from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='communesplone.ws4plonemeeting',
      version=version,
      description="WebService for PloneMeeting",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.communesplone.org/svn/communesplone.ws4plonemeeting/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['communesplone', 'communesplone.ws4plonemeeting'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'lxml',
          'z3c.soap',
          'ZSI',
          'archetypes.schemaextender',
          'BeautifulSoup',
          'ctypes',
          'python-magic'
          # -*- optional SOAP clients for tests (see docs/README.txt) -*-
          #'SOAPpy',
          #'suds',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
