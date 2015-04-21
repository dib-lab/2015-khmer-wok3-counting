NULLGRAPH=../nullgraph
KHMER=../khmer

all: simple-genome-reads.fa simple-genome-reads.fa.corr

clean:
	-rm simple-genome-reads.fa

simple-genome.fa:
	$(NULLGRAPH)/make-random-genome.py -l 1000 -s 1 > simple-genome.fa

simple-genome-reads.fa: simple-genome.fa
	$(NULLGRAPH)/make-reads.py -S 1 -e .01 -r 100 -C 100 simple-genome.fa --mutation-details simple-genome-reads.mut > simple-genome-reads.fa

simple-genome-reads.fa.corr: simple-genome-reads.fa
	$(KHMER)/sandbox/correct-errors.py -x 1e7 -N 4 -k 20 simple-genome-reads.fa

