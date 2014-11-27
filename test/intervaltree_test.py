"""
PyIntervalTree: A mutable, self-balancing interval tree.

Test module

Copyright 2013-2014 Chaim-Leib Halbert

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

from intervaltree import Interval, IntervalTree
from pprint import pprint
import pickle


def test_empty_init():
    tree = IntervalTree()
    tree.verify()
    assert not tree
    assert len(tree) == 0
    assert list(tree) == []


def test_list_init():
    tree = IntervalTree([Interval(-10, 10), Interval(-20.0, -10.0)])
    tree.verify()
    assert tree
    assert len(tree) == 2
    assert tree.items() == set([Interval(-10, 10), Interval(-20.0, -10.0)])


def test_generator_init():
    tree = IntervalTree(
        Interval(begin, end) for begin, end in
        [(-10, 10), (-20, -10), (10, 20)]
    )
    tree.verify()
    assert tree
    assert len(tree) == 3
    assert tree.items() == set([
        Interval(-20, -10),
        Interval(-10, 10),
        Interval(10, 20),
    ])


def test_duplicate_insert():
    tree = IntervalTree()

    ## string data
    tree[-10:20] = "arbitrary data"
    assert len(tree) == 1
    assert tree.items() == set([Interval(-10, 20, "arbitrary data")])

    tree.addi(-10, 20, "arbitrary data")
    assert len(tree) == 1
    assert tree.items() == set([Interval(-10, 20, "arbitrary data")])

    tree.add(Interval(-10, 20, "arbitrary data"))
    assert len(tree) == 1
    assert tree.items() == set([Interval(-10, 20, "arbitrary data")])

    tree.extend([Interval(-10, 20, "arbitrary data")])
    assert len(tree) == 1
    assert tree.items() == set([Interval(-10, 20, "arbitrary data")])

    ## None data
    tree[-10:20] = None
    assert len(tree) == 2
    assert tree.items() == set([
        Interval(-10, 20),
        Interval(-10, 20, "arbitrary data"),
    ])

    tree.addi(-10, 20)
    assert len(tree) == 2
    assert tree.items() == set([
        Interval(-10, 20),
        Interval(-10, 20, "arbitrary data"),
    ])

    tree.add(Interval(-10, 20))
    assert len(tree) == 2
    assert tree.items() == set([
        Interval(-10, 20),
        Interval(-10, 20, "arbitrary data"),
    ])

    tree.extend([Interval(-10, 20)])
    assert len(tree) == 2
    assert tree.items() == set([
        Interval(-10, 20),
        Interval(-10, 20, "arbitrary data"),
    ])



def test_empty_queries():
    t = IntervalTree()
    e = set()

    assert len(t) == 0
    assert t.is_empty()
    assert t[3] == e
    assert t[4:6] == e
    assert t.begin() == 0
    assert t.end() == 0
    assert t[t.begin():t.end()] == e
    assert t.items() == e
    assert set(t) == e
    assert set(t.copy()) == e
    assert t.find_nested() == {}
    t.verify()


def test_copy():
    itree = IntervalTree([Interval(0, 1, "x"), Interval(1, 2, ["x"])])
    itree.verify()

    itree2 = IntervalTree(itree)  # Shares Interval objects
    itree2.verify()

    itree3 = itree.copy()         # Shallow copy (same as above, as Intervals are singletons)
    itree3.verify()

    itree4 = pickle.loads(pickle.dumps(itree))  # Deep copy
    itree4.verify()

    list(itree[1])[0].data[0] = "y"
    assert sorted(itree) == [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
    assert sorted(itree2) == [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
    assert sorted(itree3) == [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
    assert sorted(itree4) == [Interval(0, 1, 'x'), Interval(1, 2, ['x'])]


def sdata(s):
    return set(iv.data for iv in s)


def test_all():
    def make_interval(lst):
        return Interval(lst[0], lst[1], "{0}-{1}".format(*lst))
    
    ivs = list(map(make_interval, [
        [1, 2],
        [4, 7],
        [5, 9],
        [6, 10],
        [8, 10],
        [8, 15],
        [10, 12],
        [12, 14],
        [14, 15],
    ]))
    t = IntervalTree(ivs)
    t.verify()
    orig = t.print_structure(True)
        
    assert orig == """
Node<8, balance=0>
 Interval(5, 9, '5-9')
 Interval(6, 10, '6-10')
 Interval(8, 10, '8-10')
 Interval(8, 15, '8-15')
<:  Node<4, balance=-1>
     Interval(4, 7, '4-7')
    <:  Node<1, balance=0>
         Interval(1, 2, '1-2')
>:  Node<12, balance=0>
     Interval(12, 14, '12-14')
    <:  Node<10, balance=0>
         Interval(10, 12, '10-12')
    >:  Node<14, balance=0>
         Interval(14, 15, '14-15')
"""[1:]
    
    # Query tests
    print('Query tests...')
    assert sdata(t[4]) == set(['4-7'])
    assert sdata(t[4:5]) == set(['4-7'])
    assert sdata(t[4:6]) == set(['4-7', '5-9'])
    assert sdata(t[9]) == set(['6-10', '8-10', '8-15'])
    assert sdata(t[15]) == set()
    assert sdata(t.search(5)) == set(['4-7', '5-9'])
    assert sdata(t.search(6, 11, strict=True)) == set(['6-10', '8-10'])
    
    print('    passed')
    
    # Membership tests
    print('Membership tests...')
    assert ivs[1] in t
    assert Interval(1, 3, '1-3') not in t
    assert t.overlaps(4)
    assert t.overlaps(9)
    assert not t.overlaps(15)
    assert t.overlaps(0, 4)
    assert t.overlaps(1, 2)
    assert t.overlaps(1, 3)
    assert t.overlaps(8, 15)
    assert not t.overlaps(15, 16)
    assert not t.overlaps(-1, 0)
    assert not t.overlaps(2, 4)
    print('    passed')
    
    # Insertion tests
    print('Insertion tests...')
    t.add(make_interval([1, 2]))  # adding duplicate should do nothing
    assert sdata(t[1]) == set(['1-2'])
    assert orig == t.print_structure(True)
    
    t[1:2] = '1-2'                # adding duplicate should do nothing
    assert sdata(t[1]) == set(['1-2'])
    assert orig == t.print_structure(True)
    
    t.add(make_interval([2, 4]))
    assert sdata(t[2]) == set(['2-4'])
    t.verify()
    
    t[13:15] = '13-15'
    assert sdata(t[14]) == set(['8-15', '13-15', '14-15'])
    t.verify()
    print('    passed')
    
    # Duplication tests
    print('Interval duplication tests...')
    t.add(Interval(14, 15, '14-15####'))
    assert sdata(t[14]) == set(['8-15', '13-15', '14-15', '14-15####'])
    t.verify()
    print('    passed')
    
    # Copying and casting
    print('Tree copying and casting...')
    tcopy = IntervalTree(t)
    tcopy.verify()
    assert t == tcopy
    
    tlist = list(t)
    for iv in tlist:
        assert iv in t
    for iv in t:
        assert iv in tlist
    
    tset = set(t)
    assert tset == t.items()
    print('    passed')
    
    # Deletion tests
    print('Deletion tests...')
    try:
        t.remove(Interval(1, 3, "Doesn't exist"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
    
    try:
        t.remove(Interval(500, 1000, "Doesn't exist"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
    
    orig = t.print_structure(True)
    t.discard(Interval(1, 3, "Doesn't exist"))
    t.discard(Interval(500, 1000, "Doesn't exist"))
    assert orig == t.print_structure(True)
    
    assert sdata(t[14]) == set(['8-15', '13-15', '14-15', '14-15####'])
    t.remove(Interval(14, 15, '14-15####'))
    assert sdata(t[14]) == set(['8-15', '13-15', '14-15'])
    t.verify()
    
    assert sdata(t[2]) == set(['2-4'])
    t.discard(make_interval([2, 4]))
    assert sdata(t[2]) == set()
    t.verify()
    
    assert t[14]
    t.remove_overlap(14)
    t.verify()
    assert not t[14]
    
    # Emptying the tree
    #t.print_structure()
    for iv in sorted(iter(t)):
        #print('### Removing '+str(iv)+'... ###')
        t.remove(iv)
        #t.print_structure()
        t.verify()
        #print('')
    assert len(t) == 0
    assert t.is_empty()
    assert not t
    
    t = IntervalTree(ivs)
    #t.print_structure()
    t.remove_overlap(1)
    #t.print_structure()
    t.verify()
    
    t.remove_overlap(8)
    #t.print_structure()    
    print('    passed')

    print('Split overlaps...')
    t = IntervalTree(ivs)
    pprint(t)
    t.split_overlaps()
    pprint(t)
    #import cPickle as pickle
    #p = pickle.dumps(t)
    #print(p)
