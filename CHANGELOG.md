Change log
==========

Version 0.3.3
-------------

- Bug fixes:
    - Made IntervalTree crash if inited with a null Interval (end <= begin)
- Behavior change:
    - IntervalTree raises ValueError instead of AssertionError when a null Interval is inserted 

Version 0.3.2
-------------

- Support for Python 3.2+ and 2.6+
- Changed license from LGPL to more permissive Apache license
- Merged changes from https://github.com/konstantint/PyIntervalTree to
    https://github.com/chaimleib/PyIntervalTree
    - Interval now inherits from a namedtuple. Benefits: should be faster.
        Drawbacks: slight behavioural change (Intervals not mutable anymore).
    - Added float tests
    - Use setup.py for tests
    - Automatic testing via travis-ci
    - Removed dependency on six
- Interval improvements:
    - Intervals without data have a cleaner string representation
    - Intervals without data are pickled more compactly
    - Better hashing
    - Intervals are ordered by begin, then end, then by data. If data is not
        orderable, sorts by type(data)
- Bug fixes:
    - Fixed crash when querying empty tree
    - Fixed missing close parenthesis in examples
    - Made IntervalTree crash earlier if a null Interval is added
- Internals:
    - New test directory
    - Nicer display of data structures for debugging, using custom
        test/pprint.py (Python 2.6, 2.7)
    - More sensitive exception handling
    - Local script to test in all supported versions of Python
    - Added IntervalTree.score() to measure how optimally a tree is structured

Version 0.2.3
-------------

- Slight changes for inclusion in PyPI.
- Some documentation changes
- Added tests
- Fixed the bug, where interval addition via [] would not work properly 
    in Python 2.7 (see http://bugs.python.org/issue21785)
- Added intervaltree.bio subpackage, adding some utilities for use in bioinformatics
    
Version 0.2.2b
--------------

- Forked from https://github.com/MusashiAharon/PyIntervalTree