curl https://s3.amazonaws.com/public.ged.msu.edu/2015-wok/rseq-mapped.fq.gz | \
      gunzip -c | head -3166748 | \
      gzip -9c > rseq-mapped.fq.gz

curl https://s3.amazonaws.com/public.ged.msu.edu/2015-wok/rseq-corr.fq.gz | \
      gunzip -c | head -3166748 |
      gzip -9c > rseq-corr.fq.gz

curl https://s3.amazonaws.com/public.ged.msu.edu/2014-paper-streaming/mouse-ref.fa.gz \
        | gunzip -c \
        > rna.fa
