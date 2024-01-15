#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import shutil
import struct

import math
from collections import defaultdict, Counter
from collections import OrderedDict
from typing import List, TextIO, BinaryIO

#import import_ipynb
import sys
sys.path.append('../')  # Go up two folders to the project root

from structures.LexiconRow import LexiconRow
from structures.DocumentIndex import DocumentIndex
from utilities.General_Utilities import Singleton
from building_data_structures.CollectionStatistics import Collection_statistics


# In[ ]:


class Lexicon:    
    def __init__(self, capacity:int,path_lexicon:str="../building_data_structures/LEXICON/lexicon.bin",path_collection_statistic:str="../building_data_structures/DOC_INDEX/collection_statistics.bin"):
        self.capacity = capacity
        self._vocabulary = OrderedDict()
        
        
        self.collectionStatistics = Collection_statistics(path_collection_statistic)
        self.collectionStatistics.read_binary_mode()
        
        #This open just one time the lexicon file specified
        self.file_lexicon=open(path_lexicon, 'rb')
        

    def add_term(self, lex_row: LexiconRow) -> None:
        if lex_row.term not in self._vocabulary:
            if len(self._vocabulary) >= self.capacity:
                self._vocabulary.popitem(last=False) # delete less recent element

            self._vocabulary[lex_row.term] = lex_row

    def get_terms(self, term: str) -> LexiconRow:
        """Fetches a row to the lexicon"""
        return self._vocabulary.get(term, None)

    def is_empty(self)->bool:
        """Check if there is no term in the lexicon."""
        return len(self.get_structure())==0

    def clear_structure(self):
        """ It clears the lexicon data structure."""
        self._vocabulary.clear()
    
    def get_structure(self):
        """Returns the lexicon data structure."""
        return self._vocabulary 
    
    def close_file(self):
        """Closes the opened lexicon file."""
        self.file_lexicon.close()

    def find_entry(self,term: str) -> LexiconRow:
        """Perform binary search to find a lexicon entry for a given term.

        Args:
            term: The term to search for in the lexicon.
    
        Returns:
            The LexiconRow object if the term is found, otherwise None.
        """
        entry = LexiconRow("",0)  
        start = 0 
        
        # "end" is equal (at the beginning) to the total number of distinct terms in the lexicon
        end = self.collectionStatistics.num_distinct_terms - 1  
    
        while start <= end:
            mid = start + (end - start) // 2
            
            # Get entry from disk
            entry.read_lexicon_row_on_disk_from_opened_file(self.file_lexicon, mid * entry.SIZE_LEXICON_ROW_FINAL)
            key = entry.term.strip()
            
            # Check if the search was successful
            if key == term:
                return entry
    
            # Update search portion parameters
            if term > key:
                start = mid + 1
            else:
                end = mid - 1
    
        return None

    def get_entry(self, term: str) -> LexiconRow:
        entry = self.get_terms(term) # check if term is in cache
        if entry is not None:
            return entry
            
        entry = self.find_entry(term)
        
        if entry is not None:         # add to cache
            self.add_term(entry)
        
        return entry


# In[4]:


#Esempio di utilizzo:
# vocabulary_cache = Lexicon(2)
# vocabulary_cache.get_entry("happiness")
# print(vocabulary_cache.get_structure())
# print("\n")

# vocabulary_cache.get_entry("dog")
# print(vocabulary_cache.get_structure())
# print("\n")

# vocabulary_cache.get_entry("cat")
# print(vocabulary_cache.get_structure())
# print("\n")

