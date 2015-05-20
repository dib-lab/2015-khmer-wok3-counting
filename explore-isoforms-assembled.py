#! /usr/bin/env python
import khmer
import screed
import argparse

K=21

parser = argparse.ArgumentParser()
parser.add_argument('transcripts')
args = parser.parse_args()

ct = khmer.new_counting_hash(K, 1e6, 4)
aligner = khmer.ReadAligner(ct, 2, 1.0)
ct2 = khmer.new_counting_hash(K, 1e6, 4)

# first, read in all of the sequences => a graph (ct)
ct.consume_fasta(args.transcripts)

# second, read in all the sequences & build a consensus graph (in ct2)
for record in screed.open(args.transcripts):
    counts = []

    # correct 'seq' against the first-round graph
    seq = record.sequence.replace('N', 'A')
    score, alignment, read, trunc = aligner.align(seq)
    alignment = alignment.replace('-', '')
    ct2.consume(alignment)

# third, read in all the sequences again, and look for exon boundaries
# using the readaligner.
aligner2 = khmer.ReadAligner(ct2, 2, 1.0)

for record in screed.open(args.transcripts):
    seq = record.sequence.replace('N', 'A')
    score, alignment, read, trunc = aligner2.align(seq)
    print 'xx', record.name, alignment[222:222 + K]
    
    for pos in range(len(alignment) - K + 1):
        kmer = alignment[pos:pos + K]
        n = ct2.get(kmer)
        counts.append(n)

    #print record.name,
    #for n in counts:
    #    print n,
    #print

    # do edge detection
    pos = K
    last_count = ct2.get(alignment[pos:pos+K])
    boundaries = []
    while pos < len(alignment) - K + 1:
        count = ct2.get(alignment[pos:pos+K])
        if count != last_count:
            print record.name, last_count, count, pos, len(alignment)
            last_count = count
            boundaries.append(pos)

        pos += 1

    print boundaries
