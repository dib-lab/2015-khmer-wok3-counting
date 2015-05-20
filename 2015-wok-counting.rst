Abundance counting in sequence with graphalign
==============================================

`De Bruijn graph alignment
<http://ivory.idyll.org/blog/2015-wok-error-correction.html>`__ should
also be useful for exploring concepts in transcriptomics/mRNAseq
expression.  As with `variant calling
<http://ivory.idyll.org/blog/2015-wok-variant-calling.html>`__
graphalign can also be used to avoid the mapping step in
quantification; and, again, as with the variant calling approach, we
can do so by aligning our reference sequences to the graph rather than
the reads to the reference sequences.

The basic concept here is that you build a (non-abundance-normalized)
De Bruijn graph from the reads, and then align transcripts or genomic
regions to the graph and get the k-mer counts across the alignment.
This is nice because it gives you a few options for dealing with
multimapping issues as well as variation across the reference.  You
can also make use of the variant calling code to account for certain
types of genomic/transcriptomic variation and potentially address
allelic bias issues.

Given the existence of `Sailfish/Salmon
<http://nextgenseek.com/2014/04/sailfish-alignment-free-isoform-quantification-from-rna-seq-reads/>`__
and the recent posting of `Kallisto
<https://liorpachter.wordpress.com/2015/05/10/near-optimal-rna-seq-quantification-with-kallisto/>`__,
I don't want to be disingenuous and pretend that this is any way a
novel idea!  It's been clear for a long time that using De Bruijn
graphs in RNAseq quantification is a worthwhile idea.  Also, whenever
someone uses k-mers to do something in bioinformatics, there's an
overlap with De Bruijn graph concepts (...pun intended).

What we like about the graphalign code in connection with
transcriptomics is that it makes a surprisingly wide array of things
easy to do.  By eliminating or at least downgrading the "noisiness" of
queries into graphs, we can ask all sorts of questions, quickly, about
read counts, graph structure, isoforms, etc.  Moreover, by building
the graph with `error corrected reads
<http://ivory.idyll.org/blog/2015-wok-error-correction.html>`__, the
counts should in theory become more accurate.  (Note that this does have the
potential for biasing against low-abundance isoforms because
low-coverage reads can't be error corrected.)

For one simple example of the possibilities, let's compare mapping
counts (bowtie2) against transcript graph counts from the graph
(khmer) for a small subset of a mouse mRNAseq dataset.  We measure
transcript graph counts here by walking along the transcript in the
graph and averaging over k-mer counts along the path.  This is implicitly
a multimapping approach; to get results
comparable to bowtie2's default parameters, we divide out the number
of transcripts in which each k-mer appears (see count-median-norm.py@@,
'counts' vs 'counts2').

Just doing this doesn't look that good:

@@ show some counts?

However, it turns out that one reason for the poor correlation is that
there is a lot of splice isoforms in the reference transcriptome we're
using, and we're running bowtie2 in its default "random assignment" mode.
Thus the bowtie2 counts are being averaged across transcripts in weird
ways, while the graph counts are being reused multiple times (once for
each time an exon is used in any transcript).

If we correct for this, we get a much nicer looking correlation:

@@

Isoform structure and expression
--------------------------------

Another set of use cases worth thinking about is looking at isoform
structure and expression across data sets.  Currently we are somewhat
at the mercy of our reference transcriptome, unless we re-run de novo
assembly every time we get a new data set.  Since we don't do this,
for some model systems (especially emerging model organisms) isoform
families may or may not correspond well to the information in the
individual samples.  This leads to strange-looking situations where
specific transcripts have high coverage in one region and low coverage
in another (See `SAMmate <http://arxiv.org/abs/1208.3619>`__ for a
good overview of this problem.)

Consider the situation where a gene with four exons, 1-2-3-4,
expresses isoform 1-2-4 in tissue A, but expresses 1-3-4 in tissue B.
If the transcriptome is built only from data from tissue A, then when
we map reads from tissue B to the transcriptome, exon 2 will have no
coverage and counts from exon 3 will (still) be missing.  This can
lead to poor sensitivity in detecting low-expressed genes, weird
differential splicing results, and other scientific mayhem.

(Incidentally, it should be clear from this discussion that it's kind
of insane to build "a transcriptome" once - what we really want do is
build a graph of all relevant RNAseq data where the paths and counts
are labeled with information about the source sample.  If only we had
a way of efficiently labeling our graphs in khmer! Alas, alack!)

With graph alignment approaches, we can short-circuit the currently
common ( mapping-to-reference->summing up counts->looking at isoforms
) approach, and go directly to looking directly at counts along the
transcript path.  Again, this is something that Kallisto and Salmon
also enable, but there's a lot of unexplored territory here.

@@ show counts along sim 
@@ show counts along mouse paths;
@@ show diffs w/in mouse by exon (?)
@@ note errors, allelic differences.

Exon structure
--------------

If we can probe the structure of the De Bruijn graph directly with an
alignment based approach, we can readily distinguish exonic
boundaries@@ (align reads x reads?)  We can also quantify features
across all the reads, and cross examine expression grouped by tissue
or cell type by just loading those specific reads into the graph.
(Or, we can use labeled De Bruijn graphs, aka "colored" DBG; more on
that later.)

@@ align transcripts x gmc graph.
@@ note: errors/allelic differences

We can also discover exon boundaries by aligning all the transcripts
to all the transcripts.  (It turns out that when you design your data
structures to handle billions of reads, they often scale pretty well
to hundreds of thousands of transcripts.)

@@ align transcripts to transcripts graph
@@ note: errors, allelic differences

----

Other thoughts --

* all of this can be used on metagenomes as well, for straight
  abundance counting as well as analysis of strain variation.  This is
  of great interest to us.

