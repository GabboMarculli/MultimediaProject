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
            entry.read_lexicon_row_on_disk_from_opened_file(self.file_lexicon, mid * entry.SIZE_LEXICON_ROW)
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


# In[2]:


# DIR_LEXICON="../building_data_structures/LEXICON"
# PATH_FINAL_LEXICON="lexicon.bin"

# '''
# def create_lexicon(file_input_path: str, file_output_path: str, DIR_FOLDER: str, file_extension: str, block_size: int, document_index: doc_index.DocumentIndex) -> int:
#     """
#     Function returns a file with one row for each distinct term in the corpus. Rows are composed by:
#     term, document frequency, inverse document frequency, term upper bound
#     Each values is separated by a comma.

#     Args:
#         file_input_path: file that contains the inverted index
#         file_output_path: file that will contains the result
#         DIR_FOLDER: folder that will contains the output file
#         file_extension: extension of the file
#         block_size: dimension of rows in main memory
#     """
#     # Check if the input file path exists and is a file
#     if not file_input_path or not os.path.exists(file_input_path) or not os.path.isfile(file_input_path):
#         raise ValueError("Invalid file_input_path.")

#     # Check if the output folder path exists
#     if not file_output_path:
#         raise ValueError("Invalid file_output_path.")

#     # Check if DIR_FOLDER is a non-empty string
#     if not DIR_FOLDER or not isinstance(DIR_FOLDER, str):
#         raise ValueError("Invalid DIR_FOLDER.")

#     # Check if the file extension is a non-empty string
#     if not file_extension or not isinstance(file_extension, str):
#         raise ValueError("Invalid file_extension.")

#     # Check that block_size is a positive integer
#     if not isinstance(block_size, int) or block_size <= 0:
#         raise ValueError("Invalid block_size. Must be a positive integer.")

#     # Check that document_index is an instance of DocumentIndex
#     if not document_index or not isinstance(document_index, doc_index.DocumentIndex):
#         raise ValueError("Invalid document_index. Must be an instance of DocumentIndex.")
        
#     try:
#         lexicon = Lexicon()
#         create_folder(DIR_FOLDER)
#         nr_block = 0
#         if os.path.exists(DIR_FOLDER + file_output_path + str(nr_block) + file_extension):
#                 os.remove(DIR_FOLDER + file_output_path + str(nr_block) + file_extension)
            
#         with open(file_input_path, 'r') as file:
#             for line in file:
#                 # term sarà qualcosa tipo "ciao", invece la postings list sarà 3:2 3:3 ecc
#                 elements = line.split()
#                 term = elements[0]          
#                 postings_list = ' '.join(elements[1:])
                
#                 # il dft si trova facendo la split su spazi e punti e virgola di tutta la posting list
#                 dft = len(postings_list.split())

#                 # la term frequency massima
#                 max_tf = compute_max_term_frequency(postings_list)

#                 if (sys.getsizeof(lexicon.get_structure()) > block_size):  #Free memory available
#                     write_to_block(DIR_FOLDER + file_output_path + str(nr_block) + file_extension, lexicon.get_structure())
#                     lexicon.clear_structure()
#                     nr_block=nr_block + 1 

#                 lexicon.add_term(term, dft, document_index, max_tf)

#             #Finally, saving the last remaing block.       
#             if (not lexicon.is_empty()):   
#                 write_to_block(DIR_FOLDER + file_output_path + str(nr_block) + file_extension, lexicon.get_structure())

#             return 0                
#     except IOError as e:
#         print(f"Error reading from {file_input_path}: {e}")
#         return -1
# '''
     

# class Lexicon(Singleton):
#     def __init__(self):
#         self._vocabulary = defaultdict(LexiconRow)
        
#         self.collectionStatistics = Collection_statistics("../building_data_structures/DOC_INDEX/collection_statistics.bin")
#         self.collectionStatistics.read_binary_mode()

#     def add_term(self, term: str) -> None:
#         """Adds a document to the lexicon."""
#         if not isinstance(term, str):
#             raise ValueError("There's an error in parameter's type.")
            
#         # Append new row to the lexicon
#         if (self.get_terms(term)==None):
#             self._vocabulary[term]=[]
#         self._vocabulary[term] = LexiconRow(term)

#     def add_term(self, lex_row: LexiconRow) -> None:
#         if (self.get_terms(lex_row.term)==None):
#             self._vocabulary[lex_row.term]=[]
#         self._vocabulary[lex_row.term] = lex_row
             
#     def get_terms(self, term: str) -> LexiconRow:
#         """Fetches a row to the lexicon"""
#         if not isinstance(term, str):
#             raise ValueError("Term must be a string.")
            
#         if (term in self._vocabulary):
#             return self._vocabulary[term]
#         return None
    
#     def is_empty(self)->bool:
#         """Check if there is no term in the lexicon."""
#         return len(self.get_term())==0
    
#     def get_term(self) -> List[str]:
#         """Returns all unique terms in the lexicon."""
#         return self._vocabulary.keys() 
    
#     def clear_structure(self):
#         """ It clears the lexicon data structure."""
#         self._vocabulary.clear()
    
#     def get_structure(self):
#         """Returns the lexicon data structure."""
#         return self._vocabulary 

#     def find_entry(self,term: str) -> LexiconRow:
#         """Perform binary search to find a lexicon entry for a given term.

#         Args:
#             term: The term to search for in the lexicon.
    
#         Returns:
#             The LexiconRow object if the term is found, otherwise None.
#         """
#         entry = LexiconRow("",0)  
#         start = 0 
        
#         # "end" is equal (at the beginning) to the total number of distinct terms in the lexicon
#         end = self.collectionStatistics.num_distinct_terms - 1  
    
#         while start <= end:
#             mid = start + (end - start) // 2
            
#             # Get entry from disk
#             with open(DIR_LEXICON+ "/" + PATH_FINAL_LEXICON, 'rb') as file:
#                 entry.read_lexicon_row_on_disk_from_opened_file(file, mid * entry.SIZE_LEXICON_ROW)
#             key = entry.term.strip()
            
#             # Check if the search was successful
#             if key == term:
#                 return entry
    
#             # Update search portion parameters
#             if term > key:
#                 start = mid + 1
#             else:
#                 end = mid - 1
    
#         return None

#     # come svuotare la cache? vanno implementate altre funzionalità?
#     def get_entry(self, term: str) -> LexiconRow:
#         entry = self.get_terms(term) # check if term is in cache
#         if entry is not None:
#             return entry
            
#         entry = self.find_entry(term)
        
#         if entry is not None:         # add to cache
#             self.add_term(entry)
        
#         return entry


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

