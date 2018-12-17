"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Basic insertion methods

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

    tree.update([Interval(19.9, 20.1), Interval(20.1, 30)])
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

    tree.update([Interval(-10, 20, "arbitrary data")])
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

    tree.update([Interval(-10, 20), Interval(-10, 20, "arbitrary data")])
    assert len(tree) == 2
    assert tree.items() == contents


def test_same_range_insert():
    t = IntervalTree.from_tuples(data.ivs1.data)

    t.add(Interval(14, 15, '[14,15)####'))
    assert match.set_data(t[14]) == set(['[8,15)', '[14,15)', '[14,15)####'])
    t.verify()


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


def test_insert_to_filled_tree():
    t = IntervalTree.from_tuples(data.ivs1.data)
    orig = t.print_structure(True)  # original structure record

    assert match.set_data(t[1]) == set(['[1,2)'])
    t.add(Interval(1, 2, '[1,2)'))  # adding duplicate should do nothing
    assert match.set_data(t[1]) == set(['[1,2)'])
    assert orig == t.print_structure(True)

    t[1:2] = '[1,2)'                # adding duplicate should do nothing
    assert match.set_data(t[1]) == set(['[1,2)'])
    assert orig == t.print_structure(True)

    assert Interval(2, 4, '[2,4)') not in t
    t.add(Interval(2, 4, '[2,4)'))
    assert match.set_data(t[2]) == set(['[2,4)'])
    t.verify()

    t[13:15] = '[13,15)'
    assert match.set_data(t[14]) == set(['[8,15)', '[13,15)', '[14,15)'])
    t.verify()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
