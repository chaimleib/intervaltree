from intervaltree import Interval

def test_str():
    iv = Interval(0, 1)
    s = str(iv)
    assert s == 'Interval(0, 1)'
    assert repr(iv) == s

    iv = Interval(0, 1, '[0,1)')
    s = str(iv)
    assert s == "Interval(0, 1, '[0,1)')"
    assert repr(iv) == s

    iv = Interval((1,2), (3,4))
    s = str(iv)
    assert s == 'Interval((1, 2), (3, 4))'
    assert repr(iv) == s

    iv = Interval((1,2), (3,4), (5, 6))
    s = str(iv)
    assert s == 'Interval((1, 2), (3, 4), (5, 6))'
    assert repr(iv) == s


def test_str_type():
    class MyInterval(Interval):
        pass

    iv = MyInterval(0, 1)
    s = str(iv)
    assert s == 'MyInterval(0, 1)'
    assert repr(iv) == s

    iv = MyInterval(0, 1, '[0,1)')
    s = str(iv)
    assert s == "MyInterval(0, 1, '[0,1)')"
    assert repr(iv) == s

    iv = MyInterval((1,2), (3,4))
    s = str(iv)
    assert s == 'MyInterval((1, 2), (3, 4))'
    assert repr(iv) == s

    iv = MyInterval((1,2), (3,4), (5, 6))
    s = str(iv)
    assert s == 'MyInterval((1, 2), (3, 4), (5, 6))'
    assert repr(iv) == s


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
