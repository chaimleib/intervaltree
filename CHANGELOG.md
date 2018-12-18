# Change log

## Version 3.0.2
- Fixed:
    - On some systems, setup.py opened README.md with a non-unicode encoding. My fault for leaving the encoding flapping in the breeze. It's been fixed.

## Version 3.0.1
- Added:
    - Travis testing for 3.7 and 3.8-dev. These needed OpenSSL, sudo and Xenial. 3.8-dev is allowed to fail.
- Fixed:
    - PyPI wasn't rendering markdown because I didn't tell it what format to use.
    - Python 2 wasn't installing via pip because of a new utils package. It has been zapped.
- Maintainers:
    - TestPyPI version strings use `.postN` as the suffix instead of `bN`, and `N` counts from the latest tagged commit, which should be the last release
    - Install from TestPyPI works via `make install-testpypi`

## Version 3.0.0
- Breaking:
    - `search(begin, end, strict)` has been replaced with `at(point)`, `overlap(begin, end)`, and `envelop(begin, end)`
    - `extend(items)` has been deleted, use `update(items)` instead
    - Methods that take a `strict=True/False` argument now consistently default to `strict=True`
    - Dropped support for Python 2.6, 3.2, and 3.3
    - Add support for Python 3.5, 3.6, and 3.7
- Faster `Interval` overlap checking (@tuxzz, #56)
- Updated README:
    - new restructuring methods from 2.1.0
    - example of `from_tuples()` added
    - more info about `chop()`, `split_overlaps()`, `merge_overlaps()` and `merge_equals()`.
- Fixes:
    - `Node.from_tuples()` will now raise an error if given an empty iterable. This should never happen, and it should error if it does.
    - `Interval.distance_to()` gave an incorrect distance when passed the `Interval`'s upper boundary
    - `Node.pop_greatest_child()` sometimes forgot to `rotate()` when creating new child nodes. (@escalonn, #41, #42)
    - `IntervalTree.begin()` and `end()` are O(1), not O(n). (@ProgVal, #40)
    - `intersection_update()` and `symmetric_difference()` and `symmetric_difference_update()` didn't actually work. Now they do.
    - `collections.abc` deprecation warning no longer happens
- Maintainers:
    - PyPi accepts Markdown! Woohoo!
    - reorganize tests
    - more tests added to improve code coverage (We're at 96%! Yay!)
    - test for issue #4 had a broken import reference

## Version 2.1.0
- Added:
    - `merge_overlaps()` method and tests
    - `merge_equals()` method and tests
    - `range()` method
    - `span()` method, for returning the difference between `end()` and `begin()`
- Fixes:
    - Development version numbering is changing to be compliant with PEP440. Version numbering now contains major, minor and micro release numbers, plus the number of builds following the stable release version, e.g. 2.0.4b34
    - Speed improvement: `begin()` and `end()` methods used iterative `min()` and `max()` builtins instead of the more efficient `iloc` member available to `SortedDict`
    - `overlaps()` method used to return `True` even if provided null test interval
- Maintainers:
    - Added coverage test (`make coverage`) with html report (`htmlcov/index.html`)
    - Tests run slightly faster

## Version 2.0.4
- Fix: Issue #27: README incorrectly showed using a comma instead of a colon when querying the `IntervalTree`: it showed `tree[begin, end]` instead of `tree[begin:end]`

## Version 2.0.3
- Fix: README showed using + operator for setlike union instead of the correct | operator
- Removed tests from release package to speed up installation; to get the tests, download from GitHub

## Version 2.0.2
- Fix: Issue #20: performance enhancement for large trees. `IntervalTree.search()` made a copy of the entire `boundary_table` resulting in linear search time. The `sortedcollections` package is now the sole install dependency

## Version 2.0.1
- Fix: Issue #26: failed to prune empty `Node` after a rotation promoted contents of `s_center`

## Version 2.0.0
- `IntervalTree` now supports the full `collections.MutableSet` API
- Added:
    - `__delitem__` to `IntervalTree`
    - `Interval` comparison methods `lt()`, `gt()`, `le()` and `ge()` to `Interval`, as an alternative to the comparison operators, which are designed for sorting
    - `IntervalTree.from_tuples(iterable)`
    - `IntervalTree.clear()`
    - `IntervalTree.difference(iterable)`
    - `IntervalTree.difference_update(iterable)`
    - `IntervalTree.union(iterable)`
    - `IntervalTree.intersection(iterable)`
    - `IntervalTree.intersection_update(iterable)`
    - `IntervalTree.symmetric_difference(iterable)`
    - `IntervalTree.symmetric_difference_update(iterable)`
    - `IntervalTree.chop(a, b)`
    - `IntervalTree.slice(point)`
- Deprecated `IntervalTree.extend()` -- use `update()` instead
- Internal improvements:
    - More verbose tests with progress bars
    - More tests for comparison and sorting behavior
    - Code in the README is included in the unit tests
- Fixes
    - BACKWARD INCOMPATIBLE: On ranged queries where `begin >= end`, the query operated on the overlaps of `begin`. This behavior was documented as expected in 1.x; it is now changed to be more consistent with the definition of `Interval`s, which are half-open.
    - Issue #25: pruning empty Nodes with staggered descendants could result in invalid trees
    - Sorting `Interval`s and numbers in the same list gathered all the numbers at the beginning and the `Interval`s at the end
    - `IntervalTree.overlaps()` and friends returned `None` instead of `False`
    - Maintainers: `make install-testpypi` failed because the `pip` was missing a `--pre` flag

## Version 1.1.1
- Removed requirement for pyandoc in order to run functionality tests.

## Version 1.1.0
- Added ability to use `Interval.distance_to()` with points, not just `Intervals`
- Added documentation on return types to `IntervalTree` and `Interval`
- `Interval.__cmp__()` works with points too
- Fix: `IntervalTree.score()` returned maximum score of 0.5 instead of 1.0. Now returns max of subscores instead of avg
- Internal improvements:
    - Development version numbering scheme, based on `git describe` the "building towards" release is appended after a hyphen, eg. 1.0.2-37-g2da2ef0-1.10. The previous tagged release is 1.0.2, and there have been 37 commits since then, current tag is g2da2ef0, and we are getting ready for a 1.1.0 release
    - Optimality tests added
    - `Interval` overlap tests for ranges, `Interval`s and points added

## Version 1.0.2
-Bug fixes:
    - `Node.depth_score_helper()` raised `AttributeError`
    - README formatting

## Version 1.0.1
- Fix: pip install failure because of failure to generate README.rst

## Version 1.0.0
- Renamed from PyIntervalTree to intervaltree
- Speed improvements for adding and removing Intervals (~70% faster than 0.4)
- Bug fixes:
    - BACKWARD INCOMPATIBLE: `len()` of an `Interval` is always 3, reverting to default behavior for `namedtuples`. In Python 3, `len` returning a non-integer raises an exception. Instead, use `Interval.length()`, which returns 0 for null intervals and `end - begin` otherwise. Also, if the `len() === 0`, then `not iv` is `True`.
    - When inserting an `Interval` via `__setitem__` and improper parameters given, all errors were transformed to `IndexError`
    - `split_overlaps` did not update the `boundary_table` counts
- Internal improvements:
    - More robust local testing tools
    - Long series of interdependent tests have been separated into sections

## Version 0.4
- Faster balancing (~80% faster)
- Bug fixes:
    - Double rotations were performed in place of a single rotation when presented an unbalanced Node with a balanced child.
    - During single rotation, kept referencing an unrotated Node instead of the new, rotated one

## Version 0.3.3
- Made IntervalTree crash if inited with a null Interval (end <= begin)
- IntervalTree raises ValueError instead of AssertionError when a null Interval is inserted

## Version 0.3.2
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

## Version 0.2.3
- Slight changes for inclusion in PyPI.
- Some documentation changes
- Added tests
- Bug fix: interval addition via [] was broken in Python 2.7 (see http://bugs.python.org/issue21785)
- Added intervaltree.bio subpackage, adding some utilities for use in bioinformatics

## Version 0.2.2b
- Forked from https://github.com/MusashiAharon/PyIntervalTree
