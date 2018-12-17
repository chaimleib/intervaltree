"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Basic query methods (read-only)

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
from intervaltree import Interval, IntervalTree
import pytest
from test import data, match
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
    assert t.overlap(t.begin(), t.end()) == e
    assert t.envelop(t.begin(), t.end()) == e
    assert t.items() == e
    assert set(t) == e
    assert set(t.copy()) == e
    assert t.find_nested() == {}
    assert t.range().is_null()
    assert t.range().length() == 0
    t.verify()


def test_point_queries():
    t = IntervalTree.from_tuples(data.ivs1.data)
    assert match.set_data(t[4]) == set(['[4,7)'])
    assert match.set_data(t.at(4)) == set(['[4,7)'])
    assert match.set_data(t[9]) == set(['[6,10)', '[8,10)', '[8,15)'])
    assert match.set_data(t.at(9)) == set(['[6,10)', '[8,10)', '[8,15)'])
    assert match.set_data(t[15]) == set()
    assert match.set_data(t.at(15)) == set()
    assert match.set_data(t[5]) == set(['[4,7)', '[5,9)'])
    assert match.set_data(t.at(5)) == set(['[4,7)', '[5,9)'])
    assert match.set_data(t[4:5]) == set(['[4,7)'])


def test_envelop_vs_overlap_queries():
    t = IntervalTree.from_tuples(data.ivs1.data)
    assert match.set_data(t.envelop(4, 5)) == set()
    assert match.set_data(t.overlap(4, 5)) == set(['[4,7)'])
    assert match.set_data(t.envelop(4, 6)) == set()
    assert match.set_data(t.overlap(4, 6)) == set(['[4,7)', '[5,9)'])
    assert match.set_data(t.envelop(6, 10)) == set(['[6,10)', '[8,10)'])
    assert match.set_data(t.overlap(6, 10)) == set([
        '[4,7)', '[5,9)', '[6,10)', '[8,10)', '[8,15)'])
    assert match.set_data(t.envelop(6, 11)) == set(['[6,10)', '[8,10)'])
    assert match.set_data(t.overlap(6, 11)) == set([
        '[4,7)', '[5,9)', '[6,10)', '[8,10)', '[8,15)', '[10,12)'])


def test_partial_get_query():
    def assert_get(t, limit):
        s = set(t)
        assert t[:] == s

        s = set(iv for iv in t if iv.begin < limit)
        assert t[:limit] == s

        s = set(iv for iv in t if iv.end > limit)
        assert t[limit:] == s

    assert_get(IntervalTree.from_tuples(data.ivs1.data), 7)
    assert_get(IntervalTree.from_tuples(data.ivs2.data), -3)


def test_tree_bounds():
    def assert_tree_bounds(t):
        begin, end, _ = set(t).pop()
        for iv in t:
            if iv.begin < begin: begin = iv.begin
            if iv.end > end: end = iv.end
        assert t.begin() == begin
        assert t.end() == end

    assert_tree_bounds(IntervalTree.from_tuples(data.ivs1.data))
    assert_tree_bounds(IntervalTree.from_tuples(data.ivs2.data))


def test_membership():
    t = IntervalTree.from_tuples(data.ivs1.data)
    assert Interval(1, 2, '[1,2)') in t
    assert t.containsi(1, 2, '[1,2)')
    assert Interval(1, 3, '[1,3)') not in t
    assert not t.containsi(1, 3, '[1,3)')
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
    t = IntervalTree.from_tuples(data.ivs1.data)
    assert not t.overlaps(-3.2)
    assert t.overlaps(1)
    assert t.overlaps(1.5)
    assert t.overlaps(0, 3)
    assert not t.overlaps(0, 1)
    assert not t.overlaps(2, 4)
    assert not t.overlaps(4, 2)
    assert not t.overlaps(3, 0)


def test_span():
    e = IntervalTree()
    assert e.span() == 0

    t = IntervalTree.from_tuples(data.ivs1.data)
    assert t.span() == t.end() - t.begin()
    assert t.span() == 14


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
