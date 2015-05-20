#! /usr/bin/env python2
#
# This file is part of khmer, https://github.com/dib-lab/khmer/, and is
# Copyright (C) Michigan State University, 2009-2015. It is licensed under
# the three-clause BSD license; see LICENSE.
# Contact: khmer-project@idyll.org
#
# pylint: disable=missing-docstring,invalid-name
"""
Adapted from count-median.py in khmer 1.4
"""
import screed
import argparse
import sys
import csv
import textwrap

import khmer
from khmer.kfile import check_input_files, check_space
from khmer.khmer_args import info


def kmers(seq, K):
    for pos in range(0, len(seq) - K + 1):
        yield seq[pos:pos+K]


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('ct_reads')
    parser.add_argument('ct_exon')
    parser.add_argument('transcripts')

    return parser


def main():
    args = get_parser().parse_args()

    # reads counting table
    ct_reads = khmer.load_counting_hash(args.ct_reads)

    # transcripts counting table
    ct_exon = khmer.load_counting_hash(args.ct_exon)

    # transcripts themselves
    transcripts = args.transcripts

    K = ct_reads.ksize()
    assert ct_exon.ksize() == K

    # build a read aligner against, well, the reads:
    aligner = khmer.ReadAligner(ct_reads, 1, 1.0)

    # pick up a list of sequences to pay attention to
    searchlist = set([ x.strip() for x in open('seq-profiles.list') ])

    # run through the transcripts.
    for record in screed.open(transcripts):
        if record.name.split(' ')[0] not in searchlist:
            continue
        print 'found!', record.name.split(' ')[0]
        
        counts = []                     # not norm by exon count
        counts2 = []                    # norm by exon count
        
        seq = record.sequence.replace('N', 'A')

        for kmer in kmers(seq, K):
            exon_count = ct_exon.get(kmer)
            if exon_count:
                count = ct_reads.get(kmer)
                
                counts.append(count)
                counts2.append(count / float(exon_count))

        filename = record.name.split(' ')[0] + '.kprofile'
        fp = open(filename, 'w')
        for n, (c1, c2) in enumerate(zip(counts, counts2)):
            print >>fp, n, c1, c2


if __name__ == '__main__':
    main()
