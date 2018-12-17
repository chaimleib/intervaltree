"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Basic deletion methods

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


def test_delete():
    t = IntervalTree.from_tuples(data.ivs1.data)
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

    assert match.set_data(t[14]) == set(['[8,15)', '[14,15)'])
    t.remove(Interval(14, 15, '[14,15)'))
    assert match.set_data(t[14]) == set(['[8,15)'])
    t.verify()

    t.discard(Interval(8, 15, '[8,15)'))
    assert match.set_data(t[14]) == set()
    t.verify()

    assert t[5]
    t.remove_overlap(5)
    t.verify()
    assert not t[5]


def test_removei():
    # Empty tree
    e = IntervalTree()
    with pytest.raises(ValueError):
        e.removei(-1000, -999, "Doesn't exist")
    e.verify()
    assert len(e) == 0

    # Non-existent member should raise ValueError
    t = IntervalTree.from_tuples(data.ivs1.data)
    oldlen = len(t)
    with pytest.raises(ValueError):
        t.removei(-1000, -999, "Doesn't exist")
    t.verify()
    assert len(t) == oldlen

    # Should remove existing member
    assert Interval(1, 2, '[1,2)') in t
    t.removei(1, 2, '[1,2)')
    assert len(t) == oldlen - 1
    assert Interval(1, 2, '[1,2)') not in t


def test_discardi():
    # Empty tree
    e = IntervalTree()
    e.discardi(-1000, -999, "Doesn't exist")
    e.verify()
    assert len(e) == 0

    # Non-existent member should do nothing quietly
    t = IntervalTree.from_tuples(data.ivs1.data)
    oldlen = len(t)
    t.discardi(-1000, -999, "Doesn't exist")
    t.verify()
    assert len(t) == oldlen

    # Should discard existing member
    assert Interval(1, 2, '[1,2)') in t
    t.discardi(1, 2, '[1,2)')
    assert len(t) == oldlen - 1
    assert Interval(1, 2, '[1,2)') not in t


def test_emptying_iteration():
    t = IntervalTree.from_tuples(data.ivs1.data)

    for iv in sorted(iter(t)):
        t.remove(iv)
        t.verify()
    assert len(t) == 0
    assert t.is_empty()
    assert not t


def test_emptying_clear():
    t = IntervalTree.from_tuples(data.ivs1.data)
    assert t
    t.clear()
    assert len(t) == 0
    assert t.is_empty()
    assert not t

    # make sure emptying an empty tree does not crash
    t.clear()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
