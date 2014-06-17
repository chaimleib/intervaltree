'''
Test module for GenomeIntervalTree

Copyright 2014, Konstantin Tretyakov

Licensed under MIT license.
'''
import os
from urllib import urlretrieve
from intervaltree.bio import GenomeIntervalTree, UCSCTable

def test_knownGene():
    # To speed up testing, we'll download the file and reuse the downloaded copy
    knownGene_url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/knownGene.txt.gz'
    # Mirror. Slightly faster, I believe:
    #knownGene_url = 'http://kt.era.ee/tmp/knownGene.txt.gz'

    # To speed up testing, we'll download the file and reuse the downloaded copy
    knownGene_file, headers = urlretrieve(knownGene_url)
    
    knownGene_localurl = 'file:///%s' % os.path.abspath(knownGene_file)
    knownGene = GenomeIntervalTree.from_table(url=knownGene_localurl)
    assert len(knownGene) == 82960
    result = knownGene['chr1'].search(100000, 138529)
    assert len(result) == 1
    assert list(result)[0].data['name'] == 'uc021oeg.2'
    
    knownGene = GenomeIntervalTree.from_table(url=knownGene_localurl, mode='cds')
    assert len(knownGene) == 82960
    assert not knownGene['chr1'].overlaps(100000, 138529)
    
    knownGene = GenomeIntervalTree.from_table(url=knownGene_localurl, mode='exons')
    assert len(knownGene) == 742493
    result = list(knownGene['chr1'].search(134772, 140566))
    assert len(result) == 3
    assert result[0].data == result[1].data and result[0].data == result[2].data
    
def test_ensGene():
    # Smoke-test we can at least read ensGene.
    ensGene_url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/ensGene.txt.gz'
    #ensGene_url = 'http://kt.era.ee/tmp/ensGene.txt.gz'
    ensGene = GenomeIntervalTree.from_table(url=ensGene_url, mode='cds', parser=UCSCTable.ENS_GENE)
    assert len(ensGene) == 204940

def test_refGene():
    # Smoke-test for refGene
    refGene_url = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/database/refGene.txt.gz'
    #refGene_url = 'http://kt.era.ee/tmp/refGene.txt.gz'
    refGene = GenomeIntervalTree.from_table(url=refGene_url, mode='tx', parser=UCSCTable.REF_GENE)
    assert len(refGene) == 50919 
