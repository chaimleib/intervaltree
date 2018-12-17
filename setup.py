"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Distribution logic

Note that "python setup.py test" invokes pytest on the package. With appropriately
configured setup.cfg, this will check both xxx_test modules and docstrings.

Copyright 2013-2018 Chaim Leib Halbert

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import
from sys import exit
from setuptools import setup
from setuptools.command.test import test as TestCommand

from utils import version

## CONFIG
target_version = '3.0.0'

version_info = version.version_info(target_version)
if version_info['is_dev_version']:
    print("This is a DEV version")
    print("Target: {target_version}\n".format(**version_info))
else:
    print("!!!>>> This is a RELEASE version <<<!!!\n")
    print("Version: {version}".format(**version_info))

with open('README.md', 'r') as fh:
    long_description = fh.read()

## PyTest
# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest  # import here, because outside the required eggs aren't loaded yet
        exit(pytest.main(self.test_args))


## Run setuptools
setup(
    name='intervaltree',
    version=version_info['version'],
    install_requires=['sortedcontainers >= 2.0, < 3.0'],
    description='Editable interval tree data structure for Python 2 and 3',
    long_description=long_description,
    classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Markup',
    ],
    keywords='interval-tree data-structure intervals tree',  # Separate with spaces
    author='Chaim Leib Halbert, Konstantin Tretyakov',
    author_email='chaim.leib.halbert@gmail.com',
    url='https://github.com/chaimleib/intervaltree',
    download_url='https://github.com/chaimleib/intervaltree/tarball/{version}'.format(**version_info),
    license="Apache License, Version 2.0",
    packages=["intervaltree"],
    include_package_data=True,
    zip_safe=True,
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
