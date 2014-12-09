"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: Intervals

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

from intervaltree import Interval
from pprint import pprint
import pickle


def test_isnull():
    iv = Interval(0, 0)
    assert iv.is_null()

    iv = Interval(1, 0)
    assert iv.is_null()


def test_copy():
    iv0 = Interval(1, 2, 3)
    iv1 = iv0.copy()
    assert iv1.begin == iv0.begin
    assert iv1.end == iv0.end
    assert iv1.data == iv0.data
    assert iv1 == iv0

    iv2 = pickle.loads(pickle.dumps(iv0))
    assert iv2.begin == iv0.begin
    assert iv2.end == iv0.end
    assert iv2.data == iv0.data
    assert iv2 == iv0


def test_len():
    iv = Interval(0, 0)
    assert len(iv) == 3

    iv = Interval(0, 1, 2)
    assert len(iv) == 3

    iv = Interval(1.3, 2.2)
    assert len(iv) == 3


def test_length():
    iv = Interval(0, 0)
    assert iv.length() == 0

    iv = Interval(0, 3)
    assert iv.length() == 3

    iv = Interval(-1, 1, 'data')
    assert iv.length() == 2

    iv = Interval(0.1, 3)
    assert iv.length() == 2.9
