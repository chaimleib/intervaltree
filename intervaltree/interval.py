"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Interval class

Copyright 2013-2014 Chaim-Leib Halbert
Modifications copyright 2014 Konstantin Tretyakov

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
from numbers import Number
from collections import namedtuple


class Interval(namedtuple('IntervalBase', ['begin', 'end', 'data'])):
    __slots__ = ()  # Saves memory, avoiding the need to create __dict__ for each interval
    def __new__(cls, begin, end, data=None):
        return super(Interval, cls).__new__(cls, begin, end, data)
    
    def overlaps(self, begin, end=None):
        if end is not None:
            return (
                (begin <= self.begin < end) or
                (begin < self.end <= end) or
                (self.begin <= begin < self.end) or
                (self.begin < end <= self.end)
            )
        elif isinstance(begin, Number):
            return self.contains_point(begin)
        else:   # duck-typed interval
            return self.overlaps(begin.begin, begin.end)
    
    def contains_point(self, p):
        return self.begin <= p < self.end
    
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

    def is_null(self):
        """
        Returns True if nothing is contained in this interval, i.e. end <= begin.
        """
        return self.begin >= self.end

    def length(self):
        if self.is_null():
            return 0
        return self.end - self.begin

    def __hash__(self):
        return hash((self.begin, self.end))

    def __eq__(self, other):
        return (
            self.begin == other.begin and
            self.end == other.end and
            self.data == other.data
        )

    def __cmp__(self, other):
        s = self[0:2]
        o = other[0:2]
        if s != o:
            return -1 if s < o else 1
        try:
            if self.data == other.data:
                return 0
            return -1 if self.data < other.data else 1
        except TypeError:
            s = type(self.data).__name__
            o = type(other.data).__name__
            if s == o:
                return 0
            return -1 if s < o else 1
        
    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def _get_fields(self):
        """Used by str, unicode, repr and __reduce__.

        Returns only the fields necessary to reconstruct the Interval.
        """
        if self.data is not None:
            return self.begin, self.end, self.data
        else:
            return self.begin, self.end
    
    def __repr__(self):
        if isinstance(self.begin, Number):
            s_begin = str(self.begin)
            s_end = str(self.end)
        else:
            s_begin = repr(self.begin)
            s_end = repr(self.end)
        if self.data is None:
            return "Interval({0}, {1})".format(s_begin, s_end)
        else:
            return "Interval({0}, {1}, {2})".format(s_begin, s_end, repr(self.data))

    __str__ = __repr__

    def copy(self):
        return Interval(self.begin, self.end, self.data)
    
    def __reduce__(self):
        """
        For pickle-ing.
        """
        return Interval, self._get_fields()
