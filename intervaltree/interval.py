from numbers import Number

class Interval:
    def __init__(self, begin, end, data = None):
        self.begin = begin
        self.end = end
        self.data = data
    
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
        return self.end - self.begin
    
    def __hash__(self):
        #data_hash = hash(self.data) if hasattr('__hash__', self.data) else id(self.data)
        return hash( self.begin * self.end )
    
    def __cmp__(self, other):
        #try:
        c = self.begin - other.begin
        #except Exception as e:
        #    print("self: {}".format(self) )
        #    print("other: {}".format(other))
        #    raise e
        if c == 0:
            c = self.end - other.end
        if c == 0:
            c = -1 if self.data < other.data else (1 if self.data > other.data else 0)
        return c
    
    def __str__(self):
        return str(unicode(self))
    
    def __unicode__(self):
        return u"<Interval: "+ repr([self.begin, self.end, self.data])+u">"
    
    def __repr__(self):
        fields = map(repr, [self.begin, self.end, self.data])
        return "Interval({}, {}, {})".format(*fields)
    
    def copy(self):
        return Interval(self.begin, self.end, self.data)
    
    def __reduce__(self):
        """
        For pickle-ing.
        """
        return Interval, (self.begin, self.end, self.data)
