"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Special methods

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
from test import data
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_emptying_partial():
    t = IntervalTree.from_tuples(data.ivs1.data)
    assert t[7:]
    t.remove_overlap(7, t.end())
    assert not t[7:]

    t = IntervalTree.from_tuples(data.ivs1.data)
    assert t[:7]
    t.remove_overlap(t.begin(), 7)
    assert not t[:7]


def test_remove_overlap():
    t = IntervalTree.from_tuples(data.ivs1.data)
    assert t[1]
    t.remove_overlap(1)
    assert not t[1]
    t.verify()

    assert t[8]
    t.remove_overlap(8)
    assert not t[8]
    t.verify()


def test_merge_overlaps_empty():
    t = IntervalTree()
    t.merge_overlaps()
    t.verify()

    assert len(t) == 0


def test_merge_overlaps_gapless():
    # default strict=True
    t = IntervalTree.from_tuples(data.ivs2.data)
    t.merge_overlaps()
    t.verify()
    assert [(iv.begin, iv.end, iv.data) for iv in sorted(t)] == data.ivs2.data

    # strict=False
    t = IntervalTree.from_tuples(data.ivs2.data)
    rng = t.range()
    t.merge_overlaps(strict=False)
    t.verify()
    assert len(t) == 1
    assert t.pop() == rng

def test_merge_overlaps_with_gap():
    t = IntervalTree.from_tuples(data.ivs1.data)

    t.merge_overlaps()
    t.verify()
    assert len(t) == 2
    assert t == IntervalTree([Interval(1, 2, '[1,2)'), Interval(4, 15)])


def test_merge_overlaps_reducer_wo_initializer():
    def reducer(old, new):
        return "%s, %s" % (old, new)
    # empty tree
    e = IntervalTree()
    e.merge_overlaps(data_reducer=reducer)
    e.verify()
    assert not e

    # One Interval in tree
    o = IntervalTree.from_tuples([(1, 2, 'hello')])
    o.merge_overlaps(data_reducer=reducer)
    o.verify()
    assert len(o) == 1
    assert sorted(o) == [Interval(1, 2, 'hello')]

    # many Intervals in tree, with gap
    t = IntervalTree.from_tuples(data.ivs1.data)
    t.merge_overlaps(data_reducer=reducer)
    t.verify()
    assert len(t) == 2
    assert sorted(t) == [
        Interval(1, 2,'[1,2)'),
        Interval(4, 15, '[4,7), [5,9), [6,10), [8,10), [8,15), [10,12), [12,14), [14,15)')
    ]


def test_merge_overlaps_reducer_with_initializer():
    def reducer(old, new):
        return old + [new]
    # empty tree
    e = IntervalTree()
    e.merge_overlaps(data_reducer=reducer, data_initializer=[])
    e.verify()
    assert not e

    # One Interval in tree
    o = IntervalTree.from_tuples([(1, 2, 'hello')])
    o.merge_overlaps(data_reducer=reducer, data_initializer=[])
    o.verify()
    assert len(o) == 1
    assert sorted(o) == [Interval(1, 2, ['hello'])]

    # many Intervals in tree, with gap
    t = IntervalTree.from_tuples(data.ivs1.data)
    t.merge_overlaps(data_reducer=reducer, data_initializer=[])
    t.verify()
    assert len(t) == 2
    assert sorted(t) == [
        Interval(1, 2, ['[1,2)']),
        Interval(4, 15, [
            '[4,7)',
            '[5,9)',
            '[6,10)',
            '[8,10)',
            '[8,15)',
            '[10,12)',
            '[12,14)',
            '[14,15)',
        ])
    ]


def test_merge_equals_empty():
    t = IntervalTree()
    t.merge_equals()
    t.verify()

    assert len(t) == 0


def test_merge_equals_wo_dupes():
    t = IntervalTree.from_tuples(data.ivs1.data)
    orig = IntervalTree.from_tuples(data.ivs1.data)
    assert orig == t

    t.merge_equals()
    t.verify()

    assert orig == t


def test_merge_equals_with_dupes():
    t = IntervalTree.from_tuples(data.ivs1.data)
    orig = IntervalTree.from_tuples(data.ivs1.data)
    assert orig == t

    # one dupe
    assert t.containsi(4, 7, '[4,7)')
    t.addi(4, 7, 'foo')
    assert len(t) == len(orig) + 1
    assert orig != t

    t.merge_equals()
    t.verify()
    assert t != orig
    assert t.containsi(4, 7)
    assert not t.containsi(4, 7, 'foo')
    assert not t.containsi(4, 7, '[4,7)')

    # two dupes
    t = IntervalTree.from_tuples(data.ivs1.data)
    t.addi(4, 7, 'foo')
    assert t.containsi(10, 12, '[10,12)')
    t.addi(10, 12, 'bar')
    assert len(t) == len(orig) + 2
    assert t != orig

    t.merge_equals()
    t.verify()
    assert t != orig
    assert t.containsi(4, 7)
    assert not t.containsi(4, 7, 'foo')
    assert not t.containsi(4, 7, '[4,7)')
    assert t.containsi(10, 12)
    assert not t.containsi(10, 12, 'bar')
    assert not t.containsi(10, 12, '[10,12)')


def test_merge_equals_reducer_wo_initializer():
    def reducer(old, new):
        return "%s, %s" % (old, new)
    # empty tree
    e = IntervalTree()
    e.merge_equals(data_reducer=reducer)
    e.verify()
    assert not e

    # One Interval in tree, no change
    o = IntervalTree.from_tuples([(1, 2, 'hello')])
    o.merge_equals(data_reducer=reducer)
    o.verify()
    assert len(o) == 1
    assert sorted(o) == [Interval(1, 2, 'hello')]

    # many Intervals in tree, no change
    t = IntervalTree.from_tuples(data.ivs1.data)
    orig = IntervalTree.from_tuples(data.ivs1.data)
    t.merge_equals(data_reducer=reducer)
    t.verify()
    assert len(t) == len(orig)
    assert t == orig

    # many Intervals in tree, with change
    t = IntervalTree.from_tuples(data.ivs1.data)
    orig = IntervalTree.from_tuples(data.ivs1.data)
    t.addi(4, 7, 'foo')
    t.merge_equals(data_reducer=reducer)
    t.verify()
    assert len(t) == len(orig)
    assert t != orig
    assert not t.containsi(4, 7, 'foo')
    assert not t.containsi(4, 7, '[4,7)')
    assert t.containsi(4, 7, '[4,7), foo')


def test_merge_equals_reducer_with_initializer():
    def reducer(old, new):
        return old + [new]
    # empty tree
    e = IntervalTree()
    e.merge_equals(data_reducer=reducer, data_initializer=[])
    e.verify()
    assert not e

    # One Interval in tree, no change
    o = IntervalTree.from_tuples([(1, 2, 'hello')])
    o.merge_equals(data_reducer=reducer, data_initializer=[])
    o.verify()
    assert len(o) == 1
    assert sorted(o) == [Interval(1, 2, ['hello'])]

    # many Intervals in tree, no change
    t = IntervalTree.from_tuples(data.ivs1.data)
    orig = IntervalTree.from_tuples(data.ivs1.data)
    t.merge_equals(data_reducer=reducer, data_initializer=[])
    t.verify()
    assert len(t) == len(orig)
    assert t != orig
    assert sorted(t) == [Interval(b, e, [d]) for b, e, d in sorted(orig)]

    # many Intervals in tree, with change
    t = IntervalTree.from_tuples(data.ivs1.data)
    orig = IntervalTree.from_tuples(data.ivs1.data)
    t.addi(4, 7, 'foo')
    t.merge_equals(data_reducer=reducer, data_initializer=[])
    t.verify()
    assert len(t) == len(orig)
    assert t != orig
    assert not t.containsi(4, 7, 'foo')
    assert not t.containsi(4, 7, '[4,7)')
    assert t.containsi(4, 7, ['[4,7)', 'foo'])


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


def test_split_overlap_empty():
    t = IntervalTree()
    t.split_overlaps()
    t.verify()
    assert not t


def test_split_overlap_single_member():
    t = IntervalTree([Interval(0, 1)])
    t.split_overlaps()
    t.verify()
    assert len(t) == 1


def test_split_overlap():
    t = IntervalTree.from_tuples(data.ivs1.data)

    t.split_overlaps()
    t.verify()

    while t:
        iv = set(t).pop()
        t.remove(iv)
        for other in t.overlap(iv):
            assert other.begin == iv.begin
            assert other.end == iv.end


def test_pickle():
    t = IntervalTree.from_tuples(data.ivs1.data)

    p = pickle.dumps(t)
    t2 = pickle.loads(p)

    assert t == t2
    t2.verify()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
