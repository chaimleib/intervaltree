"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Special methods

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
from intervaltree import Interval, IntervalTree
import pytest
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_update():
    t = IntervalTree()
    interval = Interval(0, 1)
    s = set([interval])

    t.update(s)
    assert isinstance(t, IntervalTree)
    assert len(t) == 1
    assert set(t).pop() == interval

    t.clear()
    assert not t
    t.extend(s)
    t.extend(s)
    assert isinstance(t, IntervalTree)
    assert len(t) == 1
    assert set(t).pop() == interval

    interval = Interval(2, 3)
    t.update([interval])
    assert isinstance(t, IntervalTree)
    assert len(t) == 2
    assert sorted(t)[1] == interval

    t = IntervalTree(s)
    t.extend([interval])
    assert isinstance(t, IntervalTree)
    assert len(t) == 2
    assert sorted(t)[1] == interval


def test_invalid_update():
    t = IntervalTree()

    with pytest.raises(ValueError):
        t.update([Interval(1, 0)])

    with pytest.raises(ValueError):
        t.update([Interval(1, 1)])

    with pytest.raises(ValueError):
        t.extend([Interval(1, 0)])

    with pytest.raises(ValueError):
        t.extend([Interval(1, 1)])


def test_union():
    t = IntervalTree()
    interval = Interval(0, 1)
    s = set([interval])

    r = t.union(s)
    assert len(r) == 1
    assert set(r).pop() == interval

    t.extend(s)
    t.extend(s)
    assert len(t) == 1
    assert set(t).pop() == interval

    interval = Interval(2, 3)
    t.update([interval])
    assert len(t) == 2
    assert sorted(t)[1] == interval

    t = IntervalTree(s)
    t.extend([interval])
    assert len(t) == 2
    assert sorted(t)[1] == interval


def test_union_operator():
    t = IntervalTree()
    interval = Interval(0, 1)
    s = set([interval])

    # currently runs fine
    # with pytest.raises(TypeError):
    #     t | list(s)
    r = t | IntervalTree(s)
    assert len(r) == 1
    assert sorted(r)[0] == interval

    # also currently runs fine
    # with pytest.raises(TypeError):
    #     t |= s
    t |= IntervalTree(s)
    assert len(t) == 1
    assert sorted(t)[0] == interval


def test_invalid_union():
    t = IntervalTree()

    with pytest.raises(ValueError):
        t.union([Interval(1, 0)])


def test_invalid_update():
    t = IntervalTree()

    with pytest.raises(ValueError):
        t.update([Interval(1, 1)])


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
