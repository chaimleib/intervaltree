# -*- coding: utf-8 -*-
"""
Regression test for issue #127: overlaps(begin, end) on a range scanned
every boundary point in the tree (O(n) pure-python comparisons per query)
instead of only the points inside (begin, end).

300k disjoint intervals -> 600k boundary points. A miss-case query in the
unfixed code takes ~4s for 200 queries; with the boundary scan restricted
to the query range it should be under a tenth of a second.
"""
import time

from intervaltree import IntervalTree


def test_overlaps_range_scans_only_query_range():
    tree = IntervalTree.from_tuples((i * 10, i * 10 + 4) for i in range(300000))

    # sanity: semantics must be unchanged
    assert tree.overlaps(500006, 500009) is False   # range inside a pure gap
    assert tree.overlaps(500006, 500012) is True    # range reaches (500010, 500014)

    t0 = time.time()
    for _ in range(200):
        tree.overlaps(500006, 500009)
    # unfixed: ~4s (600k boundary comparisons per query)
    # fixed:    ~0.01s (only the 0-2 boundaries inside the range)
    assert time.time() - t0 < 1.0
