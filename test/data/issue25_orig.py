"""
Manually create the original tree that revealed the bug. I have to
do this, since with later code changes, the original sequence of
insertions and removals might not recreate that tree exactly, with
the same internal structure.

Node<10.58, depth=3, balance=1>
 Interval(8.65, 13.65)
<:  Node<5.66, depth=1, balance=0>
     Interval(3.57, 9.47)
     Interval(5.38, 10.38)
     Interval(5.66, 9.66)
>:  Node<16.49, depth=2, balance=-1>
     Interval(16.49, 20.83)
    <:  Node<11.42, depth=1, balance=0>
         Interval(11.42, 16.42)
"""
from intervaltree import IntervalTree, Interval
from intervaltree.node import Node

data = [
    (8.65, 13.65),  #0
    (3.57, 9.47),   #1
    (5.38, 10.38),  #2
    (5.66, 9.66),   #3
    (16.49, 20.83), #4
    (11.42, 16.42), #5
]

def tree():
    t = IntervalTree.from_tuples(data)
    # Node<10.58, depth=3, balance=1>
    #  Interval(8.65, 13.65)
    root = Node()
    root.x_center = 10.58
    root.s_center = set([Interval(*data[0])])
    root.depth = 3
    root.balance = 1

    # <:  Node<5.66, depth=1, balance=0>
    #      Interval(3.57, 9.47)
    #      Interval(5.38, 10.38)
    #      Interval(5.66, 9.66)
    n = root.left_node = Node()
    n.x_center = 5.66
    n.s_center = set(Interval(*tup) for tup in data[1:4])
    n.depth = 1
    n.balance = 0

    # >:  Node<16.49, depth=2, balance=-1>
    #      Interval(16.49, 20.83)
    n = root.right_node = Node()
    n.x_center = 16.49
    n.s_center = set([Interval(*data[4])])
    n.depth = 2
    n.balance = -1

    #     <:  Node<11.42, depth=1, balance=0>
    #          Interval(11.42, 16.42)
    n.left_node = Node()
    n = n.left_node
    n.x_center = 11.42
    n.s_center = set([Interval(*data[5])])
    n.depth = 1
    n.balance = 0

    structure = root.print_structure(tostring=True)
    # root.print_structure()
    assert structure == """\
Node<10.58, depth=3, balance=1>
 Interval(8.65, 13.65)
<:  Node<5.66, depth=1, balance=0>
     Interval(3.57, 9.47)
     Interval(5.38, 10.38)
     Interval(5.66, 9.66)
>:  Node<16.49, depth=2, balance=-1>
     Interval(16.49, 20.83)
    <:  Node<11.42, depth=1, balance=0>
         Interval(11.42, 16.42)
"""
    t.top_node = root
    t.verify()
    return t

if __name__ == "__main__":
    tree().print_structure()
