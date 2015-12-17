"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: utilities to load test data

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
from os import listdir
from os.path import join

def from_import(module, member):
    """
    Like `from module import number`, but returns the imported member.
    """
    # print('from {0} import {1}'.format(module, member))
    module = __import__(module, fromlist=[member])
    return getattr(module, member)


def ivs_names():
    """
    Get the names of the modules containing our interval data.
    """
    data_dir = join(*from_import('test', 'data').__path__)[0]
    modules = [
        module[:-len('.py')] for module in listdir(data_dir)
        if not module.startswith('__') and module.endswith('.py')
    ]
    return modules
