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
from test.intervaltrees import trees
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_invalid_union():
    t = IntervalTree()

    with pytest.raises(ValueError):
        t.union([Interval(1, 0)])

    with pytest.raises(ValueError):
        t.union([Interval(1, 1)])

    with pytest.raises(ValueError):
        t.extend([Interval(1, 0)])

    with pytest.raises(ValueError):
        t.extend([Interval(1, 1)])


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
