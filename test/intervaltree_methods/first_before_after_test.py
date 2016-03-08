from __future__ import absolute_import
from intervaltree import Interval, IntervalTree
import pytest
from test.intervaltrees import trees, sdata

def test_first_after():
    t = trees['ivs1']()
    assert t.first_after(7) in [
            Interval(8, 10, '[8,10)'),
            Interval(8, 15, '[8,15)'),
            ]
    assert t.first_after(8) in [
            Interval(8, 10, '[8,10)'),
            Interval(8, 15, '[8,15)'),
            ]
    assert t.first_after(13) == Interval(14, 15, '[14,15)')
    assert t.first_after(4) == Interval(4, 7, '[4,7)')
    assert t.first_after(5) == Interval(5, 9, '[5,9)')

def test_first_before():
    t = trees['ivs1']()
    assert t.first_before(5) == Interval(1, 2, '[1,2)')
    assert t.first_before(7) == Interval(4, 7, '[4,7)')
    assert t.first_before(10) in [
            Interval(6, 10, '[6,10)'),
            Interval(8, 10, '[8,10)'),
            ]
    assert t.first_before(15) == Interval(14, 15, '[14,15)')

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
