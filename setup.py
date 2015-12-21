"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Distribution logic

Note that "python setup.py test" invokes pytest on the package. With appropriately
configured setup.cfg, this will check both xxx_test modules and docstrings.

Copyright 2013-2015 Chaim-Leib Halbert

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
import os
import sys
import subprocess
from setuptools import setup
from setuptools.command.test import test as TestCommand

from utils import fs
from utils import doc

## CONFIG
target_version = '2.1.1'
create_rst = True


def development_version_number():
    p = subprocess.Popen('git describe'.split(), stdout=subprocess.PIPE)
    git_describe = p.communicate()[0].strip()
    release, build, commitish = git_describe.split('-')
    result = "{0}b{1}".format(release, build)
    return result

is_dev_version = 'PYPI' in os.environ and os.environ['PYPI'] == 'pypitest'
if is_dev_version:
    version = development_version_number()
else:  # This is a RELEASE version
    version = target_version

print("Version: " + version)
if is_dev_version:
    print("This is a DEV version")
    print("Target: %s\n" % target_version)
else:
    print("!!!>>> This is a RELEASE version <<<!!!\n")


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
        sys.exit(pytest.main(self.test_args))


## Run setuptools
setup(
    name='intervaltree',
    version=version,
    install_requires=['sortedcontainers'],
    description='Editable interval tree data structure for Python 2 and 3',
    long_description=doc.get_rst(),
    classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Text Processing :: Markup',
    ],
    keywords="interval-tree data-structure intervals tree",  # Separate with spaces
    author='Chaim-Leib Halbert, Konstantin Tretyakov',
    author_email='chaim.leib.halbert@gmail.com',
    url='https://github.com/chaimleib/intervaltree',
    download_url='https://github.com/chaimleib/intervaltree/tarball/' + version,
    license="Apache License, Version 2.0",
    packages=["intervaltree"],
    include_package_data=True,
    zip_safe=True,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points={}
)
