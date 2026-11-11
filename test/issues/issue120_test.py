"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, range queries walk the tree once.
Submitted as issue #120 (Range Query Much Slower than List Scan)
by william-silversmith

overlap() and envelop() used to run one point search per boundary
point inside the queried range. These tests compare the single-walk
versions with a plain scan of all the intervals.

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
from intervaltree.node import Node
import random


def scan_overlap(ivs, begin, end):
    if begin >= end:
        return set()
    return set(iv for iv in ivs if iv.begin < end and iv.end > begin)


def scan_envelop(ivs, begin, end):
    if begin >= end:
        return set()
    return set(iv for iv in ivs if iv.begin >= begin and iv.end <= end)


def check_all_ranges(tree, points):
    tree.verify()
    ivs = list(tree)
    for begin in points:
        for end in points:
            assert tree.overlap(begin, end) == scan_overlap(ivs, begin, end), (begin, end)
            assert tree.envelop(begin, end) == scan_envelop(ivs, begin, end), (begin, end)
            assert tree.overlap(Interval(begin, end)) == scan_overlap(ivs, begin, end)
            assert tree.envelop(Interval(begin, end)) == scan_envelop(ivs, begin, end)
            assert tree[begin:end] == scan_overlap(ivs, begin, end)


def random_ivs(rng, count, span, max_length, data_choices=1):
    ivs = []
    for i in range(count):
        begin = rng.randint(0, span)
        end = begin + rng.randint(1, max_length)
        ivs.append(Interval(begin, end, i % data_choices))
    return ivs


def test_range_queries_match_scan_small_dense():
    # Few distinct endpoints, so many intervals share a Node, a range,
    # or both. Every pair of points is queried, including the ones just
    # outside the tree, null ranges and reversed ranges.
    rng = random.Random(120)
    points = list(range(-1, 14))
    for _ in range(40):
        ivs = random_ivs(rng, rng.randint(0, 40), 11, 6, data_choices=3)
        check_all_ranges(IntervalTree(ivs), points)


def test_range_queries_match_scan_after_mutation():
    # Trees that were built one interval at a time and then pruned
    # have different shapes from trees built in one go.
    rng = random.Random(121)
    points = list(range(-1, 32))
    for _ in range(15):
        ivs = random_ivs(rng, 60, 28, 9, data_choices=2)
        tree = IntervalTree()
        for iv in ivs:
            tree.add(iv)
        check_all_ranges(tree, points)
        for iv in rng.sample(ivs, 30):
            tree.discard(iv)
        check_all_ranges(tree, points)
        tree.remove_overlap(10, 14)
        tree.remove_envelop(18, 26)
        tree.chop(3, 6)
        check_all_ranges(tree, points)


def test_range_queries_match_scan_floats():
    rng = random.Random(122)
    values = [-2.5, -1.0, -0.5, 0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.75]
    points = [float('-inf')] + values + [4.0, float('inf')]
    for _ in range(40):
        ivs = []
        for i in range(rng.randint(1, 25)):
            begin, end = sorted(rng.sample(values, 2))
            ivs.append(Interval(begin, end, i))
        check_all_ranges(IntervalTree(ivs), points)


def test_range_queries_match_scan_deep_tree():
    rng = random.Random(123)
    ivs = random_ivs(rng, 3000, 20000, 1, data_choices=5)
    ivs += random_ivs(rng, 300, 20000, 600)
    ivs += random_ivs(rng, 30, 20000, 8000)
    tree = IntervalTree(ivs)
    assert tree.top_node.depth >= 8
    for step in range(2):
        tree.verify()
        current = list(tree)
        for _ in range(300):
            begin = rng.randint(-10, 20100)
            end = begin + rng.choice([0, 1, 2, 30, 700, 9000, 30000])
            assert tree.overlap(begin, end) == scan_overlap(current, begin, end)
            assert tree.envelop(begin, end) == scan_envelop(current, begin, end)
        for iv in rng.sample(ivs, 1500):
            tree.discard(iv)


def test_range_queries_half_open_boundaries():
    tree = IntervalTree([Interval(0, 10), Interval(10, 20), Interval(20, 30)])
    assert tree.overlap(10, 20) == set([Interval(10, 20)])
    assert tree.overlap(9, 21) == set(tree)
    assert tree.overlap(10, 10) == set()
    assert tree.overlap(20, 10) == set()
    assert tree.overlap(30, 40) == set()
    assert tree.overlap(-5, 0) == set()
    assert tree.envelop(10, 20) == set([Interval(10, 20)])
    assert tree.envelop(10, 19) == set()
    assert tree.envelop(11, 20) == set()
    assert tree.envelop(0, 30) == set(tree)


def test_range_query_does_not_search_point_by_point():
    # The old implementation searched from the root once for every
    # boundary point in the range: about 2,000 searches for this
    # query. Now there are none, and the tree is not touched by them.
    tree = IntervalTree(Interval(i, i + 1) for i in range(1000))
    calls = []
    original = Node.search_point

    def counting_search_point(self, point, result):
        calls.append(point)
        return original(self, point, result)

    Node.search_point = counting_search_point
    try:
        assert len(tree.overlap(0, 1000)) == 1000
        assert len(tree.envelop(0, 1000)) == 1000
        assert len(tree.overlap(250, 750)) == 500
        assert len(tree.envelop(250, 750)) == 500
    finally:
        Node.search_point = original
    assert calls == []
