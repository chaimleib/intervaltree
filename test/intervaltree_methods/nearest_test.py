"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, nearest() queries

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
from random import Random


def brute_force(intervals, target, k):
    ranked = sorted(intervals, key=lambda iv: (iv.distance_to(target), iv))
    return ranked[:k]


def test_empty_tree():
    t = IntervalTree()
    assert t.nearest(5) is None
    assert t.nearest(5, k=3) == []
    assert t.nearest(Interval(1, 2)) is None


def test_point_inside_interval():
    t = IntervalTree.from_tuples([(0, 5, 'a'), (10, 15, 'b')])
    assert t.nearest(3) == Interval(0, 5, 'a')
    assert t.nearest(10) == Interval(10, 15, 'b')


def test_point_in_gap():
    t = IntervalTree.from_tuples([(0, 5, 'a'), (10, 15, 'b')])
    assert t.nearest(6) == Interval(0, 5, 'a')
    assert t.nearest(8) == Interval(10, 15, 'b')
    assert t.nearest(-100) == Interval(0, 5, 'a')
    assert t.nearest(100) == Interval(10, 15, 'b')


def test_point_at_open_end():
    t = IntervalTree.from_tuples([(0, 5, 'a'), (6, 9, 'b')])
    assert t.nearest(5, k=2) == [Interval(0, 5, 'a'), Interval(6, 9, 'b')]
    assert Interval(0, 5, 'a').distance_to(5) == 0


def test_interval_target():
    t = IntervalTree.from_tuples([(0, 5), (10, 15), (30, 40)])
    assert t.nearest(Interval(4, 8)) == Interval(0, 5)
    assert t.nearest(Interval(16, 20)) == Interval(10, 15)
    assert t.nearest(Interval(22, 26)) == Interval(30, 40)
    assert t.nearest(Interval(-50, 100)) == Interval(0, 5)


def test_touching_interval_is_at_distance_zero():
    t = IntervalTree.from_tuples([(0, 5), (7, 9)])
    assert t.nearest(Interval(5, 6), k=1) == [Interval(0, 5)]
    assert t.nearest(Interval(6, 7), k=2) == [Interval(7, 9), Interval(0, 5)]


def test_k_returns_list_nearest_first():
    t = IntervalTree.from_tuples([(0, 1), (3, 4), (10, 11), (20, 21)])
    assert t.nearest(5, k=3) == [Interval(3, 4), Interval(0, 1), Interval(10, 11)]
    assert t.nearest(5, k=1) == [Interval(3, 4)]


def test_k_zero():
    t = IntervalTree.from_tuples([(0, 1)])
    assert t.nearest(0, k=0) == []


def test_k_larger_than_tree():
    t = IntervalTree.from_tuples([(0, 1), (5, 6), (9, 12)])
    assert t.nearest(4, k=10) == [Interval(5, 6), Interval(0, 1), Interval(9, 12)]


def test_ties_are_broken_by_interval_order():
    t = IntervalTree.from_tuples([(10, 12, 'x'), (0, 4, 'y'), (0, 4, 'x')])
    assert t.nearest(7, k=3) == [
        Interval(0, 4, 'x'),
        Interval(0, 4, 'y'),
        Interval(10, 12, 'x'),
    ]
    assert t.nearest(7) == Interval(0, 4, 'x')


def test_ties_with_unorderable_data():
    t = IntervalTree([Interval(0, 4, 'a'), Interval(0, 4, 1), Interval(10, 12)])
    result = t.nearest(7, k=3)
    assert result[:2] == sorted([Interval(0, 4, 'a'), Interval(0, 4, 1)])
    assert result[2] == Interval(10, 12)


def test_float_and_negative_coordinates():
    t = IntervalTree.from_tuples([(-2.5, -1.5), (0.5, 1.0), (4.25, 9.0)])
    assert t.nearest(-1.0) == Interval(-2.5, -1.5)
    assert t.nearest(2.0) == Interval(0.5, 1.0)
    assert t.nearest(3.0, k=2) == [Interval(4.25, 9.0), Interval(0.5, 1.0)]


def test_nearest_after_mutation():
    t = IntervalTree.from_tuples([(0, 1), (100, 101)])
    assert t.nearest(50) == Interval(0, 1)
    t.addi(48, 49)
    assert t.nearest(50) == Interval(48, 49)
    t.remove(Interval(48, 49))
    assert t.nearest(50) == Interval(0, 1)


def test_tree_is_not_modified():
    t = IntervalTree.from_tuples([(0, 1), (5, 6), (9, 12)])
    before = set(t)
    t.nearest(4, k=2)
    assert set(t) == before
    t.verify()


def test_null_interval_target():
    t = IntervalTree.from_tuples([(0, 1)])
    with pytest.raises(ValueError):
        t.nearest(Interval(3, 3))
    with pytest.raises(ValueError):
        t.nearest(Interval(5, 3), k=2)


def test_invalid_k():
    t = IntervalTree.from_tuples([(0, 1)])
    with pytest.raises(ValueError):
        t.nearest(0, k=-1)
    for bad in (1.5, '2', True):
        with pytest.raises(TypeError):
            t.nearest(0, k=bad)


def test_against_brute_force():
    rng = Random(20240229)
    for _ in range(300):
        intervals = set()
        for _ in range(rng.randint(0, 25)):
            begin = rng.randint(-20, 20)
            intervals.add(Interval(begin, begin + rng.randint(1, 8),
                                   rng.choice([None, 'a', 'b'])))
        t = IntervalTree(intervals)
        if rng.random() < 0.5:
            target = rng.randint(-30, 30)
        else:
            begin = rng.randint(-30, 30)
            target = Interval(begin, begin + rng.randint(1, 8))
        for k in (1, 2, 3, 7, 40):
            assert t.nearest(target, k=k) == brute_force(intervals, target, k)
        expected = brute_force(intervals, target, 1)
        assert t.nearest(target) == (expected[0] if expected else None)


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
