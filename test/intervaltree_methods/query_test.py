"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Basic query methods (read-only)

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
from test.intervaltrees import trees, sdata
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_empty_queries():
    t = IntervalTree()
    e = set()

    assert len(t) == 0
    assert t.is_empty()
    assert t[3] == e
    assert t[4:6] == e
    assert t.begin() == 0
    assert t.end() == 0
    assert t[t.begin():t.end()] == e
    assert t.items() == e
    assert set(t) == e
    assert set(t.copy()) == e
    assert t.find_nested() == {}
    assert t.range().is_null()
    assert t.range().length() == 0
    assert t.length() == 0
    t.verify()


def test_queries():
    t = trees['ivs1']()

    assert sdata(t[4]) == set(['[4,7)'])
    assert sdata(t[4:5]) == set(['[4,7)'])
    assert sdata(t[4:6]) == set(['[4,7)', '[5,9)'])
    assert sdata(t[9]) == set(['[6,10)', '[8,10)', '[8,15)'])
    assert sdata(t[15]) == set()
    assert sdata(t.search(5)) == set(['[4,7)', '[5,9)'])
    assert sdata(t.search(6, 11, strict=True)) == set(['[6,10)', '[8,10)'])


def test_partial_slice_query():
    def assert_chop(t, limit):
        s = set(t)
        assert t[:] == s

        s = set(iv for iv in t if iv.begin < limit)
        assert t[:limit] == s

        s = set(iv for iv in t if iv.end > limit)
        assert t[limit:] == s

    assert_chop(trees['ivs1'](), 7)
    assert_chop(trees['ivs2'](), -3)


def test_tree_bounds():
    def assert_tree_bounds(t):
        begin, end, _ = set(t).pop()
        for iv in t:
            if iv.begin < begin: begin = iv.begin
            if iv.end > end: end = iv.end
        assert t.begin() == begin
        assert t.end() == end

    assert_tree_bounds(trees['ivs1']())
    assert_tree_bounds(trees['ivs2']())


def test_membership():
    t = trees['ivs1']()
    assert Interval(1, 2, '[1,2)') in t
    assert Interval(1, 3, '[1,3)') not in t
    assert t.overlaps(4)
    assert t.overlaps(9)
    assert not t.overlaps(15)
    assert t.overlaps(0, 4)
    assert t.overlaps(1, 2)
    assert t.overlaps(1, 3)
    assert t.overlaps(8, 15)
    assert not t.overlaps(15, 16)
    assert not t.overlaps(-1, 0)
    assert not t.overlaps(2, 4)

def test_overlaps_empty():
    # Empty tree
    t = IntervalTree()
    assert not t.overlaps(-1)
    assert not t.overlaps(0)

    assert not t.overlaps(-1, 1)
    assert not t.overlaps(-1, 0)
    assert not t.overlaps(0, 0)
    assert not t.overlaps(0, 1)
    assert not t.overlaps(1, 0)
    assert not t.overlaps(1, -1)
    assert not t.overlaps(0, -1)

    assert not t.overlaps(Interval(-1, 1))
    assert not t.overlaps(Interval(-1, 0))
    assert not t.overlaps(Interval(0, 0))
    assert not t.overlaps(Interval(0, 1))
    assert not t.overlaps(Interval(1, 0))
    assert not t.overlaps(Interval(1, -1))
    assert not t.overlaps(Interval(0, -1))


def test_overlaps():
    t = trees['ivs1']()
    assert not t.overlaps(-3.2)
    assert t.overlaps(1)
    assert t.overlaps(1.5)
    assert t.overlaps(0, 3)
    assert not t.overlaps(0, 1)
    assert not t.overlaps(2, 4)
    assert not t.overlaps(4, 2)
    assert not t.overlaps(3, 0)

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
