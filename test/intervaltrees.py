from __future__ import absolute_import
from intervaltree import Interval, IntervalTree
from pprint import pprint
from random import randint, choice
try:
    xrange
except NameError:
    xrange = range

def make_iv(begin, end, label=False):
    if label:
        return Interval(begin, end, "[{0},{1})".format(begin, end))
    else:
        return Interval(begin, end)

def nogaps_rand(size=100, labels=False):
    cur = -50
    ivs = []
    for i in xrange(size):
        length = randint(1, 10)
        ivs.append(make_iv(cur, cur+length, labels))
        cur += length
    return IntervalTree(ivs)

def gaps_rand(size=100, labels=False):
    cur = -50
    ivs = []
    for i in xrange(size):
        length = randint(1, 10)
        if choice([True, False]):
            cur += length
            length = randint(1, 10)
        ivs.append(make_iv(cur, cur+length, labels))
        cur += length
    return IntervalTree(ivs)


if __name__ == "__main__":
    pprint(gaps_rand(labels=False))