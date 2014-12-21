"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTrees

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
import pytest
from intervaltree import Interval, IntervalTree

from test.intervaltrees import trees, sdata
from pprint import pprint
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_empty_init():
    tree = IntervalTree()
    tree.verify()
    assert not tree
    assert len(tree) == 0
    assert list(tree) == []
    assert tree.is_empty()


def test_list_init():
    tree = IntervalTree([Interval(-10, 10), Interval(-20.0, -10.0)])
    tree.verify()
    assert tree
    assert len(tree) == 2
    assert tree.items() == set([Interval(-10, 10), Interval(-20.0, -10.0)])
    assert tree.begin() == -20
    assert tree.end() == 10


def test_generator_init():
    tree = IntervalTree(
        Interval(begin, end) for begin, end in
        [(-10, 10), (-20, -10), (10, 20)]
    )
    tree.verify()
    assert tree
    assert len(tree) == 3
    assert tree.items() == set([
        Interval(-20, -10),
        Interval(-10, 10),
        Interval(10, 20),
    ])
    assert tree.begin() == -20
    assert tree.end() == 20


def test_insert():
    tree = IntervalTree()

    tree[0:1] = "data"
    assert len(tree) == 1
    assert tree.items() == set([Interval(0, 1, "data")])

    tree.add(Interval(10, 20))
    assert len(tree) == 2
    assert tree.items() == set([Interval(0, 1, "data"), Interval(10, 20)])

    tree.addi(19.9, 20)
    assert len(tree) == 3
    assert tree.items() == set([
        Interval(0, 1, "data"),
        Interval(19.9, 20),
        Interval(10, 20),
    ])

    tree.extend([Interval(19.9, 20.1), Interval(20.1, 30)])
    assert len(tree) == 5
    assert tree.items() == set([
        Interval(0, 1, "data"),
        Interval(19.9, 20),
        Interval(10, 20),
        Interval(19.9, 20.1),
        Interval(20.1, 30),
    ])


def test_duplicate_insert():
    tree = IntervalTree()

    # string data
    tree[-10:20] = "arbitrary data"
    contents = frozenset([Interval(-10, 20, "arbitrary data")])

    assert len(tree) == 1
    assert tree.items() == contents

    tree.addi(-10, 20, "arbitrary data")
    assert len(tree) == 1
    assert tree.items() == contents

    tree.add(Interval(-10, 20, "arbitrary data"))
    assert len(tree) == 1
    assert tree.items() == contents

    tree.extend([Interval(-10, 20, "arbitrary data")])
    assert len(tree) == 1
    assert tree.items() == contents

    # None data
    tree[-10:20] = None
    contents = frozenset([
        Interval(-10, 20),
        Interval(-10, 20, "arbitrary data"),
    ])

    assert len(tree) == 2
    assert tree.items() == contents

    tree.addi(-10, 20)
    assert len(tree) == 2
    assert tree.items() == contents

    tree.add(Interval(-10, 20))
    assert len(tree) == 2
    assert tree.items() == contents

    tree.extend([Interval(-10, 20), Interval(-10, 20, "arbitrary data")])
    assert len(tree) == 2
    assert tree.items() == contents


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
    t.verify()


def test_copy():
    itree = IntervalTree([Interval(0, 1, "x"), Interval(1, 2, ["x"])])
    itree.verify()

    itree2 = IntervalTree(itree)  # Shares Interval objects
    itree2.verify()

    itree3 = itree.copy()         # Shallow copy (same as above, as Intervals are singletons)
    itree3.verify()

    itree4 = pickle.loads(pickle.dumps(itree))  # Deep copy
    itree4.verify()

    list(itree[1])[0].data[0] = "y"
    assert sorted(itree) == [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
    assert sorted(itree2) == [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
    assert sorted(itree3) == [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
    assert sorted(itree4) == [Interval(0, 1, 'x'), Interval(1, 2, ['x'])]


def test_add_invalid_interval():
    """
    Ensure that begin < end.
    """
    itree = IntervalTree()
    with pytest.raises(ValueError):
        itree.addi(1, 0)

    with pytest.raises(ValueError):
        itree.addi(1, 1)

    with pytest.raises(ValueError):
        itree[1:0] = "value"

    with pytest.raises(ValueError):
        itree[1:1] = "value"

    with pytest.raises(ValueError):
        itree[1.1:1.05] = "value"

    with pytest.raises(ValueError):
        itree[1.1:1.1] = "value"

    with pytest.raises(ValueError):
        itree.extend([Interval(1, 0)])

    with pytest.raises(ValueError):
        itree.extend([Interval(1, 1)])


def test_init_invalid_interval():
    """
    Ensure that begin < end.
    """
    with pytest.raises(ValueError):
        IntervalTree([Interval(-1, -2)])

    with pytest.raises(ValueError):
        IntervalTree([Interval(0, 0)])

    with pytest.raises(ValueError):
        IntervalTree(Interval(b, e) for b, e in [(1, 2), (1, 0)])

    with pytest.raises(ValueError):
        IntervalTree(Interval(b, e) for b, e in [(1, 2), (1, 1)])


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


def test_insert_to_filled_tree():
    t = trees['ivs1']()
    orig = t.print_structure(True)  # original structure record

    assert sdata(t[1]) == set(['[1,2)'])
    t.add(Interval(1, 2, '[1,2)'))  # adding duplicate should do nothing
    assert sdata(t[1]) == set(['[1,2)'])
    assert orig == t.print_structure(True)

    t[1:2] = '[1,2)'                # adding duplicate should do nothing
    assert sdata(t[1]) == set(['[1,2)'])
    assert orig == t.print_structure(True)

    assert Interval(2, 4, '[2,4)') not in t
    t.add(Interval(2, 4, '[2,4)'))
    assert sdata(t[2]) == set(['[2,4)'])
    t.verify()

    t[13:15] = '[13,15)'
    assert sdata(t[14]) == set(['[8,15)', '[13,15)', '[14,15)'])
    t.verify()


def test_duplicates():
    t = trees['ivs1']()

    t.add(Interval(14, 15, '[14,15)####'))
    assert sdata(t[14]) == set(['[8,15)', '[14,15)', '[14,15)####'])
    t.verify()


def test_copy_cast():
    t = trees['ivs1']()

    tcopy = IntervalTree(t)
    tcopy.verify()
    assert t == tcopy

    tlist = list(t)
    for iv in tlist:
        assert iv in t
    for iv in t:
        assert iv in tlist

    tset = set(t)
    assert tset == t.items()


def test_delete():
    t = trees['ivs1']()
    try:
        t.remove(Interval(1, 3, "Doesn't exist"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

    try:
        t.remove(Interval(500, 1000, "Doesn't exist"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

    orig = t.print_structure(True)
    t.discard(Interval(1, 3, "Doesn't exist"))
    t.discard(Interval(500, 1000, "Doesn't exist"))
    assert orig == t.print_structure(True)

    assert sdata(t[14]) == set(['[8,15)', '[14,15)'])
    t.remove(Interval(14, 15, '[14,15)'))
    assert sdata(t[14]) == set(['[8,15)'])
    t.verify()

    t.discard(Interval(8, 15, '[8,15)'))
    assert sdata(t[14]) == set()
    t.verify()

    assert t[5]
    t.remove_overlap(5)
    t.verify()
    assert not t[5]


def test_emptying_iteration():
    t = trees['ivs1']()

    for iv in sorted(iter(t)):
        t.remove(iv)
        t.verify()
    assert len(t) == 0
    assert t.is_empty()
    assert not t


def test_emptying_empty():
    t = trees['ivs1']()
    assert t
    t.clear()
    assert len(t) == 0
    assert t.is_empty()
    assert not t

    # make sure emptying an empty tree does not crash
    t.clear()


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


def test_pickle():
    t = trees['ivs1']()

    p = pickle.dumps(t)
    t2 = pickle.loads(p)

    assert t == t2
    t2.verify()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
