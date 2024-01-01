#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
#import import_ipynb
import sys
sys.path.append('../')  # Go up two folders to the project root

import structures.DocumentIndex as doc_ind
import structures.LexiconRow as lex_row
from building_data_structures.CollectionStatistics import  Collection_statistics
from structures.DocumentIndexRow import DocumentIndexRow
from structures.LexiconRow import LexiconRow


# In[3]:


DIR_DOC_INDEX="../building_data_structures/DOC_INDEX"
PATH_DOC_INDEX = "document_index.bin"

class Scoring:
    upper_bound_TF: float
    upper_bound_DL: float
    doc_index_row = DocumentIndexRow(0, "0", "")
    
    def __init__(self,collectionStatistic: Collection_statistics):
        self.collection_statistics=collectionStatistic
        self.avgDL = self.collection_statistics.get_average_Document_Length()
        #self.open_files()

    def open_files(self):
        self.file_DocIndex = open(DIR_DOC_INDEX+"/"+PATH_DOC_INDEX, 'rb')

    def close_files(self):
        self.file_DocIndex.close()  

    def choose_scoring_function(self, choice: str, doc_id: int, term_freq:int, dft:int):
        return self.compute_BM25_term(doc_id, term_freq, dft) if choice == "bm25" else self.compute_TFIDF(term_freq, dft)
    
    def compute_BM25_term(self, doc_id: int, term_freq:int, dft:int, k1:float = 1.6, b:float = 0.75)-> float:            
        if doc_id < 0 or term_freq <= 0:
            raise ValueError("doc_id and term_freq must be positive")
            
        # print("Sono dentro BM25, doc_id e term_freq e dft: ", doc_id, term_freq, dft)
        idf = self.compute_IDFT(dft)
        # print("idf è venuto: ", idf)
        log_tf = (1 + math.log(term_freq))
        # print("log_tf è venuto: ", log_tf)
        
        self.doc_index_row.read_doc_index_row_on_disk(self.file_DocIndex, doc_id*self.doc_index_row.SIZE_DOC_INDEX_ROW)
        doc_len = self.doc_index_row.document_length 
        # print("Doc_len è: ", doc_len)

        # oppure così? (idf * term_freq)/(term_freq + k1 * ( (1 - b) + b * (doc_len/self.avgDL) ))
        return (idf * log_tf)/(log_tf + k1 * ( (1 - b) + b * (doc_len/self.avgDL) )) # funziona meglio così ma non è la formula giusta

    def compute_IDFT(self, dft:int) -> float:
        """
        Compute the inverse document frequency for a term based on the document index (doc_index) and document frequency (dft).
    
        Args:
            dft: The document frequency of the term.
        """
        if dft <= 0:
            raise ValueError("Invalid parameters.")
        # print("Dentro compute_idft, self.collection_statistics.num_documents e dft: ", self.collection_statistics.num_documents, dft)
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
    
    

    def compute_term_upper_bound_bm25(self,lexicon_row:LexiconRow,k1:float = 1.6, b:float = 0.75)->float:
        """
            This function compute the final upper bound of the term using the BM25 formula.
            Args:
                lexicon_row: the term on which to compute the bm25 upperbound.
        """

        return (lexicon_row.idft * lexicon_row.BM25Tf)  / ( lexicon_row.BM25Tf + k1 * (1 - b + b * lexicon_row.BM25Dl/self.avgDL));
    
    
    


# In[ ]:




