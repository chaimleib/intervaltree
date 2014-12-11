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
from pprint import pprint
try:
    from functools import cmp_to_key
except ImportError:
    def cmp_to_key(mycmp):
        """Convert a cmp= function into a key= function"""
        class K(object):
            def __init__(self, obj):
                self.obj = obj

            def __lt__(self, other):
                return mycmp(self.obj, other.obj) < 0

            def __gt__(self, other):
                return mycmp(self.obj, other.obj) > 0

            def __eq__(self, other):
                return mycmp(self.obj, other.obj) == 0

            def __le__(self, other):
                return mycmp(self.obj, other.obj) <= 0

            def __ge__(self, other):
                return mycmp(self.obj, other.obj) >= 0

            def __ne__(self, other):
                return mycmp(self.obj, other.obj) != 0

            def __hash__(self):
                raise TypeError('hash not implemented')

        return K


# noinspection PyBroadException
class Interval(namedtuple('IntervalBase', ['begin', 'end', 'data'])):
    __slots__ = ()  # Saves memory, avoiding the need to create __dict__ for each interval

    def __new__(cls, begin, end, data=None):
        return super(Interval, cls).__new__(cls, begin, end, data)
    
    def overlaps(self, begin, end=None):
        """
        Whether the interval overlaps the given point, range or Interval.
        :param begin: beginning point of the range, or the point, or an Interval
        :param end: end point of the range. Optional if not testing ranges.
        :return: True or False
        :rtype: bool
        """
        if end is not None:
            return (
                (begin <= self.begin < end) or
                (begin < self.end <= end) or
                (self.begin <= begin < self.end) or
                (self.begin < end <= self.end)
            )
        try:
            return self.overlaps(begin.begin, begin.end)
        except:
            return self.contains_point(begin)

    def contains_point(self, p):
        """
        Whether the Interval contains p.
        :param p: a point
        :return: True or False
        :rtype: bool
        """
        return self.begin <= p < self.end
    
    def range_matches(self, other):
        """
        Whether the begins equal and the ends equal. Compare __eq__().
        :param other: Interval
        :return: True or False
        :rtype: bool
        """
        return (
            self.begin == other.begin and 
            self.end == other.end
        )
    
    def contains_interval(self, other):
        """
        Whether other is contained in this Interval.
        :param other: Interval
        :return: True or False
        :rtype: bool
        """
        return (
            self.begin <= other.begin and
            self.end >= other.end
        )
    
    def distance_to(self, other):
        """
        Returns the size of the gap between intervals, or 0 
        if they touch or overlap.
        :param other: Interval or point
        :return: distance
        :rtype: Number
        """
        if self.overlaps(other):
            return 0
        try:
            if self.begin < other.begin:
                return other.begin - self.end
            else:
                return self.begin - other.end
        except:
            if self.end < other:
                return other - self.end
            else:
                return self.begin - other

    def is_null(self):
        """
        Whether this equals the null interval.
        :return: True if end <= begin else False
        :rtype: bool
        """
        return self.begin >= self.end

    def length(self):
        """
        The distance covered by this Interval.
        :return: length
        :type: Number
        """
        if self.is_null():
            return 0
        return self.end - self.begin

    def __hash__(self):
        """
        Depends on begin and end only.
        :return: hash
        :rtype: Number
        """
        return hash((self.begin, self.end))

    def __eq__(self, other):
        """
        Whether the begins equal, the ends equal, and the data fields
        equal. Compare range_matches().
        :param other: Interval
        :return: True or False
        :rtype: bool
        """
        return (
            self.begin == other.begin and
            self.end == other.end and
            self.data == other.data
        )

    def __cmp__(self, other):
        """
        Tells whether other sorts before, after or equal to this
        Interval.

        Sorting is by begins, then by ends, then by data fields.

        If data fields are not both sortable types, data fields are
        compared alphabetically by type name.
        :param other: Interval
        :return: -1, 0, 1
        :rtype: int
        """
        s = self[0:2]
        try:
            o = other[0:2]
        except:
            o = (other,)
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
    cmp = __cmp__

    """
    Sorting keys, for use in
        sorted(list(...), key=Interval.key)

    TODO: figure out a way that users don't have to specify the key.
    http://stackoverflow.com/questions/27413491/python-sorting-intervals-with-cmp-with-lt-meaning-strictly-less-than
    """
    key = __key__ = cmp_to_key(cmp)


    @classmethod
    def sorted(cls, *args, **kwargs):
        """
        Same as sorted(lst, key=Interval.key).
        :param lst: an iterable
        :return: list of Interval
        """
        return sorted(*args, key=cls.key, **kwargs)


    def __lt__(self, other):
        """
        Less than operator. Returns False if there is an overlap.
        :param other: Interval or point
        :return: True or False
        :rtype: bool
        """
        return not self.overlaps(other) and self.end <= other

    def __gt__(self, other):
        """
        Greater than operator. Returns False if there is an overlap.
        :param other: Interval or point
        :return: True or False
        :rtype: bool
        """
        return not self.overlaps(other) and self.begin > other

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
