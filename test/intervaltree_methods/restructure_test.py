"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Special methods

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
from intervaltree import Interval, IntervalTree
import pytest
from test.intervaltrees import trees
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_emptying_partial():
    t = trees['ivs1']()
    assert t[7:]
    t.remove_overlap(7, t.end())
    assert not t[7:]

    t = trees['ivs1']()
    assert t[:7]
    t.remove_overlap(t.begin(), 7)
    assert not t[:7]


def test_remove_overlap():
    t = trees['ivs1']()
    assert t[1]
    t.remove_overlap(1)
    assert not t[1]
    t.verify()

    assert t[8]
    t.remove_overlap(8)
    assert not t[8]
    t.verify()


def test_chop():
    t = IntervalTree([Interval(0, 10)])
    t.chop(3, 7)
    assert len(t) == 2
    assert sorted(t)[0] == Interval(0, 3)
    assert sorted(t)[1] == Interval(7, 10)

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 7)
    assert len(t) == 1
    assert sorted(t)[0] == Interval(7, 10)

    t = IntervalTree([Interval(0, 10)])
    t.chop(5, 10)
    assert len(t) == 1
    assert sorted(t)[0] == Interval(0, 5)

    t = IntervalTree([Interval(0, 10)])
    t.chop(-5, 15)
    assert len(t) == 0

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 10)
    assert len(t) == 0


def test_chop_datafunc():
    def datafunc(iv, islower):
        oldlimit = iv[islower]
        return "oldlimit: {0}, islower: {1}".format(oldlimit, islower)

    t = IntervalTree([Interval(0, 10)])
    t.chop(3, 7, datafunc)
    assert len(t) == 2
    assert sorted(t)[0] == Interval(0, 3, 'oldlimit: 10, islower: True')
    assert sorted(t)[1] == Interval(7, 10, 'oldlimit: 0, islower: False')

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 7, datafunc)
    assert len(t) == 1
    assert sorted(t)[0] == Interval(7, 10, 'oldlimit: 0, islower: False')

    t = IntervalTree([Interval(0, 10)])
    t.chop(5, 10, datafunc)
    assert len(t) == 1
    assert sorted(t)[0] == Interval(0, 5, 'oldlimit: 10, islower: True')

    t = IntervalTree([Interval(0, 10)])
    t.chop(-5, 15, datafunc)
    assert len(t) == 0

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 10, datafunc)
    assert len(t) == 0


def test_slice():
    t = IntervalTree([Interval(5, 15)])
    t.slice(10)
    assert sorted(t)[0] == Interval(5, 10)
    assert sorted(t)[1] == Interval(10, 15)

    t = IntervalTree([Interval(5, 15)])
    t.slice(5)
    assert sorted(t)[0] == Interval(5, 15)

    t.slice(15)
    assert sorted(t)[0] == Interval(5, 15)

    t.slice(0)
    assert sorted(t)[0] == Interval(5, 15)

    t.slice(20)
    assert sorted(t)[0] == Interval(5, 15)


def test_slice_datafunc():
    def datafunc(iv, islower):
        oldlimit = iv[islower]
        return "oldlimit: {0}, islower: {1}".format(oldlimit, islower)

    t = IntervalTree([Interval(5, 15)])
    t.slice(10, datafunc)
    assert sorted(t)[0] == Interval(5, 10, 'oldlimit: 15, islower: True')
    assert sorted(t)[1] == Interval(10, 15, 'oldlimit: 5, islower: False')

    t = IntervalTree([Interval(5, 15)])
    t.slice(5, datafunc)
    assert sorted(t)[0] == Interval(5, 15)

    t.slice(15, datafunc)
    assert sorted(t)[0] == Interval(5, 15)

    t.slice(0, datafunc)
    assert sorted(t)[0] == Interval(5, 15)

    t.slice(20, datafunc)
    assert sorted(t)[0] == Interval(5, 15)


def test_split_overlap():
    t = trees['ivs1']()

    t.split_overlaps()
    t.verify()

    while t:
        iv = set(t).pop()
        t.remove(iv)
        for other in t.search(iv):
            assert other.begin == iv.begin
            assert other.end == iv.end

def test_merge_overlap():
    t = trees['ivs1']()

    t.merge_overlaps()
    t.verify()

    assert len(t) == 2
    assert sorted(t)[0] == Interval(1,2,'[1,2)')
    assert sorted(t)[1] == Interval(4,15)

def test_merge_overlap_datafunc():
    t = trees['ivs1']()

    def func(lower,higher):
        return lower

    t.merge_overlaps(func)
    t.verify()

    assert len(t) == 2
    assert sorted(t)[0] == Interval(1,2,'[1,2)')
    assert sorted(t)[1] == Interval(4,15,'[4,7)')

def test_merge_equals():
    t = trees['ivs1']()
    t.addi(4,7,'foo')

    t.merge_equals()
    t.verify()

    assert len(t.search(4,7,True)) == 1
    assert sorted(t.search(4,7,True))[0] == Interval(4,7)

def test_merge_equals_datafunc():
    t = trees['ivs1']()
    t.addi(4,7,'foo')

    def func(lower,higher):
        return lower

    t.merge_equals(func)
    t.verify()

    assert len(t.search(4,7,True)) == 1
    assert sorted(t.search(4,7,True))[0] == Interval(4,7,'[4,7)')

def test_pickle():
    t = trees['ivs1']()

    p = pickle.dumps(t)
    t2 = pickle.loads(p)

    assert t == t2
    t2.verify()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
