"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Copying

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
from test import data
try:
    import cPickle as pickle
except ImportError:
    import pickle


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


def test_copy_cast():
    t = IntervalTree.from_tuples(data.ivs1.data)

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


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
