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

    # run through the transcripts.
    for record in screed.open(transcripts):
        counts = []                     # not norm by exon count
        counts2 = []                    # norm by exon count
        counts3 = []                    # aligned & norm by exon count
        
        seq = record.sequence.replace('N', 'A')
        x, y, z = ct_reads.get_median_count(seq)
        if x == 0:                      # skip
            continue

        # first, do straight k-mer distribution
        for kmer in kmers(seq, K):
            exon_count = ct_exon.get(kmer)
            if exon_count:
                count = ct_reads.get(kmer)
                
                counts.append(count)
                counts2.append(count / float(exon_count))

        # next, do aligned k-mer distribution, normalized
        score, alignment, _, trunc = aligner.align(seq)
        alignment = alignment.replace('-', '')
        for pos in range(len(alignment) - K + 1):
            kmer = alignment[pos:pos + K]
            
            exon_count = ct_exon.get(kmer)
            if exon_count:
                count = ct_reads.get(kmer)
                counts3.append(count / float(exon_count))

        # calculate summaries
        avg = sum(counts) / float(len(counts))
        avg2 = sum(counts2) / float(len(counts))
        
        avg3 = 0.0
        if counts3:
            avg3 = sum(counts3) / float(len(counts3))

        # check to see if the alignment was truncated; set to numerical
        if trunc:
            trunc = 1
        else:
            trunc = 0

        # output!
        print record.name, avg, avg2, avg3, trunc, len(seq), len(alignment)


if __name__ == '__main__':
    main()
