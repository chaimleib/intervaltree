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
from intervaltree import Interval, IntervalTree
from pprint import pprint

def optimality():
    def make_interval(lst):
        return Interval(lst[0], lst[1], "{0}-{1}".format(*lst))

    ivs = [make_interval(iv) for iv in [
        [1, 2],
        [4, 7],
        [5, 9],
        [6, 10],
        [8, 10],
        [8, 15],
        [10, 12],
        [12, 14],
        [14, 15],
    ]]
    t = IntervalTree(ivs)
    t.print_structure()
    pprint(t.score(True), width=20)


if __name__ == "__main__":
    optimality()
