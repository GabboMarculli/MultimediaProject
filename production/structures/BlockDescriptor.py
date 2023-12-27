#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import shutil
import struct

import math
from collections import defaultdict, Counter
from typing import List
from typing import TextIO, BinaryIO
import sys


# In[ ]:


class BlockDescriptorBuilder:
    
    def __init__(self,path_collection_statistics:str):
        #Todo leggersi il file di collection statistic per determinare il numero dopo il quale si va a gestire
        #la posting list su più di un blocco.
        
        self.min_posting_list_size=512
    
    def get_number_of_blocks(self,nr_postings:int):
        
        
        if (nr_postings<self.min_posting_list_size):
            return 1
        
        #The strategy is to use as default block size the squared root of the length of the posting list
        return math.ceil(math.sqrt(nr_postings))
    


# In[ ]:


open


# In[9]:


class BlockDescriptor:
    
    STR_SIZE_BLOCK_DESCRIPTOR='2q 5i'
    SIZE_BLOCK_DESCRIPTOR=struct.calcsize(STR_SIZE_BLOCK_DESCRIPTOR)
    
    offset_doc_ids:int
    offset_freqs:int 
        
    nr_postings:int    
        
    doc_ids_bytes_size:int
    freq_bytes_size:int    
        
    min_doc_id:int
    max_doc_id:int
        
        
    def __init__(self,nr_postings:int=0,offset_doc_ids:int=0,offset_freqs:int=0,doc_ids_bytes_size:int=0,freq_bytes_size:int=0,min_doc_id:int=0,max_doc_id:int=0):
        """ Costructor method for istantiation of a Block Descriptor
        
        Args:
            nr_postings: the number of posting contained in the block
            offset_doc_ids: the starting offset of the doc_ids file
            offset_freqs: the startign offset of the freqs file
            doc_ids_bytes_size: the dimension in byte of the doc_ids contained in the block 
            freq_bytes_size: the dimension in byte of the freqs contained in the block 
            min_doc_id: the minimum doc id contained in the block, used for d-gap decompression
            max_doc_id: the maximum doc id contained in the block, used for skipping to next block
            
        """
        self.nr_postings=nr_postings
        
        self.offset_doc_ids=offset_doc_ids
        self.offset_freqs=offset_freqs
        
        self.doc_ids_bytes_size=doc_ids_bytes_size
        self.freq_bytes_size=freq_bytes_size
        
        self.min_doc_id=min_doc_id
        self.max_doc_id=max_doc_id
        
        
    def write_block_descriptor_on_disk_to_opened_file(self,file:BinaryIO,offset:int=0):
        """This function writes on a specific position of an opened file a block descriptor .
           
           Args:
               file: the file to store the block descriptor
               offset: the position inside the file to store the block descriptor
           Returns:
               the new offset free position after writing on the file
        """
        file.seek(offset)
       
        binary_data = struct.pack(self.STR_SIZE_BLOCK_DESCRIPTOR, self.offset_doc_ids,self.offset_freqs,self.nr_postings,
                                 self.doc_ids_bytes_size,self.freq_bytes_size,self.min_doc_id,self.max_doc_id)
        file.write(binary_data)
            
        return self.SIZE_BLOCK_DESCRIPTOR+offset
    
    
    def read_block_descriptor_on_disk_from_opened_file(self,file:BinaryIO,offset:int):
        """This function reads a block descriptor information in a specific position from an opened file.
        
        Args:
            file: the file to read a block descriptor
            offset: the position inside the file to read the block descriptor
        
        Returns:
            the offset position after reading
            
        """
        file.seek(offset)  
        bytesLetti = file.read(self.SIZE_BLOCK_DESCRIPTOR) 
        
        if(not bytesLetti):
            return None
        
        self.offset_doc_ids,self.offset_freqs,self.nr_postings,self.doc_ids_bytes_size,self.freq_bytes_size,self.min_doc_id,self.max_doc_id= struct.unpack(self.STR_SIZE_BLOCK_DESCRIPTOR, bytesLetti)
        
        return offset+self.SIZE_BLOCK_DESCRIPTOR
    
    
#USED FOR DEBUGGING
    
    def write_block_descriptor_on_disk(self,file_path:str,offset:int=0):
        """This function opens a file and writes on a specific position a block descriptor information.
            This is used for debug and tests.
        
            Args:
               file_path: the file to store the block descriptor
               offset: the position inside the file to store the block descriptor
            Returns:
                the new offset free position after writing
               
        """
        with open(file_path, 'ab') as file:
            return self.write_block_descriptor_on_disk_to_opened_file(file,offset)
            
    def read_block_descriptor_on_disk(self,file_path:str,offset:int):
        """This function opens a file and reads in a specific position a block descriptor information.
            This is used for debug and tests.
        
            Args:
               file_path: the file to read a lexicon row
               offset: the position inside the file to read the block descriptor
            Returns:
                the offset position after reading
        """
        with open(file_path, 'rb') as file:
            return self.read_block_descriptor_on_disk_from_opened_file(file,offset) 
        
        
    


# In[3]:


#Short tests.
#a=BlockDescriptor(5,15,31,10,11,1,15)
#a.write_block_descriptor_on_disk("prova.bin",0)
#b=BlockDescriptor()
#b.read_block_descriptor_on_disk("prova.bin",0)

