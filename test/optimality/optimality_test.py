"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree optimality

Copyright 2013-2018 Chaim Leib Halbert

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
from __future__ import absolute_import
from pprint import pprint
from warnings import warn

from test.optimality.optimality_test_matrix import OptimalityTestMatrix
from test import data


matrix = OptimalityTestMatrix(verbose=1)
matrix.run()


def test_ivs1():
    """
    Small, but has overlaps.
    """
    report = matrix.result_matrix['ivs name']['ivs1']
    prev_score = 0.375
    worst = 0.0
    for test in matrix.test_types:
        # score of this test
        score = report[test]['_cumulative']

        # update worst score
        if score > worst:
            worst = score

        # make sure we did at least as well as before's worst-case
        assert score <= prev_score
        assert 0.0 == report[test]['depth']

    if worst < prev_score:  # worst-case has improved!
        warn(IntervalTree.from_tuples(data.ivs1.data).print_structure(True))
        warn("ivs1 scored {0} < {1} worst-case, better than expected!".format(
            score,
            prev_score
        ))


def test_ivs2():
    """
    No gaps, no overlaps.
    """
    report = matrix.result_matrix['ivs name']['ivs2']
    assert 0.0 == report['add ascending']['_cumulative']
    assert 0.0 == report['add descending']['_cumulative']
    assert 0.0 == report['init']['_cumulative']

def test_ivs3():
    """
    Gaps, no overlaps.
    """
    report = matrix.result_matrix['ivs name']['ivs2']
    assert 0.0 == report['add ascending']['_cumulative']
    assert 0.0 == report['add descending']['_cumulative']
    assert 0.0 == report['init']['_cumulative']


if __name__ == "__main__":
    test_ivs1()
    test_ivs2()
    test_ivs3()
    pprint(matrix.summary_matrix)
    pprint(matrix.result_matrix)
