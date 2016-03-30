"""
Manually create the original tree that revealed the bug. I have to
do this, since with later code changes, the original sequence of
insertions and removals might not recreate that tree exactly, with
the same internal structure.

Node<961, depth=2, balance=0>
 Interval(961, 986, 1)
<:  Node<871, depth=1, balance=0>
     Interval(860, 917, 1)
     Interval(860, 917, 2)
     Interval(860, 917, 3)
     Interval(860, 917, 4)
     Interval(871, 917, 1)
     Interval(871, 917, 2)
     Interval(871, 917, 3)
>:  Node<1047, depth=1, balance=0>
     Interval(1047, 1064, 1)
     Interval(1047, 1064, 2)
"""
from intervaltree import IntervalTree, Interval
from intervaltree.node import Node

data = [
    (860, 917, 1),   #0
    (860, 917, 2),   #1
    (860, 917, 3),   #2
    (860, 917, 4),   #3
    (871, 917, 1),   #4
    (871, 917, 2),   #5
    (871, 917, 3),   #6
    (961, 986, 1),   #7
    (1047, 1064, 1), #8
    (1047, 1064, 2), #9
]

def tree():
    t = IntervalTree.from_tuples(data)
    # Node<961, depth=2, balance=0>
    #  Interval(961, 986, 1)
    root = Node()
    root.x_center = 961
    root.s_center = set([Interval(*data[7])])
    root.depth = 2
    root.balance = 0

    # <:  Node<871, depth=1, balance=0>
    #      Interval(860, 917, 1)
    #      Interval(860, 917, 2)
    #      Interval(860, 917, 3)
    #      Interval(860, 917, 4)
    #      Interval(871, 917, 1)
    #      Interval(871, 917, 2)
    #      Interval(871, 917, 3)
    n = root.left_node = Node()
    n.x_center = 871
    n.s_center = set(Interval(*tup) for tup in data[:7])
    n.depth = 1
    n.balance = 0

    # >:  Node<1047, depth=1, balance=0>
    #      Interval(1047, 1064, 1)
    #      Interval(1047, 1064, 2)
    n = root.right_node = Node()
    n.x_center = 1047
    n.s_center = set(Interval(*tup) for tup in data[8:])
    n.depth = 1
    n.balance = 0

    structure = root.print_structure(tostring=True)
    # root.print_structure()
    assert structure == """\
Node<961, depth=2, balance=0>
 Interval(961, 986, 1)
<:  Node<871, depth=1, balance=0>
     Interval(860, 917, 1)
     Interval(860, 917, 2)
     Interval(860, 917, 3)
     Interval(860, 917, 4)
     Interval(871, 917, 1)
     Interval(871, 917, 2)
     Interval(871, 917, 3)
>:  Node<1047, depth=1, balance=0>
     Interval(1047, 1064, 1)
     Interval(1047, 1064, 2)
"""
    t.top_node = root
    t.verify()
    return t

if __name__ == "__main__":
    tree().print_structure()
