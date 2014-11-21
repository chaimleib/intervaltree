'''
PyIntervalTree: A mutable, self-balancing interval tree.

Interval class.

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
    
    def __len__(self):
        # NB: This redefines the tuple's own "len" which would always return 3
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
        #try:
        c = self.begin - other.begin
        #except Exception as e:
        #    print("self: {0}".format(self) )
        #    print("other: {0}".format(other))
        #    raise e
        if c == 0:
            c = self.end - other.end
        if c == 0:
            c = -1 if self.data < other.data \
                else (1 if self.data > other.data else 0)
        return c

    # def __lt__(self, other):
    #     if (self.begin, self.end) == (other.begin, other.end):
    #         try:
    #             # The third element here helps solve the "unorderable type" problem in Python3 when comparing, e.g., None and non-None data fields.
    #             return (self.begin, self.end, type(self.data).__name__, self.data) < (other.begin, other.end, type(other.data).__name__, other.data)
    #         except TypeError: # still get an "unorderable type" error (e.g. dict cannot be compared with dict in Py3)
    #             # Not really sure whether it may backfire anywhere
    #             return False
    #     else:
    #         return (self.begin, self.end) < (other.begin, other.end)
        
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

    def __str__(self):
        return str(self.__unicode__())
    
    def __unicode__(self):
        fields = self._get_fields()
        return u"Interval{0}".format(fields)
    
    def __repr__(self):
        return str(self)

    def copy(self):
        return Interval(self.begin, self.end, self.data)
    
    def __reduce__(self):
        """
        For pickle-ing.
        """
        return Interval, self._get_fields()

