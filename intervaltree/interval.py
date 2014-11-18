'''
PyIntervalTree: A mutable, self-balancing interval tree.

Interval class.

Copyright 2014, Chaim-Leib Halbert et al.
Most recent fork and modifications by Konstantin Tretyakov

Licensed under LGPL.
'''
from numbers import Number
from collections import namedtuple

class Interval(namedtuple('IntervalBase', ['begin', 'end', 'data'])):
    __slots__ = ()  # Saves memory, avoiding the need to create __dict__ for each interval
    def __new__(cls, begin, end, data=None):
        return super(Interval, cls).__new__(cls, begin, end, data)
    
    def overlaps(self, begin, end=None):
        if end is not None:
            return (
                (begin <= self.begin <  end)      or
                (begin <  self.end   <= end)      or
                (self.begin <= begin <  self.end) or
                (self.begin <  end   <= self.end)
            )
        elif isinstance(begin, Number):
            return self.contains_point(begin)
        else:   # duck-typed interval
            return self.overlaps(begin.begin, begin.end)
    
    def contains_point(self, p):
        return (self.begin) <= p < (self.end)
    
    def range_matches(self, other):
        return (
            self.begin == other.begin and 
            self.end == other.end
        )
    
    def contains_interval(self, other):
        return (
            self.begin <= other.begin and
            self.end >= other.end
        )
    
    def distance_to(self, other):
        """
        Returns the size of the gap between intervals, or 0 
        if they touch or overlap.
        """
        if self.overlaps(other):
            return 0
        elif self.begin < other.begin:
            return other.begin - self.end
        else:
            return self.begin - other.end
    
    def __len__(self):
        # NB: This redefines the tuple's own "len" which would always return 3
        return self.end - self.begin
    
    def __hash__(self):
        # Allow to have unhashable elements in the data field.
        return hash((self.begin, self.end))
    
    def __lt__(self, other):
        if (self.begin, self.end) == (other.begin, other.end):
            try:
                # The third element here helps solve the "unorderable type" problem in Python3 when comparing, e.g., None and non-None data fields.
                return (self.begin, self.end, type(self.data).__name__, self.data) < (other.begin, other.end, type(other.data).__name__, other.data)
            except TypeError: # still get an "unorderable type" error (e.g. dict cannot be compared with dict in Py3)
                # Not really sure whether it may backfire anywhere
                return False
        else:
            return (self.begin, self.end) < (other.begin, other.end)
        
    def __repr__(self):
        fields = map(repr, [self.begin, self.end, self.data])
        return "Interval({}, {}, {})".format(*fields)
    
    __str__ = __repr__    
    
    def copy(self):
        return Interval(self.begin, self.end, self.data)
    
    def __reduce__(self):
        """
        For pickle-ing.
        """
        return Interval, (self.begin, self.end, self.data)
