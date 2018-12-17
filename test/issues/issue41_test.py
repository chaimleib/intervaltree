"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, removal of intervals
Submitted as issue #41 (Interval removal breaks this tree) by escalonn

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
from intervaltree import IntervalTree
from test import data
import pytest


def test_sequence():
    t = IntervalTree()
    t.addi(860, 917, 1)
    t.verify()
    t.addi(860, 917, 2)
    t.verify()
    t.addi(860, 917, 3)
    t.verify()
    t.addi(860, 917, 4)
    t.verify()
    t.addi(871, 917, 1)
    t.verify()
    t.addi(871, 917, 2)
    t.verify()
    t.addi(871, 917, 3)     # Value inserted here
    t.verify()
    t.addi(961, 986, 1)
    t.verify()
    t.addi(1047, 1064, 1)
    t.verify()
    t.addi(1047, 1064, 2)
    t.verify()
    t.removei(961, 986, 1)
    t.verify()
    t.removei(871, 917, 3)  # Deleted here
    t.verify()


def test_structure():
    """
    Reconstruct the original tree just before the removals, then
    perform the removals.
    """
    t = data.issue41_orig.tree()
    t.verify()

    t.removei(961, 986, 1)
    t.verify()

    t.removei(871, 917, 3)
    t.verify()


if __name__ == "__main__":
    # pytest.main([__file__, '-v'])
    test_structure()
