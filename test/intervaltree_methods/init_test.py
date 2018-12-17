"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, initialization methods

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


def test_invalid_interval_init():
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


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
