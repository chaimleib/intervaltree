"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, tree balance invariant after bulk construction
Submitted as issue #135 (specific intervals cause inbalanced nodes)

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


# The exact set of intervals from the issue report that, when built
# into a tree at once, left the root node with balance +2 (its left
# subtree was entirely pruned away by the rotation promotees logic,
# but the node was only refresh_balance()'d, never re-balanced).
ISSUE135_INTERVALS = [
    (478019, 486075),
    (478041, 483497),
    (478215, 486619),
    (478416, 488227),
    (479107, 483366),
    (479112, 488300),
    (479867, 489663),
    (481266, 490406),
    (482870, 485066),
    (483050, 487543),
    (484692, 485957),
    (488408, 489859),
    (490057, 492197),
    (491277, 493556),
]


def test_bulk_construction_is_balanced():
    # regression: building this set at once raised
    #   AssertionError: Error: Rotation should have happened, but didn't!
    t = IntervalTree.from_tuples(ISSUE135_INTERVALS)
    t.verify()
    # and no interval was lost in the process
    assert sorted(t) == sorted(Interval(*iv) for iv in ISSUE135_INTERVALS)


def test_sequential_add_is_balanced():
    # the same intervals added one at a time must also stay balanced
    t = IntervalTree()
    for iv in ISSUE135_INTERVALS:
        t.addi(iv[0], iv[1])
        t.verify()
    assert sorted(t) == sorted(Interval(*iv) for iv in ISSUE135_INTERVALS)


if __name__ == "__main__":
    test_bulk_construction_is_balanced()
    test_sequential_add_is_balanced()
