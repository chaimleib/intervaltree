Change log
==========

Version 2.0.0
-------------
- `IntervalTree` now supports the full `MutableMapping` and `MutableSet` APIs from the `collections` module
- Added `__delitem__` to `IntervalTree`
- Added comparison methods `lt()`, `gt()`, `le()` and `ge()` to `Interval`, as an alternative to the comparison operators, which are designed for sorting
- Added `IntervalTree.empty()`
- Internal improvements:
    - More verbose tests with progress bars
    - More automatic test harnesses
    - More tests for comparison and sorting behavior
- Fixes
    - BACKWARD INCOMPATIBLE: When deleting or searching over ranges were begin >= end, deleted or searched over the overlaps of begin. This behavior was documented as expected in 1.x; it is now changed to be more consistent with the definition of `Interval`s, which are half-open
    - Sorting `Interval`s and numbers in the same list gathered all the numbers at the beginning and the `Interval`s at the end
    - `IntervalTree.overlaps()` and friends returned None instead of False
    - Maintainers: `make install-testpypi` failed because the `pip` was missing a `--pre` flag

Version 1.1.1
-------------
- Removed requirement for pyandoc in order to run functionality tests.

Version 1.1.0
-------------
- Added ability to use `Interval.distance_to()` with points, not just `Intervals`
- Added documentation on return types to `IntervalTree` and `Interval`
- `Interval.__cmp__()` works with points too
- Fix: `IntervalTree.score()` returned maximum score of 0.5 instead of 1.0. Now returns max of subscores instead of avg
- Internal improvements:
    - Development version numbering scheme, based on `git describe` the "building towards" release is appended after a hyphen, eg. 1.0.2-37-g2da2ef0-1.10. The previous tagged release is 1.0.2, and there have been 37 commits since then, current tag is g2da2ef0, and we are getting ready for a 1.1.0 release
    - Optimality tests added
    - `Interval` overlap tests for ranges, `Interval`s and points added

Version 1.0.2
-------------
-Bug fixes:
    - `Node.depth_score_helper()` raised `AttributeError`
    - README formatting

Version 1.0.1
-------------
- Fix: pip install failure because of failure to generate README.rst

Version 1.0.0
-------------
- Renamed from PyIntervalTree to intervaltree
- Speed improvements for adding and removing Intervals (~70% faster than 0.4)
- Bug fixes:
    - BACKWARD INCOMPATIBLE: `len()` of an `Interval` is always 3, reverting to default behavior for `namedtuples`. In Python 3, `len` returning a non-integer raises an exception. Instead, use `Interval.length()`, which returns 0 for null intervals and `end - begin` otherwise. Also, if the `len() === 0`, then `not iv` is `True`.
    - When inserting an `Interval` via `__setitem__` and improper parameters given, all errors were transformed to `IndexError`
    - `split_overlaps` did not update the `boundary_table` counts
- Internal improvements:
    - More robust local testing tools
    - Long series of interdependent tests have been separated into sections

Version 0.4
-------------

- Faster balancing (~80% faster)
- Bug fixes:
    - Double rotations were performed in place of a single rotation when presented and unbalanced Node with a balanced child.
    - During single rotation, kept referencing an unrotated Node instead of the new, rotated one

Version 0.3.3
-------------

- Made IntervalTree crash if inited with a null Interval (end <= begin)
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
