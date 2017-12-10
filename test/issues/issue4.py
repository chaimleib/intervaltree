'''
PyIntervalTree issue #4 test
https://github.com/konstantint/PyIntervalTree/issues/4

Test contributed by jacekt
'''
from __future__ import absolute_import
from intervaltree import IntervalTree
from test.progress_bar import ProgressBar
from test import data
items = data.issue4.data
MAX = data.issue4.MAX
from test.intervals import write_ivs_data
from test.optimality.optimality_test_matrix import OptimalityTestMatrix
from pprint import pprint
import cProfile
import pstats


def test_build_tree():
    pbar = ProgressBar(len(items))

    tree = IntervalTree()
    tree[0:MAX] = None
    for b, e, alloc in items:
        if alloc:
            ivs = tree[b:e]
            assert len(ivs)==1
            iv = ivs.pop()
            assert iv.begin<=b and e<=iv.end
            tree.remove(iv)
            if iv.begin<b:
                tree[iv.begin:b] = None
            if e<iv.end:
                tree[e:iv.end] = None
        else:
            ivs = tree[b:e]
            assert not ivs
            prev = tree[b-1:b]
            assert len(prev) in (0, 1)
            if prev:
                prev = prev.pop()
                b = prev.begin
                tree.remove(prev)
            next = tree[e:e+1]
            assert len(next) in (0, 1)
            if next:
                next = next.pop()
                e = next.end
                tree.remove(next)
            tree[b:e] = None
        pbar()
    tree.verify()
    return tree


def optimality_core():
    #tree = test_build_tree()
    #write_result(tree)
    #print(len(tree))
    matrix = OptimalityTestMatrix({
        'issue4result': IntervalTree.from_tuples(data.issue4_result.data),
    })
    pprint(matrix.summary_matrix)


def optimality():
    cProfile.run('optimality_core()', 'restats')
    print_restats()


def profile():
    cProfile.run('test_build_tree()', 'restats')
    print_restats()


def print_restats():
    p = pstats.Stats('restats')
    p.sort_stats('cumulative').print_stats()


def write_result(tree):
    write_ivs_data('issue4_result', tree, docstring='''
Result tree data from test/issue4.py.
''')


def write_items():
    items = [(begin, end, data) for data, begin, end in items]
    write_ivs_data('issue4', items, docstring = """
Source data for test/issue4. Very long!
""", imports='MAX = %d' % MAX)


if __name__ == '__main__':
    # optimality()
    profile()
