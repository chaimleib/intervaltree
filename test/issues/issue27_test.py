"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, insertion and removal of float intervals
Submitted as issue #26 (Pop from empty list error) by sciencectn
Ensure that rotations that promote Intervals prune when necessary

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
from intervaltree import IntervalTree, Interval
import pytest


def original_print():
    it = IntervalTree()
    it.addi(1, 3, "dude")
    it.addi(2, 4, "sweet")
    it.addi(6, 9, "rad")
    for iobj in it:
        print(it[iobj.begin, iobj.end])  # set(), should be using :

    for iobj in it:
        print(it.envelop(iobj.begin, iobj.end))

    # set([Interval(6, 9, 'rad')])
    # set([Interval(1, 3, 'dude'), Interval(2, 4, 'sweet')])
    # set([Interval(1, 3, 'dude'), Interval(2, 4, 'sweet')])


def test_brackets_vs_overlap():
    it = IntervalTree()
    it.addi(1, 3, "dude")
    it.addi(2, 4, "sweet")
    it.addi(6, 9, "rad")
    for iobj in it:
        assert it[iobj.begin:iobj.end] == it.overlap(iobj.begin, iobj.end)

    # set([Interval(6, 9, 'rad')])
    # set([Interval(1, 3, 'dude'), Interval(2, 4, 'sweet')])
    # set([Interval(1, 3, 'dude'), Interval(2, 4, 'sweet')])


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

