#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os

from typing import List,Iterator
from typing import TextIO, BinaryIO
import sys

#import import_ipynb
import sys
sys.path.append('../')  

from structures.InvertedIndex import Posting,InvertedIndex
from structures.LexiconRow import LexiconRow
from structures.BlockDescriptor import BlockDescriptor


# In[2]:


"""The aim of this class is to handle the entire posting list that can be partially on memory and partial on disk.
   This class exends the classical concept of the iterator in Python in order to hide all the details of the implementation
   about loading other postings from disk.
"""
class Posting_List_Reader:
    
    lexicon_elem:LexiconRow
        
    __block_descriptors:List[BlockDescriptor]
    __posting_list:Iterator[Posting]
    
    file_doc_ids:BinaryIO
    file_freqs: BinaryIO
    file_blocks: BinaryIO
    compression_mode: bool
        
    __block_index:int
    
    __current_posting: Posting
    
    def __init__(self,lexiconRow:LexiconRow,compression_mode:bool,file_doc_ids:BinaryIO,file_freqs:BinaryIO,file_blocks:BinaryIO):
        """ Costructor method:
            Args:
            lexiconRow: the lexicon element related that we want to read the posting list
            compression_mode: the modality in which the posting list is saved
            file_doc_ids: the file from which loading the doc_ids of the posting list
            file_freqs: the file from which loading the freqs of the posting list
            file_blocks: the file from which loading the blocks of the posting list
        
        """
        self.lexicon_elem=lexiconRow
        
        self.compression_mode=compression_mode
        
        self.file_doc_ids=file_doc_ids
        self.file_freqs=file_freqs
        self.file_blocks=file_blocks
        self.__current_posting=None
        
        self.__block_descriptors=[]
        self.__posting_list=iter([])
        
        #Saving immediatly the information about all the blocks of a posting in memory.
        for i in range(0,self.lexicon_elem.numBlocks):
            block=BlockDescriptor()
            block.read_block_descriptor_on_disk_from_opened_file(self.file_blocks,self.lexicon_elem.blockOffset + (block.SIZE_BLOCK_DESCRIPTOR*i))
            self.__block_descriptors.append(block)
                 
        self.__block_index=-1
    
    def __iter__(self):
        return self
 
    def __update_posting_list__(self):
        """
            This function loads from disk the part of the posting list of the next block if available.
        """
        current_block=self.get_current_block()
        if (current_block!=None and self.__block_index<len(self.__block_descriptors)):
            # print("Leggo da disco effettivamente")
            lista,_,_=iter(InvertedIndex.read_from_files_a_posting_list(self.file_doc_ids,
                                                                 self.file_freqs,
                                                                 self.compression_mode,
                                                                 current_block.offset_doc_ids,
                                                                 current_block.offset_freqs,
                                                                 current_block.nr_postings,
                                                                 current_block.doc_ids_bytes_size,
                                                                 current_block.freq_bytes_size,
                                                                 current_block.min_doc_id
                                                            ))
            self.__posting_list=iter(lista)
            
    def __next__(self):
        """
            This method returns the next element in the posting list updating the current one.
        """  
        self.__current_posting=next(self.__posting_list,None)
        
        if (self.__current_posting==None and self.__block_index<len(self.__block_descriptors)):
            
            self.__block_index+=1
            self.__update_posting_list__()
            self.__current_posting=next(self.__posting_list,None)
            if (self.__current_posting==None):
                raise StopIteration()
        return self.__current_posting
    
    def get_total_blocks(self):
        """ This method returns the total number of blocks in for a specific lexicon term."""
        return len(self.__block_descriptors)
    
    def get_current_block(self):
        """ This method returns the current block information for a specific lexicon term."""
        if (self.__block_index<0 or self.__block_index>=len(self.__block_descriptors)):
            return None
        return self.__block_descriptors[self.__block_index]
    
    def get_current_posting(self):
        """ This method returns the current posting of a posting list."""
        return self.__current_posting

    def nextGEQ(self, doc_id: int):
        """ 
         This method is used to skip the posting list to a specific element with greater or equal doc_id passed as argument.
         Args:
             doc_id: the doc_id to skip to
        """
        # flag to check if the block has changed
        block_changed = False

        # move to the block with max_doc_id >= doc_id
        # current block is None only if it's the first read
        while self.get_current_block() is None or self.get_current_block().max_doc_id < doc_id:
            # end of list, return None
            if self.__block_index >= len(self.__block_descriptors) - 1:
                self.__current_posting = None
                return None

            self.__block_index += 1
            block_changed = True

        if self.get_current_block() is not None:
            self.__update_posting_list__()

        # block changed, load postings and update iterator
        if block_changed:
            # remove previous postings
            self.__current_posting = next(self.__posting_list, None)
        
        # move to the first posting greater or equal then docid and return it
        while self.__current_posting is not None and self.__current_posting.doc_id < doc_id:
            self.__current_posting = next(self.__posting_list, None)
        
        return self.__current_posting
          

