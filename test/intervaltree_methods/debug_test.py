"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree, Basic query methods (read-only)

Copyright 2013-2015 Chaim-Leib Halbert

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
from test.intervaltrees import trees, sdata
try:
    import cPickle as pickle
except ImportError:
    import pickle


def test_print_empty():
    t = IntervalTree()
    assert t.print_structure(True) == "<empty IntervalTree>"
    t.print_structure()

    t.verify()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
