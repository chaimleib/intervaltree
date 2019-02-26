"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: Intervals, methods on two intervals

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

from intervaltree import Interval
from pprint import pprint
import pickle

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
iv10 = Interval(-5, 0)


def test_interval_overlaps_size_interval():
    assert iv0.overlap_size(iv0) == 10
    assert not iv0.overlap_size(iv1)
    assert not iv0.overlap_size(iv2)
    assert iv0.overlap_size(iv3) == 5
    assert iv0.overlap_size(iv4) == 10
    assert iv0.overlap_size(iv5) == 10
    assert iv0.overlap_size(iv6) == 10
    assert iv0.overlap_size(iv7) == 5
    assert not iv0.overlap_size(iv8)
    assert not iv0.overlap_size(iv9)


def test_interval_overlap_interval():
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


def test_contains_interval():
    assert iv0.contains_interval(iv0)
    assert not iv0.contains_interval(iv1)
    assert not iv0.contains_interval(iv2)
    assert not iv0.contains_interval(iv3)
    assert not iv0.contains_interval(iv4)
    assert not iv0.contains_interval(iv5)
    assert not iv0.contains_interval(iv6)
    assert not iv0.contains_interval(iv7)
    assert not iv0.contains_interval(iv8)
    assert not iv0.contains_interval(iv9)
    assert not iv0.contains_interval(iv10)

    assert not iv2.contains_interval(iv0)
    assert iv2.contains_interval(iv1)
    assert iv2.contains_interval(iv2)
    assert not iv2.contains_interval(iv3)
    assert not iv2.contains_interval(iv4)
    assert not iv2.contains_interval(iv5)
    assert not iv2.contains_interval(iv6)
    assert not iv2.contains_interval(iv7)
    assert not iv2.contains_interval(iv8)
    assert not iv2.contains_interval(iv9)
    assert iv2.contains_interval(iv10)


def test_distance_to_interval():
    assert iv0.distance_to(iv0) == 0
    assert iv0.distance_to(iv1) == 5
    assert iv0.distance_to(iv2) == 0
    assert iv0.distance_to(iv3) == 0
    assert iv0.distance_to(iv4) == 0
    assert iv0.distance_to(iv5) == 0
    assert iv0.distance_to(iv6) == 0
    assert iv0.distance_to(iv7) == 0
    assert iv0.distance_to(iv8) == 0
    assert iv0.distance_to(iv9) == 5
    assert iv0.distance_to(iv10) == 0


def test_distance_to_point():
    assert iv0.distance_to(-5) == 5
    assert iv0.distance_to(0) == 0
    assert iv0.distance_to(5) == 0
    assert iv0.distance_to(10) == 0
    assert iv0.distance_to(15) == 5


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
