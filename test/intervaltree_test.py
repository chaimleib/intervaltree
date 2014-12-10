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
from .intervaltrees import tree1, sdata
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


# TODO: replace this with optimality test
def test_basic_structuring():
    t = tree1()
    t.verify()
    orig = t.print_structure(True)
        
    assert orig == """\
Node<8, depth=3, balance=0>
 Interval(5, 9, '[5,9)')
 Interval(6, 10, '[6,10)')
 Interval(8, 10, '[8,10)')
 Interval(8, 15, '[8,15)')
<:  Node<4, depth=2, balance=-1>
     Interval(4, 7, '[4,7)')
    <:  Node<1, depth=1, balance=0>
         Interval(1, 2, '[1,2)')
>:  Node<12, depth=2, balance=0>
     Interval(12, 14, '[12,14)')
    <:  Node<10, depth=1, balance=0>
         Interval(10, 12, '[10,12)')
    >:  Node<14, depth=1, balance=0>
         Interval(14, 15, '[14,15)')
"""


def test_queries():
    t = tree1()

    assert sdata(t[4]) == set(['[4,7)'])
    assert sdata(t[4:5]) == set(['[4,7)'])
    assert sdata(t[4:6]) == set(['[4,7)', '[5,9)'])
    assert sdata(t[9]) == set(['[6,10)', '[8,10)', '[8,15)'])
    assert sdata(t[15]) == set()
    assert sdata(t.search(5)) == set(['[4,7)', '[5,9)'])
    assert sdata(t.search(6, 11, strict=True)) == set(['[6,10)', '[8,10)'])
    

def test_membership():
    t = tree1()
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
    t = tree1()
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
    t = tree1()

    t.add(Interval(14, 15, '[14,15)####'))
    assert sdata(t[14]) == set(['[8,15)', '[14,15)', '[14,15)####'])
    t.verify()


def test_copy_cast():
    t = tree1()

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
    t = tree1()
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


def test_emptying():
    t = tree1()

    for iv in sorted(iter(t)):
        t.remove(iv)
        t.verify()
    assert len(t) == 0
    assert t.is_empty()
    assert not t


def test_remove_overlap():
    t = tree1()
    assert t[1]
    t.remove_overlap(1)
    assert not t[1]
    t.verify()

    assert t[8]
    t.remove_overlap(8)
    assert not t[8]
    t.verify()


def test_split_overlap():
    t = tree1()

    t.split_overlaps()
    t.verify()

    while t:
        iv = set(t).pop()
        t.remove(iv)
        for other in t.search(iv):
            assert other.begin == iv.begin
            assert other.end == iv.end


def test_pickle():
    t = tree1()

    p = pickle.dumps(t)
    t2 = pickle.loads(p)

    assert t == t2
    t2.verify()
