"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: test utilities

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
from intervaltree import Interval, IntervalTree
from pprint import pprint
from random import randint, choice
try:
    xrange
except NameError:
    xrange = range

def make_iv(begin, end, label=False):
    if label:
        return Interval(begin, end, "[{0},{1})".format(begin, end))
    else:
        return Interval(begin, end)

def nogaps_rand(size=100, labels=False):
    cur = -50
    ivs = []
    for i in xrange(size):
        length = randint(1, 10)
        ivs.append(make_iv(cur, cur+length, labels))
        cur += length
    return IntervalTree(ivs)

def gaps_rand(size=100, labels=False):
    cur = -50
    ivs = []
    for i in xrange(size):
        length = randint(1, 10)
        if choice([True, False]):
            cur += length
            length = randint(1, 10)
        ivs.append(make_iv(cur, cur+length, labels))
        cur += length
    return IntervalTree(ivs)


if __name__ == "__main__":
    pprint(gaps_rand(labels=False))