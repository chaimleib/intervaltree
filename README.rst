==============
PyIntervalTree
==============

    NB: This is a straight fork of `PyIntervalTree by Chaim-Leib Halbert <https://github.com/MusashiAharon/PyIntervalTree>`_.
    This fork adds some tests, fixes some bugs, registers the package at PyPI as `PyIntervalTree <https://pypi.python.org/PyIntervalTree>`_,
    adds a ``intervaltree.bio`` package with some utilities for bioinformatics needs (see below).
    Some further maintenance or updates might still be possible, and eventually the fork could merge into the original (depending on the original author's opinion).

A mutable, self-balancing interval tree. Queries may be by point, by range 
overlap, or by range envelopment.

This library was designed to allow tagging text and time intervals, where the
intervals include the lower bound but not the upper bound.

Installation
------------

The easiest way to install most Python packages is via ``easy_install`` or ``pip``::

    $ pip install PyIntervalTree

Features
--------

* Initialize blank or from an iterable of Intervals in O(n * log n).
* Insertions

  * ``tree[begin:end] = data``
  * ``tree.add(interval)``
  * ``tree.addi(begin, end, data)``
  * ``tree.extend(list_of_interval_objs)``

* Deletions

  * ``tree.remove(interval)``             (raises ``ValueError`` if not present)
  * ``tree.discard(interval)``            (quiet if not present)
  * ``tree.removei(begin, end, data)``
  * ``tree.discardi(begin, end, data)``
  * ``tree.remove_overlap(point)``
  * ``tree.remove_overlap(begin, end)``   (removes all overlapping the range)
  * ``tree.remove_envelop(begin, end)``   (removes all enveloped in the range)

* Overlap queries:

  * ``tree[point]``
  * ``tree[begin:end]``
  * ``tree.search(point)``
  * ``tree.search(begin, end)``

* Envelop queries:

  * ``tree.search(begin, end, strict = True)``

* Membership queries:

  * ``interval_obj in tree``              (this is fastest, O(1))
  * ``tree.containsi(begin, end, data)``
  * ``tree.overlaps(point)``
  * ``tree.overlaps(begin, end)``

* Iterable:

  * ``for interval_obj in tree:``
  * ``tree.items()``

* Sizing:

  * ``len(tree)``
  * ``tree.is_empty()``
  * ``not tree``
  * ``tree.begin()`` (the smallest coordinate of the leftmost interval)
  * ``tree.end()`` (the ``end`` coordinate of the rightmost interval)

* Restructuring

  * ``split_overlaps()``

* Copy- and typecast-able:

  * ``IntervalTree(tree)``    (``Interval`` objects are same as those in tree)
  * ``tree.copy()``           (``Interval`` objects are shallow copies of those in tree)
  * ``set(tree)``             (can later be fed into ``IntervalTree()``)
  * ``list(tree)``            (ditto)

* Equal-able
* Pickle-friendly
* Automatic AVL balancing
    
Examples
--------

* Getting started::

        from intervaltree import Interval, IntervalTree
        t = IntervalTree()

* Adding intervals - you don't have to use strings!::

        t[1:2] = "1-2"
        t[4:7] = "4-7"
        t[5:9] = "5-9"

* Query by point::

        ivs = t[6]            # set([Interval(4, 7, '4-7'), Interval(5, 9, '5-9')])
        iv = sorted(ivs)[0]   # Interval(4, 7, '4-7')
  
* Accessing an ``Interval`` object::

        iv.begin  # 4
        iv.end    # 7
        iv.data   # "4-7"
  
* Query by range:

  Note that ranges are inclusive of the lower limit, but non-inclusive of the
  upper limit. So::

        t[2:4]    # set([])

  But::

        t[1:5]    # set([Interval(1, 2, '1-2'), Interval(4, 7, '4-7')])

* Constructing from lists of ``Interval``'s:

  We could have made the same tree this way::

        ivs = [ [1,2], [4,7], [5,9] ]
        ivs = map( lambda begin,end: Interval(begin, end, "%d-%d" % (begin,end), 
                   *zip(*ivs) )
  
        t = IntervalTree(ivs)

* Removing intervals::

        t.remove( Interval(1, 2, "1-2") )
        list(t)     # [Interval(4, 7, '4-7'), Interval(5, 9, '5-9')]
        
        t.remove( Interval(500, 1000, "Doesn't exist") # raises ValueError
        t.discard(Interval(500, 1000, "Doesn't exist") # quietly does nothing
        
        t.remove_overlap(5)   
        list(t)     # []

  We could also empty a tree by removing all intervals, from the lowest bound
  to the highest bound of the ``IntervalTree``::
  
        t.remove_overlap(t.begin(), t.end())

Usage with Genomic Data
-----------------------

Interval trees are especially commonly used in bioinformatics, where intervals correspond to genes or various features along the genome. Such intervals are commonly stored in ``BED``-format files. To simplify working with such data, the package ``intervaltree.bio`` provides a ``GenomeIntervalTree`` class.

``GenomeIntervalTree`` is essentially a ``dict`` of ``IntervalTree``-s, indexed by chromosome names::

    gtree = GenomeIntervalTree()
    gtree['chr1'].addi(10000, 20000)
    
There is a convenience function for adding intervals::

    gtree.addi('chr2', 20000, 30000)
    
You can create a ``GenomeIntervalTree`` instance from a ``BED`` file::

    test_url = 'http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeAwgTfbsUniform/wgEncodeAwgTfbsBroadDnd41Ezh239875UniPk.narrowPeak.gz'
    data = zlib.decompress(urlopen(test_url).read(), 16+zlib.MAX_WBITS)
    gtree = GenomeIntervalTree.from_bed(StringIO(data))
    
In addition, special functions are offered to read in `UCSC tables of gene positions <https://genome.ucsc.edu/cgi-bin/hgTables>`_:

* Load the UCSC ``knownGene`` table with each interval corresponding to gene's transcribed region::

    knownGene = GenomeIntervalTree.from_table()
  
* Load the UCSC ``refGene`` table with each interval corresponding to gene's coding region::

    url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/refGene.txt.gz'
    refGene = GenomeIntervalTree.from_table(url=url, parser=UCSCTable.REF_GENE, mode='cds')
    
* Load the UCSC ``ensGene`` table with each interval corresponding to a gene's exon::

    url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/ensGene.txt.gz'
    ensGene = GenomeIntervalTree.from_table(url=url, parser=UCSCTable.ENS_GENE, mode='exons') 

You may add methods for parsing your own tabular files with genomic intervals, see the documentation for ``GenomeIntervalTree.from_table``.

Based on
--------

  * Eternally Confuzzled's `AVL tree <http://www.eternallyconfuzzled.com/tuts/datastructures/jsw_tut_avl.aspx>`_
  * Wikipedia's `Interval Tree <http://en.wikipedia.org/wiki/Interval_tree>`_
  * Heavily modified from Tyler Kahn's `Interval Tree implementation in Python <http://forrst.com/posts/Interval_Tree_implementation_in_python-e0K>`_ (`GitHub project <https://github.com/tylerkahn/intervaltree-python>`_)

Copyright
---------

  * `Chaim-Leib Halbert <https://github.com/MusashiAharon/PyIntervalTree>`_
  * This particular fork by `Konstantin Tretyakov <https://github.com/konstantint/PyIntervalTree>`_. See changes in CHANGELOG.txt.
