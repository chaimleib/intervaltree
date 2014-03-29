from interval import *
from numbers import Number
from operator import attrgetter
    
class IntervalTree:
    """
    A binary lookup tree of intervals.
    
    Features:
        * Initialize blank or from an iterable of Intervals in 
          O(n * log n).
        * Insertions
            * tree[a:b] = value
            * tree.add(Interval(a, b, value))
            * tree.extend(list_of_interval_objs)
        * Deletions
            * tree.remove(interval)
              raises ValueError if not present
            * tree.discard(interval)
              quiet if not present
            * tree.remove_overlap(point)
            * tree.remove_overlap(begin, end)
              removes all overlapping the range
            * tree.remove_envelop(begin, end)
              removes all enveloped in the range
        * Overlap queries:
            * tree[point]
            * tree[begin, end]
            * tree.search(point)
            * tree.search(begin, end)
        * Envelop queries:
            * tree.search(begin, end, strict = True)
        * Membership queries:
            * interval_obj in tree
              this is fastest
            * tree.overlaps(point)
            * tree.overlaps(begin, end)
        * Sizing:
            * len(tree)
            * tree.is_empty()
            * not tree
            * tree.begin()
            * tree.end()
        * Iterable:
            * for interval_obj in tree:
            * tree.items()
        * Copy- and typecast-able:
            * IntervalTree(tree)
              Interval objects are same as those in tree
            * tree.copy()
              Interval objects are shallow copies of those in tree
            * set(tree)
              can later be fed into IntervalTree()
            * list(tree)
              ditto
        * Equal-able
        * Hashable
        * Pickle-friendly
        * Automatic AVL balancing.
    
    Based on:
        * AVL tree, from 
          http://www.eternallyconfuzzled.com/tuts/datastructures/jsw_tut_avl.aspx
        * "Interval Tree", from 
          http://en.wikipedia.org/wiki/Interval_tree
        * Heavily modified from Tyler Kahn's "Interval Tree 
          implementation in Python," from
          http://forrst.com/posts/Interval_Tree_implementation_in_python-e0K
    """
    
    def __init__(self, intervals=None):
        """
        Set up a tree. If intervals is set, add all the intervals to 
        the tree.
        
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
        
        Completes in O( (r+m) * log n ) time, where:
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
        
        Completes in O( (r+m) * log n ) time, where:
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
        
        def add_if_nested(parent, child):
            if parent.contains_interval(child):
                if parent not in result:
                    result[parent] = set()
                result[parent].add(child)
                
        long_ivs = sorted(self.all_intervals, key=len, reverse=True)
        for i in xrange(len(long_ivs)):
            parent = long_ivs[i]
            for k in xrange(i+1, len(long_ivs)):
                add_if_nested(parent, long_ivs[k])
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
        
        Completes in worst-case O(n^2*log n) time, average O(n*log n) time.
        """
        if not self:
            return
        if len(self.boundary_table) == 2:
            return
        temp = IntervalTree()
        
        bounds = sorted(self.boundary_table) # get bound locations
        # if strict:
        for i in xrange(len(bounds)-1):
            lbound = bounds[i]
            ubound = bounds[i+1]
            for iv in self[lbound]:
                temp[lbound:ubound] = iv.data
        # else:
        #     subbounds = []
        #     for i in xrange(len(bounds)-1):
        #         bound = bounds[i]
        #         if not self.overlaps_point(bound):
        #             subbounds.append(bound)
        #     lbound = self.begin()
        
            
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
        else: # duck-typed interval
            return self.search(begin.begin, begin.end, strict)
    
    def begin(self):
        """
        Returns the begin attribute of the first interval in the tree.
        """
        return min(self.boundary_table)
    
    def end(self):
        """
        Returns the end attribute of the last interval in the tree.
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
            except Exception as e:
                print('Error: the tree and the membership set are out' \
                    ' of sync!')
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
            for key,val in self.boundary_table.iteritems():
                assert bound_check[key] == val, \
                    'Error: boundary_table[{}] should be {},' \
                    ' but is {}!'.format(
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
        Adds a new interval to the tree.
        
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
        This method only returns true for exact matches; for
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
    
    __hash__ = object.__hash__
        
    def __eq__(self, other):
        """
        Whether two interval trees are equal.
        
        Completes in O(n) time worst-case, O(1) otherwise.
        """
        return (
            isinstance(other, IntervalTree) and 
            self.all_intervals == other.all_intervals
        )
        
    def __str__(self):
        return str(unicode(self))
        
    def __unicode__(self):
        ivs = sorted(self)
        if not ivs:
            return u"IntervalTree()"
        else:
            ivs = u", ".join(map(unicode, ivs))
            return u"IntervalTree([{}])".format(ivs)
    
    def __repr__(self):
        ivs = sorted(self)
        if not ivs:
            return "IntervalTree()"
        else:
            ivs = ", ".join(map(repr, ivs))
            return "IntervalTree([{}])".format(ivs)
    
    def __reduce__(self):
        """
        For pickle-ing.
        """
        return (IntervalTree, (sorted(self.all_intervals),))

class Node:
    def __init__(self, x_center=None, s_center=set(), left_node=None, right_node=None):
        self.x_center = x_center
        self.s_center = set(s_center)
        self.left_node = left_node
        self.right_node = right_node
        
        self.rotate()
    
    @classmethod
    def from_interval(cls, interval):
        if interval is None:
            return None
        center = interval.begin #+ (interval.end-interval.begin)/2;
        #print(center)
        return Node(center, [interval] )
    
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
        center_iv = intervals[len(intervals)/2]
        self.x_center = center_iv.begin #+ (center_iv.end - center_iv.begin)/2
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
        if self.balance<0:
            #self.balance -= abs(self[0].balance)
            self.balance -= 1 if (self[0][0] or self[0][1]) else 0
        if self.balance>0:
            #self.balance += abs(self[1].balance)
            self.balance += 1 if (self[1][0] or self[1][1]) else 0
    
    def rotate(self):
        """
        Does rotating, if necessary, to balance this node, and 
        returns the new top node.
        """
        self.refresh_balance()
        if abs(self.balance) < 2:
            return self
        # balance > 0  is the heavy side
        my_heavy = self.balance>0
        child_heavy = self[my_heavy].balance>0
        if my_heavy == child_heavy: # Heavy sides same
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
        heavy = self.balance>0
        light = not heavy
        save = self[heavy]
        #print("srotate: bal={},{}".format(self.balance, save.balance))
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
        self[self.balance>0] = self[self.balance>0].srotate()
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
                                           shouldRaiseError=True)

    def discard(self, interval):
        """
        Returns self after removing interval and balancing.
        
        If interval is not present, do nothing.
        """
        done = []
        return self.remove_interval_helper(interval, done, 
                                           shouldRaiseError=False)
    
    def remove_interval_helper(self, interval, done, shouldRaiseError):
        """
        Returns self after removing interval and balancing. 
        If interval doesn't exist, raise ValueError.
        
        This method may set done to [1] to tell all callers that 
        rebalancing has completed.
        
        See Eternally Confuzzled's jsw_remove_r function (lines 1-32) 
        in his AVL tree article for reference.
        """
        trace = interval.begin == 347 and interval.end == 353
        #if trace: print('\nRemoving from {} interval {}'.format(
        #   self.x_center, interval))
        if self.center_hit(interval):
            #if trace: print('Hit at {}'.format(self.x_center))
            if not shouldRaiseError and interval not in self.s_center:
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
        else: # interval not in s_center
            direction = self.hit_branch(interval)
            
            if not self[direction]:
                if shouldRaiseError:
                    raise ValueError
                done.append(1)
                return self
            
            #if trace: 
            #   print('Descending to {} branch'.format(
            #       ['left', 'right'][direction]
            #       ))
            self[direction] = self[direction].remove_interval_helper(
                interval, done, shouldRaiseError)
            
            # Clean up
            if not done:
                #if trace: 
                #    print('Rotating {}'.format(self.x_center))
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
            if k.begin <= point and point < k.end:
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
            #    print('Grafting {} branch'.format(
            #       'right' if direction else 'left'))
            
            result = self[direction]
            #if result: result.verify()
            return result
        else:
            # Replace the root node with the greatest predecessor.
            (heir, self[0]) = self[0].pop_greatest_child()
            #if trace: 
            #    print('Replacing {} with {}.'.format(
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
        #print('Popping from {}'.format(self.x_center))
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
            
            #print('Pop hit! Returning child   = {}'.format( 
            #    child.print_structure(tostring=True)
            #    ))
            assert not child[0]
            assert not child[1]
            
            if self.s_center:
                #print('     and returning newnode = {}'.format( self ))
                #self.verify()
                return (child, self)
            else:
                #print('     and returning newnode = {}'.format( self[0] ))
                #if self[0]: self[0].verify()
                return (child, self[0]) # Rotate left child up
                
        else:
            #print('Pop descent to {}'.format(self[1].x_center))
            (greatest_child, self[1]) = self[1].pop_greatest_child()
            self.refresh_balance()
            new_self = self.rotate()
            
            # Move any overlaps into greatest_child
            for iv in set(new_self.s_center):
                if iv.contains_point(greatest_child.x_center):
                    new_self.s_center.remove(iv)
                    greatest_child.add(iv)
                    
            #print('Pop Returning child   = {}'.format( 
            #    greatest_child.print_structure(tostring=True)
            #    ))
            if new_self.s_center:
                #print('and returning newnode = {}'.format(
                #    new_self.print_structure(tostring=True)
                #    ))
                #new_self.verify()
                return (greatest_child, new_self)
            else:
                new_self = new_self.prune()
                #print('and returning prune = {}'.format( 
                #    new_self.print_structure(tostring=True)
                #    ))
                #if new_self: new_self.verify()
                return (greatest_child, new_self)
    
    def contains_point(self, p):
        """
        Returns whether this node or a child overlaps p.
        """
        for iv in self.s_center:
            if iv.contains_point(p):
                return True
        branch = self[p>self.x_center]
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
    
    def verify(self, parents = set()):
        """
        ## DEBUG ONLY ##
        Recursively ensures that the invariants of an interval subtree 
        hold.
        """
        assert(isinstance(self.s_center, set))
        
        bal = self.balance
        assert abs(bal) < 2, \
            "Error: Rotation should have happened, but didn't! \n{}".format(
                self.print_structure(tostring=True)
                )
        self.refresh_balance()
        assert bal == self.balance, \
            "Error: self.balance not set correctly! \n{}".format(
                self.print_structure(tostring=True)
                )
        
        assert self.s_center, \
            "Error: s_center is empty! \n{}".format(
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
                    "Error: Overlaps ancestor ({})! \n{}\n\n{}".format(
                        parent, iv, self.print_structure(to_string=True)
                        )
        if self[0]:
            assert self[0].x_center < self.x_center, \
                "Error: Out-of-order left child! {}".format(self.x_center)
            self[0].verify(parents.union([self.x_center]))
        if self[1]:
            assert self[1].x_center > self.x_center, \
                "Error: Out-of-order right child! {}".format(self.x_center)
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
        return "Node<{}, balance={}>".format(self.x_center, self.balance)
        #fieldcount = 'c_count,has_l,has_r = <{}, {}, {}>'.format(
        #    len(self.s_center), 
        #    bool(self.left_node), 
        #    bool(self.right_node)
        #)
        #fields = [self.x_center, self.balance, fieldcount]
        #return "Node({}, b={}, {})".format(*fields)
    
    def print_structure(self, indent=0, tostring=False):
        """
        For debugging.
        """
        result = ''
        CR = '\n'
        sp = indent*'    '
        
        rlist = []
        rlist.append(str(self) + CR)
        rlist.append(sp + '||||:' + CR)
        if self.s_center: 
            for iv in sorted(self.s_center):
                rlist.append(sp+' '+repr(iv) + CR)
        if self.left_node:
            rlist.append(sp + '<<<<:') # no CR
            rlist.append(self.left_node.print_structure(indent+1, True))
        if self.right_node:
            rlist.append(sp + '>>>>:') # no CR
            rlist.append(self.right_node.print_structure(indent+1, True))
        result = ''.join(rlist)
        if tostring:
            return result
        else:
            print(result)


if __name__ == "__main__":
    try:
        # My version of pprint formats Intervals and IntervalTrees
        # more nicely
        from util.pprint import pprint
    except Exception as e:
        from pprint import pprint
    from operator import attrgetter
    
    def makeinterval(lst):
        return Interval(
            lst[0], 
            lst[1], 
            "{}-{}".format(*lst)
            )
    
    ivs = map(makeinterval, [
        [1,2],
        [4,7],
        [5,9],
        [6,10],
        [8,10],
        [8,15],
        [10,12],
        [12,14],
        [14,15],
        ])
    t = IntervalTree(ivs)
    t.verify()
    pprint(t)
    #t.print_structure()
    orig = t.print_structure(True)
        
    assert orig == \
    """Node<8, balance=0>
||||:
 Interval(5, 9, '5-9')
 Interval(6, 10, '6-10')
 Interval(8, 10, '8-10')
 Interval(8, 15, '8-15')
<<<<:Node<4, balance=-1>
    ||||:
     Interval(4, 7, '4-7')
    <<<<:Node<1, balance=0>
        ||||:
         Interval(1, 2, '1-2')
>>>>:Node<12, balance=0>
    ||||:
     Interval(12, 14, '12-14')
    <<<<:Node<10, balance=0>
        ||||:
         Interval(10, 12, '10-12')
    >>>>:Node<14, balance=0>
        ||||:
         Interval(14, 15, '14-15')
"""
    
    def data(s): 
        return set(map(attrgetter('data'), s))
    
    # Query tests
    print('Query tests...')
    assert data(t[4])          == set(['4-7'])
    assert data(t[4:5])        == set(['4-7'])
    assert data(t[4:6])        == set(['4-7', '5-9'])
    assert data(t[9])          == set(['6-10', '8-10', '8-15'])
    assert data(t[15])         == set()
    assert data(t.search(5))   == set(['4-7', '5-9'])
    assert data(t.search(6, 11, strict = True)) == set(['6-10', '8-10'])
    
    print('    passed')
    
    # Membership tests
    print('Membership tests...')
    assert ivs[1] in t
    assert Interval(1,3, '1-3') not in t
    assert t.overlaps(4)
    assert t.overlaps(9)
    assert not t.overlaps(15)
    assert t.overlaps(0,4)
    assert t.overlaps(1,2)
    assert t.overlaps(1,3)
    assert t.overlaps(8,15)
    assert not t.overlaps(15, 16)
    assert not t.overlaps(-1, 0)
    assert not t.overlaps(2,4)
    print('    passed')
    
    # Insertion tests
    print('Insertion tests...')
    t.add( makeinterval([1,2]) )  # adding duplicate should do nothing
    assert data(t[1])        == set(['1-2'])
    assert orig == t.print_structure(True)
    
    t[1:2] = '1-2'                # adding duplicate should do nothing
    assert data(t[1])        == set(['1-2'])
    assert orig == t.print_structure(True)
    
    t.add(makeinterval([2,4]))
    assert data(t[2])        == set(['2-4'])
    t.verify()
    
    t[13:15] = '13-15'
    assert data(t[14])       == set(['8-15', '13-15', '14-15'])
    t.verify()
    print('    passed')
    
    # Duplication tests
    print('Interval duplication tests...')
    t.add(Interval(14,15,'14-15####'))
    assert data(t[14])        == set(['8-15', '13-15', '14-15', '14-15####'])
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
        t.remove(
            Interval(1,3, "Doesn't exist")
            )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
    
    try:
        t.remove(
            Interval(500, 1000, "Doesn't exist")
            )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
    
    orig = t.print_structure(True)
    t.discard( Interval(1,3, "Doesn't exist") )
    t.discard( Interval(500, 1000, "Doesn't exist") )
    assert orig == t.print_structure(True)
    
    assert data(t[14])        == set(['8-15', '13-15', '14-15', '14-15####'])
    t.remove( Interval(14,15,'14-15####') )
    assert data(t[14])        == set(['8-15', '13-15', '14-15'])
    t.verify()
    
    assert data(t[2])        == set(['2-4'])
    t.discard( makeinterval([2,4]) )
    assert data(t[2])        == set()
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
    
    t = IntervalTree(ivs)
    pprint(t)
    t.split_overlaps()
    pprint(t)
    #import cPickle as pickle
    #p = pickle.dumps(t)
    #print(p)
    
