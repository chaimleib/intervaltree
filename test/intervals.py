"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: utilities to generate intervals

Copyright 2013-2014 Chaim-Leib Halbert

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
from intervaltree import Interval
from pprint import pprint
from os import listdir
from os.path import join
from random import randint, choice

# import data to construct our intervals
def from_import(module, member):
    print('from {0} import {1}'.format(module, member))
    module = __import__(module, fromlist=[member])
    return getattr(module, member)

def ivs_names():
    """
    Get the names of the modules containing our interval data.
    """
    data_dir = join(from_import('test', 'data').__path__)[0]
    modules = [
        module[:-len('.py')] for module in listdir(data_dir)
        if
        module.startswith(('ivs')) and module.endswith('.py')
    ]
    return modules

ivs_data = {}
pprint(ivs_names())
for module in ivs_names():
    ivs_data[module] = from_import('test.data.' + module, 'data')


def make_iv(begin, end, label=False):
    if label:
        return Interval(begin, end, "[{0},{1})".format(begin, end))
    else:
        return Interval(begin, end)


def ivs1():
    """Sample list of intervals for tests."""
    ivs = [make_iv(*iv, label=True) for iv in [
        [1, 2],
        [4, 7],
        [5, 9],
        [6, 10],
        [8, 10],
        [8, 15],
        [10, 12],
        [12, 14],
        [14, 15],
    ]]
    return ivs

def nogaps_rand(size=100, labels=False):
    """
    Create a random list of Intervals with no gaps or overlaps
    between the intervals.
    """
    cur = -50
    ivs = []
    for i in xrange(size):
        length = randint(1, 10)
        ivs.append(make_iv(cur, cur + length, labels))
        cur += length
    return ivs


def gaps_rand(size=100, labels=False):
    """
    Create a random list of intervals  with random gaps, but no
    overlaps between the intervals.
    """
    cur = -50
    ivs = []
    for i in xrange(size):
        length = randint(1, 10)
        if choice([True, False]):
            cur += length
            length = randint(1, 10)
        ivs.append(make_iv(cur, cur + length, labels))
        cur += length
    return ivs


def write_ivs_data(name, ivs, imports=None):
    data = [tuple(iv) for iv in ivs]
    with open('test/data/{0}.py'.format(name), 'w') as f:
        if isinstance(imports, basestring):
            f.write(imports)
            f.write('\n\n')
        elif isinstance(imports, (list, tuple, set)):
            for line in imports:
                f.write(line + '\n')
            f.write('\n')

        f.write('data = \\\n')
        pprint(data, f)


if __name__ == '__main__':
    #write_ivs_data('ivs1', ivs1())
    pprint(ivs_data)
