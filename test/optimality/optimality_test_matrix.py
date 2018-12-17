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
from intervaltree import IntervalTree, Interval
from test import data
from copy import deepcopy
from pprint import pprint
from test.progress_bar import ProgressBar

try:
    xrange
except NameError:
    xrange = range


class OptimalityTestMatrix(object):
    def __init__(self, ivs=None, verbose=False):
        """
        Initilize a test matrix. To run it, see run().
        :param ivs: A dictionary mapping each test name to its
        iterable of Intervals.
        :type ivs: None or dict of [str, list of Interval]
        :param verbose: Whether to print the structure of the trees
        :type verbose: bool
        """
        self.verbose = verbose

        # set test_tupes
        self.test_types = {}
        # all methods beginning with "test_"
        test_names = [
            name for name in self.__class__.__dict__
            if
            callable(getattr(self, name)) and
            name.startswith('test_')
        ]
        for test_name in test_names:
            key = test_name[len('test_'):]
            key = ' '.join(key.split('_'))
            test_function = getattr(self, test_name)
            self.test_types[key] = test_function

        # set ivs
        self.ivs = {
            key: [Interval(*tup) for tup in value.data]
            for key, value in data.__dict__.items()
            if 'copy_structure' not in key and hasattr(value, 'data')
        }

        # initialize result matrix
        self.result_matrix = {
            'ivs name': {},
            'test type': {}
        }
        for name in self.ivs:
            self.result_matrix['ivs name'][name] = {}
        for name in self.test_types:
            self.result_matrix['test type'][name] = {}
        self.summary_matrix = deepcopy(self.result_matrix)

    def test_init(self, ivs):
        t = IntervalTree(ivs)
        return t

    def test_add_ascending(self, ivs):
        if self.verbose:
            pbar = ProgressBar(len(ivs))
        t = IntervalTree()
        for iv in sorted(ivs):
            t.add(iv)
            if self.verbose: pbar()
        return t

    def test_add_descending(self, ivs):
        if self.verbose:
            pbar = ProgressBar(len(ivs))
        t = IntervalTree()
        for iv in sorted(ivs, reverse=True):
            t.add(iv)
            if self.verbose: pbar()
        return t

    def test_prebuilt(self, tree):
        if isinstance(tree, IntervalTree):
            return tree
        return None  # N/A

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
                if report:
                    self.summary_matrix[report_type][name] = stats(report)
                elif report_type == "test type":
                    del self.test_types[name]
        return self.result_matrix

    def tabulate(self):
        """
        Store all the score results in self.result_matrix.
        """
        for test_name, test in self.test_types.items():
            for ivs_name, ivs in self.ivs.items():
                if self.verbose:
                    print("{0}: {1}".format(ivs_name, test_name))
                tree = test(ivs)
                if not tree:
                    continue
                score = tree.score(True)
                if self.verbose > 1:
                    tree.print_structure()

                self.result_matrix['ivs name'][ivs_name][test_name] = score
                self.result_matrix['test type'][test_name][ivs_name] = score

    def run(self):
        self.tabulate()
        self.summarize()
        results = {
            'summary': self.summary_matrix,
            'results': self.result_matrix,
        }
        return results

if __name__ == "__main__":
    from test.intervaltrees import trees
    matrix = OptimalityTestMatrix()
    matrix.run()
    pprint(matrix.summary_matrix)

    matrix = OptimalityTestMatrix({
        'ivs': trees['ivs1'](),
    })
    matrix.run()
    pprint(matrix.summary_matrix)
    # pprint(matrix.result_matrix)
