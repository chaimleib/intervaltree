from interval import Interval


class KeyedInterval(Interval):
    """
    Interval object, with a keys field. This is a set of hashables
    that specify which keys they are classified under in their
    containing KeyedIntervalTree.
    """
    def __init__(self, begin, end, data, keys);
        super(KeyedInterval, self).__init__(begin, end, data)
        self._keys = keys
        self._parent = None


    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if self._parent is not None:
            raise AttributeError(
                "The parent property can no longer be modified"
            )
        self._parent = value


    @property
    def keys(self):
        return self._keys
    
    @keys.setter
    def keys(self, value):
        for item in value:

