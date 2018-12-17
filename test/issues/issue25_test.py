"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, insertion and removal of float intervals
Submitted as issue #25 (Incorrect KeyError) by sciencectn

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
    t.addi(6.37,11.37)
    t.verify()
    t.addi(12.09,17.09)
    t.verify()
    t.addi(5.68,11.58)
    t.verify()
    t.removei(6.37,11.37)
    t.verify()
    t.addi(13.23,18.23)
    t.verify()
    t.removei(12.09,17.09)
    t.verify()
    t.addi(4.29,8.29)
    t.verify()
    t.removei(13.23,18.23)
    t.verify()
    t.addi(12.04,17.04)
    t.verify()
    t.addi(9.39,13.39)
    t.verify()
    t.removei(5.68,11.58)
    t.verify()
    t.removei(4.29,8.29)
    t.verify()
    t.removei(12.04,17.04)
    t.verify()
    t.addi(5.66,9.66)     # Value inserted here
    t.verify()
    t.addi(8.65,13.65)
    t.verify()
    t.removei(9.39,13.39)
    t.verify()
    t.addi(16.49,20.83)
    t.verify()
    t.addi(11.42,16.42)
    t.verify()
    t.addi(5.38,10.38)
    t.verify()
    t.addi(3.57,9.47)
    t.verify()
    t.removei(8.65,13.65)
    t.verify()
    t.removei(5.66,9.66)    # Deleted here
    t.verify()


def test_structure():
    """
    Reconstruct the original tree just before the final removals,
    then perform the removals. This is needed because with future
    code changes, the above sequences may not exactly reproduce the
    internal structure of the tree.
    """
    t = IntervalTree.from_tuples(data.issue25_orig.data)
    # t.print_structure()
    t.verify()

    t.removei(8.65, 13.65)  # remove root node
    # t.print_structure()
    t.verify()

    t.removei(5.66, 9.66)
    # t.print_structure()
    t.verify()

    t.removei(5.38, 10.38)  # try removing root node again
    # t.print_structure()
    t.verify()


if __name__ == "__main__":
    # pytest.main([__file__, '-v'])
    test_structure()
