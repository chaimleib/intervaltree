
#from intervaltree.bio import *
#import urllib
#data = urllib.urlopen("file:///C:/Users/Konstantin/Desktop/Downloads/knownGene.txt.gz").read()
#import zlib
#data = zlib.decompress(data, 16+zlib.MAX_WBITS)
#from StringIO import StringIO
#fileobj = StringIO(data)
#gtree = GenomeIntervalTree()
#parser = UCSCTable.KNOWN_GENE
#
#for ln in fileobj:
#    if ln[-1] == '\n':
#        ln = ln[0:-1]
#        d = parser(ln)
#        gtree.addi(d['chrom'], int(d['txStart']), int(d['txEnd']), d)
#
#print len(gtree)