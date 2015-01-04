"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: Intervals

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


def test_interval_overlaps_interval():
    iv0 = Interval(0, 10)
    iv1 = Interval(-10, -5)
    iv2 = Interval(-10, 0)
    iv3 = Interval(-10, 5)
    iv4 = Interval(-10, 10)
    iv5 = Interval(-10, 20)
    iv6 = Interval(0, 20)
    iv7 = Interval(5, 20)
    iv8 = Interval(10, 20)
    iv9 = Interval(15, 20)

    assert iv0.overlaps(iv0)
    assert not iv0.overlaps(iv1)
    assert not iv0.overlaps(iv2)
    assert iv0.overlaps(iv3)
    assert iv0.overlaps(iv4)
    assert iv0.overlaps(iv5)
    assert iv0.overlaps(iv6)
    assert iv0.overlaps(iv7)
    assert not iv0.overlaps(iv8)
    assert not iv0.overlaps(iv9)


def test_interval_overlaps_point():
    iv = Interval(0, 10)

    assert not iv.overlaps(-5)
    assert iv.overlaps(0)
    assert iv.overlaps(5)
    assert not iv.overlaps(10)
    assert not iv.overlaps(15)


def test_interval_overlaps_range():
    iv0 = Interval(0, 10)
    iv1 = (-10, -5)
    iv2 = (-10, 0)
    iv3 = (-10, 5)
    iv4 = (-10, 10)
    iv5 = (-10, 20)
    iv6 = (0, 20)
    iv7 = (5, 20)
    iv8 = (10, 20)
    iv9 = (15, 20)

    assert iv0.overlaps(iv0)
    assert not iv0.overlaps(*iv1)
    assert not iv0.overlaps(*iv2)
    assert iv0.overlaps(*iv3)
    assert iv0.overlaps(*iv4)
    assert iv0.overlaps(*iv5)
    assert iv0.overlaps(*iv6)
    assert iv0.overlaps(*iv7)
    assert not iv0.overlaps(*iv8)
    assert not iv0.overlaps(*iv9)

def test_interval_int_comparison_operators():
    iv = Interval(0, 10)

    assert (iv > -5)
    assert (-5 < iv)
    assert not (iv < -5)
    assert not (-5 > iv)

    assert (iv > 0)  # special for sorting
    assert (0 < iv)  # special for sorting
    assert not (iv < 0)
    assert not (0 > iv)

    assert not (iv > 5)
    assert not (5 < iv)
    assert (iv < 5)  # special for sorting
    assert (5 > iv)  # special for sorting

    assert not (iv > 10)
    assert not (10 < iv)
    assert (iv < 10)
    assert (10 > iv)

    assert not (iv > 15)
    assert not (15 < iv)
    assert (iv < 15)
    assert (15 > iv)


def test_interval_int_comparison_methods():
    iv = Interval(0, 10)

    assert iv.gt(-5)
    assert iv.ge(-5)
    assert not iv.lt(-5)
    assert not iv.le(-5)

    assert not iv.gt(0)
    assert iv.ge(0)
    assert not iv.lt(0)
    assert not iv.le(0)

    assert not iv.gt(5)
    assert not iv.ge(5)
    assert not iv.lt(5)
    assert not iv.le(5)

    assert not iv.gt(10)
    assert not iv.ge(10)
    assert iv.lt(10)
    assert iv.le(10)

    assert not iv.gt(15)
    assert not iv.ge(15)
    assert iv.lt(15)
    assert iv.le(15)


def test_interval_cmp_interval():
    iv0 = Interval(0, 10)
    iv1 = Interval(-10, -5)
    iv2 = Interval(-10, 0)
    iv3 = Interval(-10, 5)
    iv4 = Interval(-10, 10)
    iv5 = Interval(-10, 20)
    iv6 = Interval(0, 20)
    iv7 = Interval(5, 20)
    iv8 = Interval(10, 20)
    iv9 = Interval(15, 20)

    assert iv0.__cmp__(iv0) == 0
    assert iv0.__cmp__(iv1) == 1
    assert iv0.__cmp__(iv2) == 1
    assert iv0.__cmp__(iv3) == 1
    assert iv0.__cmp__(iv4) == 1
    assert iv0.__cmp__(iv5) == 1
    assert iv0.__cmp__(iv6) == -1
    assert iv0.__cmp__(iv7) == -1
    assert iv0.__cmp__(iv8) == -1
    assert iv0.__cmp__(iv9) == -1


def test_interval_cmp_int():
    iv = Interval(0, 10)

    assert iv.__cmp__(-5) == 1
    assert iv.__cmp__(0) == 1
    assert iv.__cmp__(5) == -1
    assert iv.__cmp__(10) == -1
    assert iv.__cmp__(15) == -1


def test_interval_sort_interval():
    base = Interval(0, 10)
    ivs = [
        Interval(-10, -5),
        Interval(-10, 0),
        Interval(-10, 5),
        Interval(-10, 10),
        Interval(-10, 20),
        Interval(0, 20),
        Interval(5, 20),
        Interval(10, 20),
        Interval(15, 20),
    ]

    for iv in ivs:
        sort = sorted([base, iv])
        assert sort[0].__cmp__(sort[1]) in (-1, 0)

        sort = sorted([iv, base])
        assert sort[0].__cmp__(sort[1]) in (-1, 0)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
