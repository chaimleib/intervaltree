from intervaltree import Interval, IntervalTree
from pprint import pprint

def optimality():
    def make_interval(lst):
        return Interval(lst[0], lst[1], "{0}-{1}".format(*lst))

    ivs = [make_interval(iv) for iv in [
        [1, 2],
        [4, 7],
        [5, 9],
        [6, 10],
        [8, 10],
        [8, 15],
        [10, 12],
        [12, 14],
        [14, 15],
    ]]
    t = IntervalTree(ivs)
    t.print_structure()
    pprint(t.score(True), width=20)


if __name__ == "__main__":
    optimality()
