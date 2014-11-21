from intervaltree import Interval, IntervalTree
from numpy import sort
from numpy.random import randint

from pprint import pprint

def random_pairs(n_pairs):
    tmp = sort(randint(1000, size=2*n_pairs))
    starts = tmp[::2]
    stops = tmp[1::2]
    intervals = zip(starts, stops)
    return intervals

def pairs_to_intervals(pairs):
    interval_objs = [Interval(start, stop) for start,stop in pairs]
    return interval_objs

def test_interval_tree(n_intervals):
    intervals = random_pairs(n_intervals)
    try:
        interval_objs = pairs_to_intervals(intervals)
    except Exception as e:
        print(">>> interval_objs")
        pprint(interval_objs)
        raise e

    try:
        tree = IntervalTree(interval_objs)
    except Exception as e:
        print(">>> tree")
        pprint(interval_objs)
        for iv in interval_objs:
            print(repr(iv))
        raise e

    return tree

t1 = test_interval_tree(10) # returns tree
pprint(t1)

t2 = test_interval_tree(50) # returns RuntimeError
pprint(t2)