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
from intervaltree import IntervalTree
from test import intervals
from copy import deepcopy
from pprint import pprint
try:
    xrange
except NameError:
    xrange = range


class OptimalityTestMatrix(object):
    def __init__(self, ivs_names=None, verbose=False):
        self.verbose = verbose

        # set test_tupes
        self.test_types = {}
        tests = [
            name for name in self.__class__.__dict__
            if
            callable(getattr(self, name)) and
            name.startswith('test_')
        ]
        for test in tests:
            name = test[len('test_'):]
            name = ' '.join(name.split('_'))
            test_function = self.bind_test_function(test)
            self.test_types[name] = test_function

        # set ivs
        self.ivs = intervals.ivs_data.copy()
        for name in list(self.ivs):
            if 'copy_structure' in name:
                del self.ivs[name]

        # set result matrix
        self.result_matrix = {
            'ivs name': {},
            'test type': {}
        }
        for name in self.ivs:
            self.result_matrix['ivs name'][name] = {}
        for name in self.test_types:
            self.result_matrix['test type'][name] = {}
        self.summary_matrix = deepcopy(self.result_matrix)

    def bind_test_function(self, function_name):
        function = getattr(self.__class__, function_name)
        def test_function(ivs):
            return function(self, ivs)
        return test_function

    def test_init(self, ivs):
        t = IntervalTree(ivs)
        return t

    def test_add_ascending(self, ivs):
        t = IntervalTree()
        for iv in sorted(ivs):
            t.add(iv)
        return t

    def test_add_descending(self, ivs):
        t = IntervalTree()
        for iv in sorted(ivs, reverse=True):
            t.add(iv)
        return t

    def register_score(self, ivs_name, test_type, score):
        self.result_matrix['ivs name'][ivs_name][test_type] = score
        self.result_matrix['test type'][test_type][ivs_name] = score

    def summarize(self):
        def stats(report):
            assert isinstance(report, dict)
            cumulatives = [test['_cumulative'] for test in report.values()]
            return {
                'mean': sum(cumulatives) / len(cumulatives),
                'worst': max(cumulatives),
                'best': min(cumulatives),
            }
        for report_type in self.result_matrix:
            for name, report in self.result_matrix[report_type].items():
                self.summary_matrix[report_type][name] = stats(report)
        return self.result_matrix


    def run(self):
        for test_name, test in self.test_types.items():
            for ivs_name, ivs in self.ivs.items():
                tree = test(ivs)
                score = tree.score(True)

                if self.verbose:
                    print("{0}: {1}".format(ivs_name, test_name))
                    tree.print_structure()

                self.register_score(ivs_name, test_name, score)

        self.summarize()
        results = {
            'summary': self.summary_matrix,
            'results': self.result_matrix,
        }
        return results

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
    pprint(matrix.summary_matrix)
    pprint(matrix.result_matrix)
