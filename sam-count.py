#! /usr/bin/env python
import sys
import argparse
import screed
import math

def ignore_at(iter):
    for item in iter:
        if item.startswith('@'):
            continue
        yield item

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('samfile')
    parser.add_argument('-o', '--outfile', type=argparse.FileType('w'),
                        default=sys.stdout)

    args = parser.parse_args()

    n = 0
    counts = {}

    for samline in ignore_at(open(args.samfile)):
        n += 1
        if n % 100000 == 0:
            print >>sys.stderr, '...', n

        readname, flags, refname, refpos, _, _, _, _, _, seq = \
                  samline.split('\t')[:10]
        if refname == '*' or refpos == '*':
            # (don't count these as skipped)
            continue

        counts[refname] = counts.get(refname, 0) + 1

    for k, v in counts.items():
        print >>args.outfile, k, v
        
if __name__ == '__main__':
    main()
