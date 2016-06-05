# Shakespeare - Social Network Analysis
## Introduction
This repository holds both the Python and R code used to analyze some of Shakespeare's plays for the *Special Lecture: 
Shakespeare - A Celebration in Style* at the Heidelberg University English Department on June 06, 2016.

The code was hacked together in a few hours and is, as of now, adequately terrible - use at your own 'risk'.

## Usage
Firstly, you need to download the *Shakespeare Corpus* from [lexically.net](http://lexically.net/wordsmith/support/shakespeare.html). Afterwards, you have to re-encode the files to UTF-8. This can be achieved, for example, by using *iconv*.

You can either analyze inidividual files by running `python ShakespeareSnaAnalysis.py filename.txt` or a complete folder of files by running `python runCorpus.py`. Make sure to set the `corpus_dir` in *runCorpus.py* correctly. Results will be stored in *./results*.

After all files have been processed you can run *SNAGraph.R* in R to generate graphical representations of the networks using igraph. As in the case of *runCorpus.py*, before running you should make some basic settings within the file.