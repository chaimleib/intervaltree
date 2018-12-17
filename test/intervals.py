"""
intervaltree: A mutable, self-balancing interval tree for Python 2 and 3.
Queries may be by point, by range overlap, or by range envelopment.

Test module: utilities to generate intervals

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
from intervaltree import Interval
from pprint import pprint
from random import randint, choice
from test.progress_bar import ProgressBar
import os
try:
    xrange
except NameError:
    xrange = range

try:
    unicode
except NameError:
    unicode = str

def make_iv(begin, end, label=False):
    if label:
        return Interval(begin, end, "[{0},{1})".format(begin, end))
    else:
        return Interval(begin, end)


def nogaps_rand(size=100, labels=False):
    """
    Create a random list of Intervals with no gaps or overlaps
    between the intervals.
    :rtype: list of Intervals
    """
    cur = -50
    result = []
    for i in xrange(size):
        length = randint(1, 10)
        result.append(make_iv(cur, cur + length, labels))
        cur += length
    return result


def gaps_rand(size=100, labels=False):
    """
    Create a random list of intervals  with random gaps, but no
    overlaps between the intervals.

    :rtype: list of Intervals
    """
    cur = -50
    result = []
    for i in xrange(size):
        length = randint(1, 10)
        if choice([True, False]):
            cur += length
            length = randint(1, 10)
        result.append(make_iv(cur, cur + length, labels))
        cur += length
    return result


def overlaps_nogaps_rand(size=100, labels=False):
    l1 = nogaps_rand(size, labels)
    l2 = nogaps_rand(size, labels)
    result = set(l1) | set(l2)
    return list(result)


def write_ivs_data(name, ivs, docstring='', imports=None):
    """
    Write the provided ivs to test/name.py.
    :param name: file name, minus the extension
    :type name: str
    :param ivs: an iterable of Intervals
    :type ivs: collections.i
    :param docstring: a string to be inserted at the head of the file
    :param imports: executable code to be inserted before data=...
    """
    def trepr(s):
        """
        Like repr, but triple-quoted. NOT perfect!

        Taken from http://compgroups.net/comp.lang.python/re-triple-quoted-repr/1635367
        """
        text = '\n'.join([repr(line)[1:-1] for line in s.split('\n')])
        squotes, dquotes = "'''", '"""'
        my_quotes, other_quotes = dquotes, squotes
        if my_quotes in text:
            if other_quotes in text:
                escaped_quotes = 3*('\\' + other_quotes[0])
                text = text.replace(other_quotes, escaped_quotes)
            else:
                my_quotes = other_quotes
        return "%s%s%s" % (my_quotes, text, my_quotes)

    data = [tuple(iv) for iv in ivs]
    with open('test/data/{0}.py'.format(name), 'w') as f:
        if docstring:
            f.write(trepr(docstring))
            f.write('\n')
        if isinstance(imports, (str, unicode)):
            f.write(imports)
            f.write('\n\n')
        elif isinstance(imports, (list, tuple, set)):
            for line in imports:
                f.write(line + '\n')
            f.write('\n')

        f.write('data = \\\n')
        pprint(data, f)


if __name__ == '__main__':
#     ivs = gaps_rand()
#     write_ivs_data('ivs3', ivs, docstring="""
# Random integer ranges, with gaps.
# """
#     )
    pprint(ivs)
