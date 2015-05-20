NULLGRAPH=../nullgraph
KHMER=../khmer

all: simple-mrna-reads.fa rseq-mapped.counts rseq-mapped.meds rseq-corr.meds2 \
	rseq-mapped.meds2

clean:
	-rm simple-mrna-reads.fa *.graph

simple-mrna-reads.fa: simple-mrna.fa
	$(NULLGRAPH)/make-biased-reads.py -S 1 -e .01 -r 100 -C 100 simple-mrna.fa --mutation-details simple-mrna-reads.mut > simple-mrna-reads.fa

simple-mrna-reads.sam: simple-mrna-reads.fa
	bowtie2-build simple-mrna.fa simple-mrna > /dev/null
	samtools faidx simple-mrna.fa

	bowtie2 -f -x simple-mrna -U simple-mrna-reads.fa -S simple-mrna-reads.sam

sim.graph: simple-mrna-reads.fa
	load-into-counting.py -k 21 -x 2e4 -N 4 sim.graph simple-mrna-reads.fa

sim_exon.graph: simple-mrna.fa
	load-into-counting.py -k 21 -x 2e4 -N 4 sim_exon.graph simple-mrna.fa

sim.meds2: simple-mrna.fa sim_exon.graph sim.graph
	./count-median-norm.py sim.graph sim_exon.graph simple-mrna.fa > sim.meds2

sim.meds: simple-mrna.fa sim.graph
	count-median.py sim.graph simple-mrna.fa sim.meds

sim.counts: simple-mrna-reads.sam
	./sam-count.py simple-mrna-reads.sam -o sim.counts

rseq.1.bt2: rna.fa
	bowtie2-build rna.fa rseq > /dev/null
	samtools faidx rna.fa

rseq-mapped.sam: rseq-mapped.fq.gz rseq.1.bt2
	gunzip -c rseq-mapped.fq.gz | bowtie2 -p 4 -x rseq -U - -S rseq-mapped.sam

rseq-mapped.counts: rseq-mapped.sam
	./sam-count.py rseq-mapped.sam -o rseq-mapped.counts

rseq-mapped.graph: rseq-mapped.fq.gz
	load-into-counting.py -k 21 -x 1e8 -N 4 rseq-mapped.graph rseq-mapped.fq.gz

rna_exon.graph: rna.fa
	load-into-counting.py -k 21 -x 8e7 -N 4 rna_exon.graph rna.fa

rseq-mapped.meds: rna.fa rseq-mapped.graph
	count-median.py rseq-mapped.graph rna.fa rseq-mapped.meds

rseq-mapped.meds2: rna.fa rna_exon.graph rseq-mapped.graph
	./count-median-norm.py rseq-mapped.graph rna_exon.graph rna.fa > rseq-mapped.meds2

rseq-corr.graph: rseq-corr.fq.gz
	load-into-counting.py -k 21 -x 8e7 -N 4 rseq-corr.graph rseq-corr.fq.gz 

rseq-corr.meds2: rseq-corr.graph rna_exon.graph
	./count-median-norm.py rseq-corr.graph rna_exon.graph rna.fa > rseq-corr.meds2
