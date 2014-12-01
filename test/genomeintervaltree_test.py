'''
Test module for GenomeIntervalTree

Copyright 2014, Konstantin Tretyakov

Licensed under MIT license.
'''
import os
try:
    from urllib import urlretrieve
except ImportError: # Python 3?
    from urllib.request import urlretrieve
from intervaltree.bio import GenomeIntervalTree, UCSCTable

def test_knownGene():
    # To speed up testing, we'll download the file and reuse the downloaded copy
    knownGene_url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/knownGene.txt.gz'

    # To speed up testing, we'll download the file and reuse the downloaded copy
    knownGene_file, headers = urlretrieve(knownGene_url)
    
    knownGene_localurl = 'file:///%s' % os.path.abspath(knownGene_file)
    knownGene = GenomeIntervalTree.from_table(
        url=knownGene_localurl,
        decompress=True
    ) # Py3 downloads .gz files to local files with names not ending with .gz
    assert len(knownGene) > 0
    result = knownGene[b'chr1'][100000:138529]
    assert len(result) == 1
    assert list(result)[0].data['name'] == b'uc021oeg.2'
    
    knownGene = GenomeIntervalTree.from_table(
        url=knownGene_localurl,
        mode='cds',
        decompress=True
    )
    assert len(knownGene) > 0
    assert not knownGene[b'chr1'][100000:138529]
    
    knownGene = GenomeIntervalTree.from_table(
        url=knownGene_localurl,
        mode='exons',
        decompress=True
    )
    assert len(knownGene) > 0
    result = sorted(knownGene[b'chr1'][134772:140566])
    assert len(result) == 3
    assert result[0].data == result[1].data
    assert result[0].data == result[2].data
    
def test_ensGene():
    # Smoke-test we can at least read ensGene.
    ensGene_url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/ensGene.txt.gz'
    ensGene = GenomeIntervalTree.from_table(
        url=ensGene_url,
        mode='cds',
        parser=UCSCTable.ENS_GENE
    )
    assert len(ensGene) > 0

def test_refGene():
    # Smoke-test for refGene
    refGene_url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/refGene.txt.gz'
    refGene = GenomeIntervalTree.from_table(
        url=refGene_url,
        mode='tx',
        parser=UCSCTable.REF_GENE
    )
    assert len(refGene) > 0


if __name__ == "__main__":
    print("known")
    test_knownGene()

    print("ens")
    test_ensGene()

    print("ref")
    test_refGene()

    print("Done.")
