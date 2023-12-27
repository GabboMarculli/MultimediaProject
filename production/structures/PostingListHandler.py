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
        
        self.lexicon_elem=lexiconRow
        
        self.compression_mode=compression_mode
        
        self.file_doc_ids=file_doc_ids
        self.file_freqs=file_freqs
        self.file_blocks=file_blocks
        self.__current_posting=None
        
        self.__block_descriptors=[]
        self.__posting_list=iter([])
         
        for i in range(0,self.lexicon_elem.numBlocks):
            block=BlockDescriptor()
            block.read_block_descriptor_on_disk_from_opened_file(self.file_blocks,block.SIZE_BLOCK_DESCRIPTOR*i)
            self.__block_descriptors.append(block)
                 
        self.__block_index=-1
    
    def __iter__(self):
        return self
 
    def __update_posting_list__(self):
        
        current_block=self.get_current_block()
        if (current_block!=None and self.__block_index<len(self.__block_descriptors)):
            print("Leggo da disco effettivamente")
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
           
        self.__current_posting=next(self.__posting_list,None)
        
        if (self.__current_posting==None and self.__block_index<len(self.__block_descriptors)):
            
            self.__block_index+=1
            self.__update_posting_list__()
            self.__current_posting=next(self.__posting_list,None)
            if (self.__current_posting==None):
                raise StopIteration()
        return self.__current_posting
    
    
    def get_current_block(self):
        if (self.__block_index<0 or self.__block_index>=len(self.__block_descriptors)):
            return None
        return self.__block_descriptors[self.__block_index]
    
    def get_current_posting(self):
        return self.__current_posting
          


# In[3]:


# DIR_TEMP_FOLDER="TEMP"
# DIR_TEMP_DOC_ID="DOC_ID_TEMP"
# DIR_TEMP_FREQ="FREQ_TEMP"
# DIR_TEMP_LEXICON="LEXICON_TEMP"

# DIR_LEXICON="../building_data_structures/LEXICON"
# DIR_DOC_INDEX="../building_data_structures/DOC_INDEX"
# DIR_INVERTED_INDEX="../building_data_structures/INV_INDEX"

# PATH_FINAL_LEXICON="lexicon.bin"
# PATH_FINAL_DOC_IDS="doc_ids.bin"
# PATH_FINAL_FREQ="freq.bin"
# PATH_FINAL_BLOCK_DESCRIPTOR="block_descriptors.bin"
# PATH_COLLECTION_STATISTICS="collection_statistics.txt"

# PATH_FINAL_INVERTED_INDEX_DEBUG="inverted_index.txt"
# PATH_FINAL_LEXICON_DEBUG="lexicon.txt"
# PATH_FINAL_DOCUMENT_INDEX="document_index.txt"


# In[4]:


# file_lex=open(DIR_LEXICON+"/"+PATH_FINAL_LEXICON, 'rb') 
# file_doc=open(DIR_INVERTED_INDEX+"/"+PATH_FINAL_DOC_IDS, 'rb') 
# file_freq=open(DIR_INVERTED_INDEX+"/"+PATH_FINAL_FREQ, 'rb')
# file_blocks=open(DIR_INVERTED_INDEX+"/"+PATH_FINAL_BLOCK_DESCRIPTOR, 'rb')



# lexTerm=LexiconRow("",0)
# lexTerm.read_lexicon_row_on_disk_from_opened_file(file_lex,0)

# posting_reader=Posting_List_Reader(lexTerm,False,file_doc,file_freq,file_blocks)


# In[9]:


# for i in range (12):
#     ris=next(posting_reader)
#     print(ris)


# In[5]:


# for obj in posting_reader:
#     print (obj)


# In[6]:


# posting_reader.get_current_posting()


# In[6]:


# file_lex.close()
# file_doc.close()
# file_freq.close()
# file_blocks.close()


# In[4]:


# iterator=iter(posting_list)


# In[7]:


# a=next(iterator,None)
# print(a)


# In[10]:


# import time

# start_time = time.time()
# #my_iter = iter(range(1000000))
# my_iter=list(range(1000000))
# for x in my_iter:
#     x=x+1
# end_time=time.time()

# print("\n\n"+str(end_time-start_time))


# In[9]:


# range(100000)


# In[3]:


# aa=iter([Posting(1,2),Posting(2,3),Posting(3,4)])


# In[9]:


# next(aa)


# In[11]:


# getsizeof(list(range(1000000)))


# In[12]:


# # Get the byte occupancy
# byte_size_list = sys.getsizeof(list(range(1000000)))
# byte_size_iter = sys.getsizeof(iter(range(1000000)))


# In[38]:


# print(byte_size_list,byte_size_iter)


# In[19]:


# # Generate a list of 100,000 integers
# integer_list = [i for i in range(10000000)]

# # Specify the file name
# file_name = "integer_list.txt"

# # Open the file in write mode
# with open(file_name, "w") as file:
#     # Write each integer to a new line
#     for integer in integer_list:
#         file.write(f"{integer}\n")

# print(f"List of 10 000 000 integers has been saved to {file_name}")


# In[22]:


# def read_integer_list(file_name):
#     """Read a file containing integers (one per line) and return a list of integers."""
#     print("PASSO DA QUI!!")
#     with open(file_name, "r") as file:
#         integer_list = [int(line.strip()) for line in file]
#     print (integer_list[:10])
#     print (len(integer_list))
#     print (sys.getsizeof(integer_list))
#     return integer_list


# In[23]:


# start_time = time.time()

# lista_letta_da_disco=read_integer_list("integer_list.txt")

# end_time=time.time()

# print("Tempo necessario per popolamento al 100%\n"+str(end_time-start_time))

# print("Dimensione in memoria:"+str(sys.getsizeof(lista_letta_da_disco)))

# start_time = time.time()
# elem=lista_letta_da_disco[56]
# end_time=time.time()

# print("Tempo di accesso al 57-esimo ["+str(elem)+"] elemento: "+str(end_time-start_time))


# In[24]:


# start_time = time.time()

# lista_letta_da_disco=iter(read_integer_list("integer_list.txt"))

# end_time=time.time()

# print("Tempo necessario per popolamento al 100%\n "+str(end_time-start_time))

# print("Dimensione in memoria:"+str(sys.getsizeof(lista_letta_da_disco)))

# start_time = time.time()
# for i in range(0,57):
#     elem=next(lista_letta_da_disco)
# end_time=time.time()
    
# print("Tempo di accesso al 57-esimo ["+str(elem)+"] elemento: "+str(end_time-start_time))


# In[ ]:




