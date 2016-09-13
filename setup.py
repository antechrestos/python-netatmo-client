import os
import shutil
import sys

from setuptools import setup, find_packages

src_dir = 'main'
package_directory = 'netatmo_client'
package_name = 'netatmo-client'
sys.path.insert(0, os.path.realpath(src_dir))

version_file = '%s/%s/__init__.py' % (src_dir, package_directory)
with open(version_file, 'r') as f:
    for line in f.readlines():
        if line.find('__version__') >= 0:
            exec line
            break
    else:
        raise AssertionError('Failed to load version from %s' % version_file)


def purge_sub_dir(path):
    shutil.rmtree(os.path.join(os.path.dirname(__file__), path))


setup(name=package_name,
      version=__version__,
      zip_safe=True,
      packages=find_packages(where=src_dir),
      author='Benjamin Einaudi',
      author_email='antechrestos@gmail.com',
      description='A client library for Netatmo',
      long_description=open('README.rst').read(),
      url='http://github.com/antechrestos/python-netatmo-client',
      classifiers=[
          "Programming Language :: Python",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Communications",
      ],
      package_dir={package_directory: '%s/%s' % (src_dir, package_directory)},
      install_requires=[requirement.rstrip(' \r\n') for requirement in open('requirements.txt')],
      tests_require=[
          'mock==2.0.0',
      ],
      test_suite='test',
      )
