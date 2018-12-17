"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, insertion and removal of float intervals
Submitted as issue #26 (Pop from empty list error) by sciencectn
Ensure that rotations that promote Intervals prune when necessary

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
from intervaltree import IntervalTree, Interval
# from test.intervaltrees import trees
import pytest


def test_original_sequence():
    t = IntervalTree()
    t.addi(17.89,21.89)
    t.addi(11.53,16.53)
    t.removei(11.53,16.53)
    t.removei(17.89,21.89)
    t.addi(-0.62,4.38)
    t.addi(9.24,14.24)
    t.addi(4.0,9.0)
    t.removei(-0.62,4.38)
    t.removei(9.24,14.24)
    t.removei(4.0,9.0)
    t.addi(12.86,17.86)
    t.addi(16.65,21.65)
    t.removei(12.86,17.86)


def test_debug_sequence():
    t = IntervalTree()
    t.verify()
    t.addi(17.89,21.89)
    t.verify()
    t.addi(11.53,16.53)
    t.verify()
    t.removei(11.53,16.53)
    t.verify()
    t.removei(17.89,21.89)
    t.verify()
    t.addi(-0.62,4.38)
    t.verify()
    t.addi(9.24,14.24)
    # t.print_structure()
    # Node<-0.62, depth=2, balance=1>
    #  Interval(-0.62, 4.38)
    # >:  Node<9.24, depth=1, balance=0>
    #      Interval(9.24, 14.24)
    t.verify()

    t.addi(4.0,9.0)  # This line breaks the invariants, leaving an empty node
    # t.print_structure()
    t.verify()
    t.removei(-0.62,4.38)
    t.verify()
    t.removei(9.24,14.24)
    t.verify()
    t.removei(4.0,9.0)
    t.verify()
    t.addi(12.86,17.86)
    t.verify()
    t.addi(16.65,21.65)
    t.verify()
    t.removei(12.86,17.86)


def test_minimal_sequence():
    t = IntervalTree()
    t.addi(-0.62, 4.38)  # becomes root
    t.addi(9.24, 14.24)  # right child

    ## Check that the tree structure is like this:
    # t.print_structure()
    # Node<-0.62, depth=2, balance=1>
    #  Interval(-0.62, 4.38)
    # >:  Node<9.24, depth=1, balance=0>
    #      Interval(9.24, 14.24)
    root = t.top_node
    assert root.s_center == set([Interval(-0.62, 4.38)])
    assert root.right_node.s_center == set([Interval(9.24, 14.24)])
    assert not root.left_node

    t.verify()

    # This line left an empty node when drotate() failed to promote
    # Intervals properly:
    t.addi(4.0, 9.0)
    t.print_structure()
    t.verify()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
