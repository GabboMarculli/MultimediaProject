Before starting to utilize any program: be sure to have downloaded the NLTK stopword.
You can do that executing the following line of code:

import nltk
nltk.download('stopwords')


To run the test follow these steps:
1) Go to folder \production\run 
2) Execute the command python .\exec_testing.py


To run the building of the all datastructures
(Lexicon, Doc.Index, Inv.Index, Coll.Stats.):

1) Put in the folder \production\run your compressed original collection
2) Rename it as collection.tar.gz
3) Execute the command python .\exec_indexing.py
4) Follow the "wizard" to configure the indexing according to your memory capability and necessity:
4.1) Decide if using or not Stemming and Stop Word remouval and/or Compression to save space on disk
4.2) Decide if using Debug mode to print a human readable file to check the correctness of the produced data structures
   