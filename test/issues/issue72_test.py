"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, remove_overlap caused incorrect balancing
where intervals overlapping an ancestor's x_center were buried too deep.
Submitted as issue #72 (KeyError raised after calling remove_overlap)
by alexandersoto

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
from intervaltree import IntervalTree, Interval
import pytest

def test_interval_removal_72():
    tree = IntervalTree([
        Interval(0.0, 2.588, 841),
        Interval(65.5, 85.8, 844),
        Interval(93.6, 130.0, 837),
        Interval(125.0, 196.5, 829),
        Interval(391.8, 521.0, 825),
        Interval(720.0, 726.0, 834),
        Interval(800.0, 1033.0, 850),
        Interval(800.0, 1033.0, 855),
    ])
    tree.verify()
    tree.remove_overlap(0.0, 521.0)
    tree.verify()
    
