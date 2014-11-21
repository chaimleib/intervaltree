'''
PyIntervalTree: A mutable, self-balancing interval tree.

Core logic.

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
'''
from __future__ import absolute_import
from .interval import Interval
from numbers import Number
from operator import attrgetter

try:
    xrange  # Python 2?
except NameError:
    xrange = range

class IntervalTree(object):
    """
    A binary lookup tree of intervals.
    The intervals contained in the tree are represented using ``Interval(a, b, data)`` objects.
    Each such object represents a half-open interval ``[a, b)`` with optional data.
    
    Examples:
    ---------
    
    Initialize a blank tree::
    
        >>> itree = IntervalTree()
        >>> len(itree)
        0
    
    Initialize a tree from an iterable set of Intervals in O(n * log n)::
    
        >>> itree = IntervalTree([Interval(-10, 10), Interval(-10.0, 10.0)])
        >>> len(itree)
        1
    
    Note that this is a set, i.e. repeated intervals are ignored. However, intervals with different data fields are regarded as different::
    
        >>> itree = IntervalTree([Interval(-10, 10), Interval(-10, 10), Interval(-10, 10, "x")])
        >>> len(itree)
        2
    
    Insertions::
    
        >>> itree[-10:20] = "arbitrary data"
        >>> itree[-10:20] = None  # Note that this is also an insertion
        >>> len(itree)
        4
        >>> itree[-10:20] = None  # This won't change anything
        >>> itree[-10:20] = "arbitrary data" # Neither will this
        >>> len(itree)
        4
        >>> itree.add(Interval(10, 20))
        >>> itree.addi(19.9, 20)
        >>> len(itree)
        6
        >>> itree.extend([Interval(19.9, 20.1), Interval(20.1, 30)])
        >>> len(itree)
        8
        >>> itree.extend([Interval(19.9, 20.1), Interval(20.1, 30)]) # Note the set-like logic again
        >>> len(itree)
        8

    Deletions::
    
        >>> itree.remove(Interval(-10, 10))
        >>> len(itree)
        7
        >>> itree.remove(Interval(-10, 10))
        Traceback (most recent call last):
        ...
        ValueError
        >>> itree.discard(Interval(-10, 10)) # Same as remove, but no exception on failure
        >>> len(itree)
        7
        
    Delete intervals, overlapping a given point::
    
        >>> itree = IntervalTree([Interval(-1.1, 1.1), Interval(-0.5, 1.5), Interval(0.5, 1.7)])
        >>> itree.remove_overlap(1.1)
        >>> list(itree)
        [Interval(-1.1, 1.1)]
        
    Delete intervals, overlapping an interval::
    
        >>> itree = IntervalTree([Interval(-1.1, 1.1), Interval(-0.5, 1.5), Interval(0.5, 1.7)])
        >>> itree.remove_overlap(0, 0.5)
        >>> list(itree)
        [Interval(0.5, 1.7)]
        >>> itree.remove_overlap(1.7, 1.8)
        >>> list(itree)
        [Interval(0.5, 1.7)]
        >>> itree.remove_overlap(1.6, 1.6) # Empty interval still works
        >>> list(itree)
        []
        
    Delete intervals, enveloped in the range::
    
        >>> itree = IntervalTree([Interval(-1.1, 1.1), Interval(-0.5, 1.5), Interval(0.5, 1.7)])
        >>> itree.remove_envelop(-1.0, 1.5)
        >>> sorted(itree)
        [Interval(-1.1, 1.1), Interval(0.5, 1.7)]
        >>> itree.remove_envelop(-1.1, 1.5)
        >>> list(itree)
        [Interval(0.5, 1.7)]
        >>> itree.remove_envelop(0.5, 1.5)
        >>> list(itree)
        [Interval(0.5, 1.7)]
        >>> itree.remove_envelop(0.5, 1.7)
        >>> list(itree)
        []
        
    Point/interval overlap queries::
    
        >>> itree = IntervalTree([Interval(-1.1, 1.1), Interval(-0.5, 1.5), Interval(0.5, 1.7)])
        >>> assert itree[-1.1]         == set([Interval(-1.1, 1.1)])
        >>> assert itree.search(1.1)   == set([Interval(-0.5, 1.5), Interval(0.5, 1.7)])   # Same as [1.1]
        >>> assert itree[-0.5:0.5]     == set([Interval(-0.5, 1.5), Interval(-1.1, 1.1)])  # Interval overlap query
        >>> assert itree.search(1.5, 1.5) == set([Interval(0.5, 1.7)])                     # Same as [1.5, 1.5]
        >>> assert itree.search(1.7, 1.7) == set([])

    Envelop queries::
    
        >>> assert itree.search(-0.5, 0.5, strict=True) == set([])
        >>> assert itree.search(-0.4, 1.7, strict=True) == set([Interval(0.5, 1.7)])
        
    Membership queries::
    
        >>> Interval(-0.5, 0.5) in itree
        False
        >>> Interval(-1.1, 1.1) in itree
        True
        >>> Interval(-1.1, 1.1, "x") in itree
        False
        >>> itree.overlaps(-1.1)
        True
        >>> not itree.overlaps(1.7) # TODO: itree.overlaps(1.7) returns None, should return False
        True
        >>> itree.overlaps(1.7, 1.8)
        False
        >>> itree.overlaps(-1.2, -1.1)
        False
        >>> itree.overlaps(-1.2, -1.0)
        True
    
    Sizing::
    
        >>> len(itree)
        3
        >>> itree.is_empty()
        False
        >>> IntervalTree().is_empty()
        True
        >>> not itree
        False
        >>> not IntervalTree()
        True
        >>> print(itree.begin())    # using print() because of floats in Python 2.6
        -1.1
        >>> print(itree.end())      # ditto
        1.7
        
    Iteration::

        (Using str() because of floats in Python 2.6)
        >>> print(', '.join(str(int.begin) for int in sorted(itree)))
        -1.1, -0.5, 0.5
        >>> assert itree.items() == set([Interval(-0.5, 1.5), Interval(-1.1, 1.1), Interval(0.5, 1.7)])

    Copy- and typecasting, pickling::
    
        >>> itree = IntervalTree([Interval(0,1,"x"), Interval(1,2,["x"])])
        >>> itree2 = IntervalTree(itree) # Does not copy Interval objects
        >>> itree3 = itree.copy()        # Shallow copy of Interval objects (which is the same as above as those are singletons).
        >>> import pickle
        >>> itree4 = pickle.loads(pickle.dumps(itree)) # Full copy
        >>> list(itree[1])[0].data[0] = "y"
        >>> list(itree)
        [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
        >>> list(itree2)
        [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
        >>> list(itree3)
        [Interval(0, 1, 'x'), Interval(1, 2, ['y'])]
        >>> list(itree4)
        [Interval(0, 1, 'x'), Interval(1, 2, ['x'])]
        
    Equality testing::
    
        >>> IntervalTree([Interval(0,1)]) == IntervalTree([Interval(0,1)])
        True
        >>> IntervalTree([Interval(0,1)]) == IntervalTree([Interval(0,1,"x")])
        False
    """
    
    def __init__(self, intervals=None):
        """
        Set up a tree. If intervals is provided, add all the intervals 
        to the tree.
        
        Completes in O(n*log n) time.
        """
        intervals = intervals if intervals is not None else []
        self.all_intervals = set(intervals)
        self.top_node = Node.from_intervals(self.all_intervals)
        self.boundary_table = {}
        for iv in self.all_intervals:
            self._add_boundaries(iv)
        #self.verify()
    
    def copy(self):
        """
        Construct a new IntervalTree using shallow copies of the 
        intervals in the source tree.
        
        Completes in O(n*log n) time.
        """
        return IntervalTree(iv.copy() for iv in self)
    
    def _add_boundaries(self, interval):
        """
        Records the boundaries of the interval in the boundary table.
        """
        begin = interval.begin
        end = interval.end
        if begin in self.boundary_table: 
            self.boundary_table[begin] += 1
        else:
            self.boundary_table[begin] = 1
        
        if end in self.boundary_table:
            self.boundary_table[end] += 1
        else:
            self.boundary_table[end] = 1
    
    def _remove_boundaries(self, interval):
        """
        Removes the boundaries of the interval from the boundary table.
        """
        begin = interval.begin
        end = interval.end
        if self.boundary_table[begin] == 1:
            del self.boundary_table[begin]
        else:
            self.boundary_table[begin] -= 1
        
        if self.boundary_table[end] == 1:
            del self.boundary_table[end]
        else:
            self.boundary_table[end] -= 1
    
    def add(self, interval):
        """
        Adds an interval to the tree, if not already present.
        
        Completes in O(log n) time.
        """
        if interval in self: 
            return
        
        #self.verify()
        
        #if self.top_node:
        #    assert(interval not in self.top_node.search_point(interval.begin, set()))
        self.all_intervals.add(interval)
        if self.top_node is None:
            self.top_node = Node.from_interval(interval)
        else:
            self.top_node = self.top_node.add(interval)
        self._add_boundaries(interval)        
        #assert(interval in self.top_node.search_point(interval.begin, set()))
        #self.verify()
    append = add
    
    def addi(self, begin, end, data=None):
        """
        Shortcut for add(Interval(begin, end, data)).
        
        Completes in O(log n) time.
        """
        return self.add(Interval(begin, end, data))
    appendi = addi
    
    def extend(self, intervals):
        """
        Given an iterable of intervals, add them to the tree.
        
        Completes in O(m*log(n+m), where m = number of intervals to 
        add.
        """
        for iv in intervals:
            self.add(iv)
    
    def remove(self, interval):
        """
        Removes an interval from the tree, if present. If not, raises 
        ValueError.
        
        Completes in O(log n) time.
        """
        #self.verify()
        if interval not in self:
            #print(self.all_intervals)
            raise ValueError
        self.top_node = self.top_node.remove(interval)
        self.all_intervals.remove(interval)
        self._remove_boundaries(interval)
        #self.verify()
    
    def removei(self, begin, end, data=None):
        """
        Shortcut for remove(Interval(begin, end, data)).
        
        Completes in O(log n) time.
        """
        return self.remove(Interval(begin, end, data))
    
    def discard(self, interval):
        """
        Removes an interval from the tree, if present. If not, does 
        nothing.
        
        Completes in O(log n) time.
        """
        if interval not in self:
            return
        self.all_intervals.discard(interval)
        self.top_node = self.top_node.discard(interval)
        self._remove_boundaries(interval)
    
    def discardi(self, begin, end, data=None):
        """
        Shortcut for discard(Interval(begin, end, data)).
        
        Completes in O(log n) time.
        """
        return self.discard(Interval(begin, end, data))
    
    def remove_overlap(self, begin, end=None):
        """
        Removes all intervals overlapping the given point or range.
        
        Completes in O((r+m)*log n) time, where:
          * n = size of the tree
          * m = number of matches
          * r = size of the search range (this is 1 for a point)
        """
        hitlist = self.search(begin, end)
        for iv in hitlist: 
            self.remove(iv)
    
    def remove_envelop(self, begin, end):
        """
        Removes all intervals completely enveloped in the given range.
        
        Completes in O((r+m)*log n) time, where:
          * n = size of the tree
          * m = number of matches
          * r = size of the search range (this is 1 for a point)
        """
        hitlist = self.search(begin, end, strict=True)
        for iv in hitlist:
            self.remove(iv)
        
    def find_nested(self):
        """
        Returns a dictionary mapping parent intervals to sets of 
        intervals overlapped by and contained in the parent.
        
        Completes in O(n^2) time.
        """
        result = {}
        
        def add_if_nested():
            if parent.contains_interval(child):
                if parent not in result:
                    result[parent] = set()
                result[parent].add(child)
                
        long_ivs = sorted(self.all_intervals, key=len, reverse=True)
        for i, parent in enumerate(long_ivs):
            for child in long_ivs[i+1:]:
                add_if_nested()
        return result
    
    def overlaps(self, begin, end=None):
        """
        Returns whether some interval in the tree overlaps the given
        point or range.
        
        Completes in O(r*log n) time, where r is the size of the
        search range.
        """
        if end is not None:
            return self.overlaps_range(begin, end)
        elif isinstance(begin, Number):
            return self.overlaps_point(begin)
        else:
            return self.overlaps_range(begin.begin, begin.end)
    
    def overlaps_point(self, p):
        """
        Returns whether some interval in the tree overlaps p.
        
        Completes in O(log n) time.
        """
        if self.is_empty():
            return False
        return self.top_node.contains_point(p)
    
    def overlaps_range(self, begin, end):
        """
        Returns whether some interval in the tree overlaps the given
        range.
        
        Completes in O(r*log n) time, where r is the range length and n
        is the table size.
        """
        if self.is_empty():
            return False
        elif self.overlaps_point(begin):
            return True
        # TODO: add support for open and closed intervals
        return any(
            self.overlaps_point(bound) 
            for bound in self.boundary_table 
            if begin <= bound < end
        )
    
    def split_overlaps(self):
        """
        Finds all intervals with overlapping ranges and splits them
        along the range boundaries.
        
        Completes in worst-case O(n^2*log n) time (many interval 
        boundaries are inside many intervals), best-case O(n*log n)
        time (small number of overlaps << n per interval).
        """
        if not self:
            return
        if len(self.boundary_table) == 2:
            return
        temp = IntervalTree()
        
        bounds = sorted(self.boundary_table)  # get bound locations

        for lbound, ubound in zip(bounds[:-1], bounds[1:]):
            for iv in self[lbound]:
                temp[lbound:ubound] = iv.data

        self.all_intervals = temp.all_intervals
        self.top_node = temp.top_node
        # self.boundary_table unchanged
        
    def items(self):
        """
        Constructs and returns a set of all intervals in the tree. 
        
        Completes in O(n) time.
        """
        return set(self.all_intervals)
    
    def is_empty(self):
        """
        Returns whether the tree is empty.
        
        Completes in O(1) time.
        """
        return len(self) == 0
    
    def search(self, begin, end=None, strict=False):
        """
        Returns a set of all intervals overlapping the given range. Or,
        if strict is True, returns the set of all intervals fully
        contained in the range [begin, end].
        
        Completes in O(m + k*log n) time, where:
          * n = size of the tree
          * m = number of matches
          * k = size of the search range (this is 1 for a point)
        """
        if self.top_node is None:
            return set()
        if end is None:
            if isinstance(begin, Number):
                return self.top_node.search_point(begin, set())
            else:
                iv = begin
                return self.search(iv.begin, iv.end, strict=strict)
        elif isinstance(end, Number):
            result = self.top_node.search_point(begin, set())
            
            # TODO: add support for open and closed intervals
            result = result.union(self.top_node.search_overlap(
                bound 
                for bound in self.boundary_table 
                if begin < bound < end
            ))
            if strict:
                result = set(
                    iv 
                    for iv in result 
                    if iv.begin >= begin and iv.end <= end
                )
            return result
        else:   # duck-typed interval
            return self.search(begin.begin, begin.end, strict)
    
    def begin(self):
        """
        Returns the lower bound of the first interval in the tree.
        
        Completes in O(n) time.
        """
        return min(self.boundary_table)
    
    def end(self):
        """
        Returns the upper bound of the last interval in the tree.
        
        Completes in O(n) time.
        """
        return max(self.boundary_table)
    
    def print_structure(self, tostring=False):
        """
        ## FOR DEBUGGING ONLY ##
        Pretty-prints the structure of the tree. 
        If tostring is true, prints nothing and returns a string.
        """
        if self.top_node:
            return self.top_node.print_structure(tostring=tostring)
        else:
            result = "<empty IntervalTree>"
            if not tostring:
                print(result)
            else:
                return result
        
    def verify(self):
        """
        ## FOR DEBUGGING ONLY ##
        Checks the table to ensure that the invariants are held.
        """
        if self.all_intervals:
            try:
                assert self.top_node.all_children() == self.all_intervals
            except AssertionError as e:
                print(
                    'Error: the tree and the membership set are out of sync!'
                )
                tivs = set(self.top_node.all_children())
                print('top_node.all_children() - all_intervals:')
                pprint(tivs - self.all_intervals)
                print('all_intervals - top_node.all_children():')
                pprint(self.all_intervals - tivs)
                raise e

            bound_check = {}
            for iv in self:
                if iv.begin in bound_check:
                    bound_check[iv.begin] += 1
                else:
                    bound_check[iv.begin] = 1
                if iv.end in bound_check:
                    bound_check[iv.end] += 1
                else:
                    bound_check[iv.end] = 1
            assert set(self.boundary_table.keys()) == set(bound_check.keys()),\
                'Error: boundary_table is out of sync with ' \
                'the intervals in the tree!'
            for key,val in self.boundary_table.items():   # For efficiency reasons it should be iteritems in Py2, but we don't care much for efficiency in debug methods anyway.
                assert bound_check[key] == val, \
                    'Error: boundary_table[{0}] should be {1},' \
                    ' but is {2}!'.format(
                        key, bound_check[key], val)
            self.top_node.verify(set())
        else:
            assert not self.boundary_table, \
                "Error: boundary table should be empty!"
            assert self.top_node is None, \
                "Error: top_node isn't None!"
    
    def __getitem__(self, index):
        """
        Returns a set of all intervals overlapping the given index or 
        slice.
        
        Completes in O(k * log(n) + m) time, where:
          * n = size of the tree
          * m = number of matches
          * k = size of the search range (this is 1 for a point)
        """
        if isinstance(index, slice):
            return self.search(index.start, index.stop)
        else:
            return self.search(index)
    
    def __setitem__(self, index, value):
        """
        Adds a new interval to the tree. A shortcut for
        add(Interval(index.start, index.stop, value)).
        
        If an identical Interval object with equal range and data 
        already exists, does nothing.
        
        Completes in O(log n) time.
        """
        if not isinstance(index, slice):
            raise IndexError
        self.add(Interval(index.start, index.stop, value))
    
    def __contains__(self, item):
        """
        Returns whether item exists as an Interval in the tree.
        This method only returns True for exact matches; for
        overlaps, see the overlaps() method.
        
        Completes in O(1) time.
        """
        # Removed point-checking code; it might trick the user into
        # thinking that this is O(1), which point-checking isn't.
        #if isinstance(item, Interval):
        return item in self.all_intervals
        #else:
        #    return self.contains_point(item)
    
    def containsi(self, begin, end, data=None):
        """
        Shortcut for (Interval(begin, end, data) in tree).
        
        Completes in O(1) time.
        """
        return Interval(begin, end, data) in self
    
    def __iter__(self):
        """
        Returns an iterator over all the intervals in the tree.
        
        Completes in O(1) time.
        """
        return self.all_intervals.__iter__()
    iter = __iter__
    
    def __len__(self):
        """
        Returns how many intervals are in the tree.
        
        Completes in O(1) time.
        """
        return len(self.all_intervals)
    
    def __eq__(self, other):
        """
        Whether two IntervalTrees are equal.
        
        Completes in O(n) time if sizes are equal; O(1) time otherwise.
        """
        return (
            isinstance(other, IntervalTree) and 
            self.all_intervals == other.all_intervals
        )
    
    def __repr__(self):
        ivs = sorted(self)
        if not ivs:
            return "IntervalTree()"
        else:
            return "IntervalTree({0})".format(ivs)

    __str__ = __repr__

    def __reduce__(self):
        """
        For pickle-ing.
        """
        return IntervalTree, (sorted(self.all_intervals),)


class Node(object):
    def __init__(self,
                 x_center=None,
                 s_center=None,
                 left_node=None,
                 right_node=None):
        self.x_center = x_center
        self.s_center = set(s_center) if s_center is not None else set()
        self.left_node = left_node
        self.right_node = right_node
        self.balance = None  # will be set when rotated
        self.rotate()
    
    @classmethod
    def from_interval(cls, interval):
        if interval is None:
            return None
        center = interval.begin
        #print(center)
        return Node(center, [interval])
    
    @classmethod
    def from_intervals(cls, intervals):
        if not intervals:
            return None
        node = Node()
        node = node.init_from_sorted(sorted(intervals))
        return node
    
    def init_from_sorted(self, intervals):
        if not intervals:
            return None
        center_iv = intervals[len(intervals)//2]
        self.x_center = center_iv.begin
        self.s_center = set()
        s_left = []
        s_right = []
        # TODO: add support for open and closed intervals
        for k in intervals:
            if k.end <= self.x_center:
                s_left.append(k)
            elif k.begin > self.x_center:
                s_right.append(k)
            else:
                self.s_center.add(k)
        self.left_node = Node.from_intervals(s_left)
        self.right_node = Node.from_intervals(s_right)
        return self.rotate()

    def center_hit(self, interval):
        """Returns whether interval overlaps self.x_center."""
        return interval.contains_point(self.x_center)
    
    def hit_branch(self, interval):
        """
        Assuming not center_hit(interval), return which branch 
        (left=0, right=1) interval is in.
        """
        # TODO: add support for open and closed intervals
        return 1 if interval.begin > self.x_center else 0
    
    def refresh_balance(self):
        """Recalculate self.balance."""
        self.balance = bool(self[1]) - bool(self[0])
        if self.balance < 0 and (self[0][0] or self[0][1]):
            self.balance -= 1
        if self.balance > 0 and (self[1][0] or self[1][1]):
            self.balance += 1
    
    def rotate(self):
        """
        Does rotating, if necessary, to balance this node, and 
        returns the new top node.
        """
        self.refresh_balance()
        if abs(self.balance) < 2:
            return self
        # balance > 0  is the heavy side
        my_heavy = self.balance > 0
        child_heavy = self[my_heavy].balance > 0
        if my_heavy == child_heavy:  # Heavy sides same
            return self.srotate()
        else:
            return self.drotate()
    
    def srotate(self):
        """Single rotation. Assumes that balance is not 0."""
        #     self        save
        #   save 3  ->   1   self
        #  1   2            2   3
        #
        #  self            save
        # 3   save  ->  self  1
        #    2   1     3   2
        
        #assert(self.balance != 0)
        heavy = self.balance > 0
        light = not heavy
        save = self[heavy]
        #print("srotate: bal={0},{1}".format(self.balance, save.balance))
        #self.print_structure()
        self[heavy] = save[light]   # 2
        #assert(save[light])
        save[light] = self
        save[light].refresh_balance()
        save[light] = save[light].rotate()
        save.refresh_balance()
        
        # Promoting save could cause invalid overlaps.
        # Repair them.
        for iv in set(self.s_center):
            if save.center_hit(iv):
                save[light] = save[light].remove(iv)
                if save[light]:
                    save[light].refresh_balance()
                save = save.add(iv)
                save.refresh_balance()
        return save
    
    def drotate(self):
        #print("drotate:")
        #self.print_structure()
        self[self.balance > 0] = self[self.balance > 0].srotate()
        self.refresh_balance()
        
        #print("First rotate:")
        #self.print_structure()
        result = self.srotate()
        
        #print("Finished drotate:")
        #self.print_structure()
        #result.verify()

        return result
    
    def add(self, interval):
        """
        Returns self after adding the interval and balancing.
        """
        if self.center_hit(interval):
            self.s_center.add(interval)
            return self
        else:
            direction = self.hit_branch(interval)
            if not self[direction]:
                self[direction] = Node.from_interval(interval)
                self.refresh_balance()
                return self
            else:
                self[direction] = self[direction].add(interval)
                return self.rotate()
    
    def remove(self, interval):
        """
        Returns self after removing the interval and balancing. 
        
        If interval is not present, raise ValueError.
        """
        # since this is a list, called methods can set this to [1],
        # making it true
        done = []     
        return self.remove_interval_helper(interval, done, 
                                           should_raise_error=True)

    def discard(self, interval):
        """
        Returns self after removing interval and balancing.
        
        If interval is not present, do nothing.
        """
        done = []
        return self.remove_interval_helper(interval, done, 
                                           should_raise_error=False)
    
    def remove_interval_helper(self, interval, done, should_raise_error):
        """
        Returns self after removing interval and balancing. 
        If interval doesn't exist, raise ValueError.
        
        This method may set done to [1] to tell all callers that 
        rebalancing has completed.
        
        See Eternally Confuzzled's jsw_remove_r function (lines 1-32) 
        in his AVL tree article for reference.
        """
        if self.center_hit(interval):
            #if trace: print('Hit at {0}'.format(self.x_center))
            if not should_raise_error and interval not in self.s_center:
                done.append(1)
                #if trace: print('Doing nothing.')
                return self
            try:
                # raises error if interval not present - this is 
                # desired.
                self.s_center.remove(interval) 
            except:
                self.print_structure()
                raise KeyError(interval)
            if self.s_center:     # keep this node
                done.append(1)    # no rebalancing necessary
                #if trace: print('Removed, no rebalancing.')
                return self
            
            # If we reach here, no intervals are left in self.s_center.
            # So, prune self.
            return self.prune()
        else:  # interval not in s_center
            direction = self.hit_branch(interval)
            
            if not self[direction]:
                if should_raise_error:
                    raise ValueError
                done.append(1)
                return self
            
            #if trace: 
            #   print('Descending to {0} branch'.format(
            #       ['left', 'right'][direction]
            #       ))
            self[direction] = self[direction].remove_interval_helper(
                interval, done, should_raise_error)
            
            # Clean up
            if not done:
                #if trace: 
                #    print('Rotating {0}'.format(self.x_center))
                #    self.print_structure()
                return self.rotate()
            return self
    
    def search_overlap(self, point_list):
        """
        Returns all intervals that overlap the point_list.
        """
        result = set()
        for j in point_list:
            self.search_point(j, result)
        return result
    
    def search_point(self, point, result):
        """
        Returns all intervals that contain point.
        """
        # TODO: add support for open and closed intervals
        for k in self.s_center:
            if k.begin <= point < k.end:
                result.add(k)
        if point < self.x_center and self[0]:
            return self[0].search_point(point, result)
        elif point > self.x_center and self[1]:
            return self[1].search_point(point, result)
        return result
    
    def prune(self):
        """
        On a subtree where the root node's s_center is empty,
        return a new subtree with no empty s_centers.
        """
        if not self[0] or not self[1]:    # if I have an empty branch
            direction = not self[0]       # graft the other branch here
            #if trace:
            #    print('Grafting {0} branch'.format(
            #       'right' if direction else 'left'))
            
            result = self[direction]
            #if result: result.verify()
            return result
        else:
            # Replace the root node with the greatest predecessor.
            (heir, self[0]) = self[0].pop_greatest_child()
            #if trace: 
            #    print('Replacing {0} with {1}.'.format(
            #        self.x_center, heir.x_center
            #        ))
            #    print('Removed greatest predecessor:')
            #    self.print_structure()
            
            #if self[0]: self[0].verify()
            #if self[1]: self[1].verify()
            
            # Set up the heir as the new root node
            (heir[0], heir[1]) = (self[0], self[1])
            #if trace: print('Setting up the heir:')
            #if trace: heir.print_structure()
            
            # popping the predecessor may have unbalanced this node; 
            # fix it
            heir.refresh_balance()
            heir = heir.rotate()
            #heir.verify()
            #if trace: print('Rotated the heir:')
            #if trace: heir.print_structure()
            return heir
        
    def pop_greatest_child(self):
        """
        Used when pruning a node with both a left and a right branch.
        Returns (greatest_child, node), where:
          * greatest_child is a new node to replace the removed node.
          * node is the subtree after: 
              - removing the greatest child
              - balancing
              - moving overlapping nodes into greatest_child
        
        See Eternally Confuzzled's jsw_remove_r function (lines 34-54)
        in his AVL tree article for reference.
        """
        #print('Popping from {0}'.format(self.x_center))
        if self[1] is None:         # This node is the greatest child.
            # To reduce the chances of an overlap with a parent, return
            # a child node containing the smallest possible number of 
            # intervals, as close as possible to the maximum bound. 
            ivs = set(self.s_center)
            # Create a new node with the largest x_center possible.
            max_iv = max(self.s_center, key=attrgetter('end'))
            max_iv_len = max_iv.end - max_iv.begin
            child_x_center = max_iv.begin if (max_iv_len <= 1) \
                else max_iv.end - 1
            child = Node.from_intervals(
                [iv for iv in ivs if iv.contains_point(child_x_center)]
            )
            child.x_center = child_x_center
            self.s_center = ivs - child.s_center
            
            #print('Pop hit! Returning child   = {0}'.format(
            #    child.print_structure(tostring=True)
            #    ))
            assert not child[0]
            assert not child[1]
            
            if self.s_center:
                #print('     and returning newnode = {0}'.format( self ))
                #self.verify()
                return child, self
            else:
                #print('     and returning newnode = {0}'.format( self[0] ))
                #if self[0]: self[0].verify()
                return child, self[0]  # Rotate left child up
                
        else:
            #print('Pop descent to {0}'.format(self[1].x_center))
            (greatest_child, self[1]) = self[1].pop_greatest_child()
            self.refresh_balance()
            new_self = self.rotate()
            
            # Move any overlaps into greatest_child
            for iv in set(new_self.s_center):
                if iv.contains_point(greatest_child.x_center):
                    new_self.s_center.remove(iv)
                    greatest_child.add(iv)
                    
            #print('Pop Returning child   = {0}'.format(
            #    greatest_child.print_structure(tostring=True)
            #    ))
            if new_self.s_center:
                #print('and returning newnode = {0}'.format(
                #    new_self.print_structure(tostring=True)
                #    ))
                #new_self.verify()
                return greatest_child, new_self
            else:
                new_self = new_self.prune()
                #print('and returning prune = {0}'.format(
                #    new_self.print_structure(tostring=True)
                #    ))
                #if new_self: new_self.verify()
                return greatest_child, new_self
    
    def contains_point(self, p):
        """
        Returns whether this node or a child overlaps p.
        """
        for iv in self.s_center:
            if iv.contains_point(p):
                return True
        branch = self[p > self.x_center]
        return branch and branch.contains_point(p)
    
    def all_children(self):
        return self.all_children_helper(set())
    
    def all_children_helper(self, result):
        result.update(self.s_center)
        if self[0]:
            self[0].all_children_helper(result)
        if self[1]:
            self[1].all_children_helper(result)
        return result
    
    def verify(self, parents=None):
        """
        ## DEBUG ONLY ##
        Recursively ensures that the invariants of an interval subtree 
        hold.
        """
        if parents is None:
            parents = set()

        assert isinstance(self.s_center, set)
        
        bal = self.balance
        assert abs(bal) < 2, \
            "Error: Rotation should have happened, but didn't! \n{0}".format(
                self.print_structure(tostring=True)
            )
        self.refresh_balance()
        assert bal == self.balance, \
            "Error: self.balance not set correctly! \n{0}".format(
                self.print_structure(tostring=True)
            )
        
        assert self.s_center, \
            "Error: s_center is empty! \n{0}".format(
                self.print_structure(tostring=True)
            )
        for iv in self.s_center:
            assert hasattr(iv, 'begin')
            assert hasattr(iv, 'end')
            # TODO: add support for open and closed intervals
            assert iv.begin < iv.end
            assert iv.overlaps(self.x_center)
            for parent in sorted(parents):
                assert not iv.contains_point(parent), \
                    "Error: Overlaps ancestor ({0})! \n{1}\n\n{2}".format(
                        parent, iv, self.print_structure(tostring=True)
                    )
        if self[0]:
            assert self[0].x_center < self.x_center, \
                "Error: Out-of-order left child! {0}".format(self.x_center)
            self[0].verify(parents.union([self.x_center]))
        if self[1]:
            assert self[1].x_center > self.x_center, \
                "Error: Out-of-order right child! {0}".format(self.x_center)
            self[1].verify(parents.union([self.x_center]))

    def __getitem__(self, index):
        """
        Returns the left child if input is equivalent to False, or 
        the right side otherwise.
        """ 
        if index:
            return self.right_node
        else:
            return self.left_node
    
    def __setitem__(self, key, value):
        """Sets the left (0) or right (1) child."""
        if key:
            self.right_node = value
        else:
            self.left_node = value
    
    def __str__(self):
        """
        Shows info about this node.
        
        Since Nodes are internal data structures not revealed to the 
        user, I'm not bothering to make this copy-paste-executable as a
        constructor.
        """
        return "Node<{0}, balance={1}>".format(self.x_center, self.balance)
        #fieldcount = 'c_count,has_l,has_r = <{0}, {1}, {2}>'.format(
        #    len(self.s_center), 
        #    bool(self.left_node), 
        #    bool(self.right_node)
        #)
        #fields = [self.x_center, self.balance, fieldcount]
        #return "Node({0}, b={1}, {2})".format(*fields)
    
    def print_structure(self, indent=0, tostring=False):
        """
        For debugging.
        """
        nl = '\n'
        sp = indent*'    '
        
        rlist = list()
        rlist.append(str(self) + nl)
        rlist.append(sp + '||||:' + nl)
        if self.s_center: 
            for iv in sorted(self.s_center):
                rlist.append(sp+' '+repr(iv) + nl)
        if self.left_node:
            rlist.append(sp + '<<<<:')  # no CR
            rlist.append(self.left_node.print_structure(indent+1, True))
        if self.right_node:
            rlist.append(sp + '>>>>:')  # no CR
            rlist.append(self.right_node.print_structure(indent+1, True))
        result = ''.join(rlist)
        if tostring:
            return result
        else:
            print(result)
