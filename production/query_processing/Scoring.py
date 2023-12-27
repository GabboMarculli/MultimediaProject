#!/usr/bin/env python
# coding: utf-8

# In[2]:


import math
#import import_ipynb
import sys
sys.path.append('../')  # Go up two folders to the project root

import structures.DocumentIndex as doc_ind
import structures.LexiconRow as lex_row
from building_data_structures.CollectionStatistics import  Collection_statistics
from structures.DocumentIndexRow import DocumentIndexRow


# In[2]:


DIR_DOC_INDEX="../building_data_structures/DOC_INDEX"
PATH_DOC_INDEX = "document_index.bin"

class Scoring:
    upper_bound_TF: float
    upper_bound_DL: float
    doc_index_row = DocumentIndexRow(0, "","")
    
    def __init__(self,collectionStatistic: Collection_statistics):
        self.collection_statistics=collectionStatistic
        self.avgDL = self.collection_statistics.get_average_Document_Length()
        #self.open_files()

    def open_files(self):
        self.file_DocIndex = open(DIR_DOC_INDEX+"/"+PATH_DOC_INDEX, 'rb') # POTREBBE ESSERCI UN BUG QUANDO LO CREO ALL'INIZIO NELL' INDEX BUILDER PERCHE IL FILE NON ESISTE ANCORA

    def close_files(self):
        self.file_DocIndex.close()  

    def choose_scoring_function(self, choice: str, doc_id: int, term_freq:int):
        # Problema: come passare dft alla computeTFIDF? possibile soluzione: nella initialize_posting_lists leggo il term_lexicon_row, lì è presente.
        # Basterebbe salvarsela in quel momento
        return self.compute_BM25_term(doc_id, term_freq) if choice == "bm25" else self.compute_TFIDF(term_freq)
    
    def compute_BM25_term(self, doc_id: int, term_freq:int, k1:float = 1.6, b:float = 0.75)-> float:            
        if doc_id < 0 or term_freq <= 0:
            raise ValueError("doc_id and term_freq must be positive")
            
        idf = self.compute_IDFT(term_freq)
        log_tf = (1 + math.log(term_freq))
        
        self.doc_index_row.read_doc_index_row_on_disk(self.file_DocIndex, doc_id*self.doc_index_row.SIZE_DOC_INDEX_ROW)
        doc_len = self.doc_index_row.document_length 
    
        return (idf * log_tf)/(log_tf + k1 * ( (1 - b) + b * (doc_len/self.avgDL) ))

    def compute_IDFT(self, dft:int) -> float:
        """
        Compute the inverse document frequency for a term based on the document index (doc_index) and document frequency (dft).
    
        Args:
            dft: The document frequency of the term.
        """
        if dft <= 0:
            raise ValueError("Invalid parameters.")

        return math.log10(self.collection_statistics.num_documents/dft)  


    def compute_TFIDF(self, tf: int, dft: int) -> float:
        """
        Compute the TF-IDF value based on the term frequency (tf) and inverse document frequency (idf).
        
        Args:
            tf: An integer representing the term frequency.
            idf: A float representing the inverse document frequency.
        """    
        if tf <= 0:
            return 0
            
        return (1 + math.log10(tf)) * self.compute_IDFT(dft)

    
    '''
    def compute_BM25_query(query:str, doc_id: int, idf: float) -> float:
        bm25 = 0.0
        
        # remove duplicates
        tokens = list(set(query.split()))
        
        for token in tokens:
            #term_freq =  come si trova la term frequencies? bisogna recuperare la postings list dal doc_index?
            bm25 = bm25 + compute_BM25_term(doc_index, doc_id, term_freq)
    
        return bm25
    '''


# In[ ]:




