'''
Interval tree functionality tuned for genomic data.

One of the major uses for Interval tree data structures is in bioinformatics, where the
intervals correspond to genes or other features of the genome.

As genomes typically consist of a set of *chromosomes*, a separate interval tree for each
chromosome has to be maintained. Thus, rather than using an IntervalTree, you would typically use
something like ``defaultdict(IntervalTree)`` to index data of genomic features.
This module offers a ``GenomeIntervalTree`` data structure, which is a similar convenience
data structure. In addition to specific methods for working with genomic intervals it also
provides facilities for reading BED files and the refGene table from UCSC.

Copyright 2014, Konstantin Tretyakov

Licensed under MIT [This particular file, PyIntervalTree in general is licensed under LGPL].
'''
try:
    from urllib import urlopen
    from StringIO import StringIO as BytesIO
except ImportError: # Python 3?
    from urllib.request import urlopen
    from io import BytesIO

import zlib
import warnings
from collections import defaultdict
from intervaltree import Interval, IntervalTree

class UCSCTable(object):
    '''A container class for the parsing functions, used in GenomeIntervalTree.from_table``.'''
    
    KNOWN_GENE_FIELDS = ['name', 'chrom', 'strand', 'txStart', 'txEnd', 'cdsStart', 'cdsEnd', 'exonCount', 'exonStarts', 'exonEnds', 'proteinID', 'alignID']
    REF_GENE_FIELDS = ['bin', 'name', 'chrom', 'strand', 'txStart', 'txEnd', 'cdsStart', 'cdsEnd', 'exonCount', 'exonStarts', 'exonEnds', 'score', 'name2', 'cdsStartStat', 'cdsEndStat', 'exonFrames']
    ENS_GENE_FIELDS = REF_GENE_FIELDS
    
    @staticmethod
    def KNOWN_GENE(line):
        return dict(zip(UCSCTable.KNOWN_GENE_FIELDS, line.split(b'\t')))
    @staticmethod
    def REF_GENE(line):
        return dict(zip(UCSCTable.REF_GENE_FIELDS, line.split(b'\t')))
    @staticmethod
    def ENS_GENE(line):
        return dict(zip(UCSCTable.ENS_GENE_FIELDS, line.split(b'\t')))


def _fix(interval):
    '''
    Helper function for ``GenomeIntervalTree.from_bed and ``.from_table``.
    
    Data tables may contain intervals with begin >= end. Such intervals lead to infinite recursions and
    other unpleasant behaviour, so something has to be done about them. We 'fix' them by simply setting end = begin+1.
    '''
    warnings.warn("Interval with reversed coordinates (begin >= end) detected when reading data. Interval was automatically fixed to point interval [begin, begin+1).")
    if interval.begin >= interval.end:
        return Interval(interval.begin, interval.begin+1, interval.data)
    else:
        return interval

class GenomeIntervalTree(defaultdict):
    '''
    The data structure maintains a set of IntervalTrees, one for each chromosome.
    It is essentially a ``defaultdict(IntervalTree)`` with a couple of convenience methods
    for reading various data formats.
    
    Examples::
    
        >>> gtree = GenomeIntervalTree()
        >>> gtree.addi('chr1', 0, 100)
        >>> gtree.addi('chr1', 1, 100)
        >>> gtree.addi('chr2', 0, 100)
        >>> len(gtree)
        3
        >>> len(gtree['chr1'])
        2
        >>> sorted(gtree.keys())
        ['chr1', 'chr2']
        
    '''
    def __init__(self):
        super(GenomeIntervalTree, self).__init__(IntervalTree)
    
    def addi(self, chrom, begin, end, data=None):
        self[chrom].addi(begin, end, data)
        
    def __len__(self):
        return sum([len(tree) for tree in self.values()])

    @staticmethod
    def from_bed(fileobj, field_sep=b'\t'):
        '''
        Initialize a ``GenomeIntervalTree`` from a BED file.
        Each line of the file must consist of several fields, separated using ``field_sep``.
        The first three fields are ``chrom``, ``start`` and ``end`` (where ``start`` is 0-based and
        the corresponding interval is ``[start, end)``). The remaining fields are ``name``, ``score``,
        ``strand``, ..., or something else, depending on the flavor of the format.
        
        Each Interval in the tree has its data field set to a list with "remaining" fields,
        i.e. interval.data[0] should be the ``name``, interval.data[1] is the ``score``, etc.
        
        Example::
            >>> test_url = 'http://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeAwgTfbsUniform/wgEncodeAwgTfbsBroadDnd41Ezh239875UniPk.narrowPeak.gz'
            >>> data = zlib.decompress(urlopen(test_url).read(), 16+zlib.MAX_WBITS)
            >>> gtree = GenomeIntervalTree.from_bed(BytesIO(data))
            >>> len(gtree)
            1732
            >>> assert gtree[b'chr10'].search(22610878) == set([Interval(22610878, 22611813, [b'.', b'1000', b'.', b'471.725544438908', b'-1', b'3.21510858105313', b'389']), Interval(22610878, 22611813, [b'.', b'791', b'.', b'123.885507169449', b'-1', b'3.21510858105313', b'596'])])
            >>> assert gtree[b'chr10'].search(22611813) == set([])
            >>> assert gtree[b'chr1'].search(145036590, 145036594) == set([Interval(145036593, 145037123, [b'.', b'247', b'.', b'38.6720804428054', b'-1', b'3.06233123683911', b'265'])])
            >>> assert gtree[b'chr10'].search(145036594, 145036595) == set([])
            
        '''
        # We collect all intervals into a set of lists, and then put them all at once into the tree structures
        # It is slightly more efficient than adding intervals one by one.
        # Moreover, the current implementation throws a "maximum recursion depth exceeded" error
        # in this case on large files (TODO)
        
        interval_lists = defaultdict(list)
        for ln in fileobj:
            if ln.endswith(b'\n'):
                ln = ln[0:-1]
            ln = ln.split(field_sep)
            interval_lists[ln[0]].append(_fix(Interval(int(ln[1]), int(ln[2]), data=ln[3:])))
        gtree = GenomeIntervalTree()
        for k, v in getattr(interval_lists, 'iteritems', interval_lists.items)():
            gtree[k] = IntervalTree(v)
        return gtree
    
    @staticmethod
    def from_table(fileobj=None, url='http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/knownGene.txt.gz',
                    parser=UCSCTable.KNOWN_GENE, mode='tx', decompress=None):
        '''
        UCSC Genome project provides several tables with gene coordinates (https://genome.ucsc.edu/cgi-bin/hgTables),
        such as knownGene, refGene, ensGene, wgEncodeGencodeBasicV19, etc.
        Indexing the rows of those tables into a ``GenomeIntervalTree`` is a common task, implemented in this method.
        
        The table can be either specified as a ``fileobj`` (in which case the data is read line by line),
        or via an ``url`` (the ``url`` may be to a ``txt`` or ``txt.gz`` file either online or locally).
        The type of the table is specified using the ``parser`` parameter. This is a function that takes a line
        of the file (with no line ending) and returns a dictionary, mapping field names to values. This dictionary will be assigned
        to the ``data`` field of each interval in the resulting tree.
        
        Finally, there are different ways genes can be mapped into intervals for the sake of indexing as an interval tree.
        One way is to represent each gene via its transcribed region (``txStart``..``txEnd``). Another is to represent using
        coding region (``cdsStart``..``cdsEnd``). Finally, the third possibility is to map each gene into several intervals,
        corresponding to its exons (``exonStarts``..``exonEnds``).
        
        The mode, in which genes are mapped to intervals is specified via the ``mode`` parameter. The value can be ``tx``, ``cds`` and
        ``exons``, corresponding to the three mentioned possiblities.
        
        The ``parser`` function must ensure that its output contains the field named ``chrom``, and also fields named ``txStart``/``txEnd`` if ``mode=='tx'``,
        fields ``cdsStart``/``cdsEnd`` if ``mode=='cds'``, and fields ``exonCount``/``exonStarts``/``exonEnds`` if ``mode=='exons'``.
        
        The ``decompress`` parameter specifies whether the provided file is gzip-compressed.
        This only applies to the situation when the url is given (no decompression is made if fileobj is provided in any case).
        If decompress is None, data is decompressed if the url ends with .gz, otherwise decompress = True forces decompression.
        
        >> knownGene = GenomeIntervalTree.from_table()
        >> len(knownGene)
        82960
        >> result = knownGene[b'chr1'].search(100000, 138529)
        >> len(result)
        1
        >> list(result)[0].data['name']
        b'uc021oeg.2'
        '''
        if fileobj is None:
            data = urlopen(url).read()
            if (decompress is None and url.endswith('.gz')) or decompress:
                data = zlib.decompress(data, 16+zlib.MAX_WBITS)
            fileobj = BytesIO(data)
        
        interval_lists = defaultdict(list)
        
        for ln in fileobj:
            if ln.endswith(b'\n'):
                ln = ln[0:-1]
            d = parser(ln)
            if mode == 'tx':
                interval_lists[d['chrom']].append(_fix(Interval(int(d['txStart']), int(d['txEnd']), d)))
            elif mode == 'cds':
                interval_lists[d['chrom']].append(_fix(Interval(int(d['cdsStart']), int(d['cdsEnd']), d)))
            elif mode == 'exons':
                exStarts = d['exonStarts'].split(b',')
                exEnds = d['exonEnds'].split(b',')
                for i in range(int(d['exonCount'])):
                    interval_lists[d['chrom']].append(_fix(Interval(int(exStarts[i]), int(exEnds[i]), d)))
            else:
                raise Exception("Parameter `mode` may only be 'tx', 'cds' or 'exons'")
                
        # Now convert interval lists into trees
        gtree = GenomeIntervalTree()
        for chrom, lst in getattr(interval_lists, 'iteritems', interval_lists.items)():
            gtree[chrom] = IntervalTree(lst)        
        return gtree
