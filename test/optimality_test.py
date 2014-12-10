"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: IntervalTree optimality

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
"""
from __future__ import absolute_import
from test.optimality_test_matrix import OptimalityTestMatrix
from pprint import pprint

matrix = OptimalityTestMatrix()
matrix.run()

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
    test_ivs2()
    test_ivs3()
    pprint(matrix.summary_matrix)