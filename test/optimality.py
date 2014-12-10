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
import test.intervals as intervals
from pprint import pprint
try:
    xrange
except NameError:
    xrange = range


IVS_NAMES = [
    '1',
]


TEST_TYPES = [
    'init',
    'add ascending',
    'add descending',
]

class OptimalityTestMatrix(object):
    def __init__(self, ivs_names=None):
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
        self.ivs = {}
        if not ivs_names:
            ivs_names = [
                name for name in intervals.__dict__
                if
                callable(getattr(intervals, name)) and
                name.startswith('ivs')
            ]
        for name in ivs_names:
            generate_ivs =  getattr(intervals, name)
            self.ivs[name] = generate_ivs()

        # set result matrix
        self.result_matrix = {
            'ivs name': {},
            'test type': {}
        }
        for name in self.ivs:
            self.result_matrix['ivs name'][name] = {}
        for name in self.test_types:
            self.result_matrix['test type'][name] = {}

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
        def awb(report):
            assert isinstance(report, dict)
            cumulatives = [test['_cumulative'] for test in report.values()]
            report.update({
                '_average': sum(cumulatives) / len(cumulatives),
                '_worst': max(cumulatives),
                '_best': min(cumulatives),
            })
        for report_type in self.result_matrix:
            for report in self.result_matrix[report_type].values():
                awb(report)
        return self.result_matrix


    def run(self):
        for test_name, test in self.test_types.items():
            for ivs_name, ivs in self.ivs.items():
                print("{0}: {1}".format(ivs_name, test_name))
                tree = test(ivs)
                tree.print_structure()

                score = tree.score(True)
                self.register_score(ivs_name, test_name, score)

        return self.summarize()



if __name__ == "__main__":
    matrix = OptimalityTestMatrix()
    pprint(matrix.run())
