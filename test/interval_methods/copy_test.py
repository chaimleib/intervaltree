from intervaltree import Interval
import pickle

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


def test_copy_type():
    class MyInterval(Interval):
        pass
    iv = MyInterval(1, 2)
    c = iv.copy()
    assert isinstance(c, MyInterval)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
