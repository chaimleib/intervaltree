"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Basic query methods (read-only)

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
from pprint import pprint, pformat
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_print_empty():
    t = IntervalTree()
    assert t.print_structure(True) == "<empty IntervalTree>"
    t.print_structure()

    t.verify()


def test_mismatched_tree_and_membership_set():
    t = IntervalTree.from_tuples(data.ivs1.data)
    members = set(t.all_intervals)
    assert t.all_intervals == members
    t.removei(1, 2, '[1,2)')
    assert t.all_intervals != members
    t.all_intervals = members  # intentionally introduce error
    with pytest.raises(AssertionError):
        t.verify()


def test_small_tree_score():
    # inefficiency score for trees of len() <= 2 should be 0.0
    t = IntervalTree()
    assert t.score() == 0.0

    t.addi(1, 4)
    assert t.score() == 0.0

    t.addi(2, 5)
    assert t.score() == 0.0

    t.addi(1, 100)  # introduces inefficiency, b/c len(s_center) > 1
    assert t.score() != 0.0


def test_score_no_report():
    t = IntervalTree.from_tuples(data.ivs1.data)
    score = t.score(False)
    assert isinstance(score, (int, float))


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
