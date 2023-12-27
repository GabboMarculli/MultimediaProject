#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys
import struct
#import import_ipynb
from typing import List, Dict, Tuple, Union, Any, Callable
from collections import Counter, defaultdict,OrderedDict
from dataclasses import dataclass
from typing import TextIO, BinaryIO


sys.path.append('../')  # Go up two folders to the project root
#from structures.Lexicon import Lexicon
from structures.LexiconRow import LexiconRow
from utilities.Compression import Compression 


# In[3]:


#Costants

TYPE_DOC_ID="type_doc_id"
TYPE_FREQ="type_freq"


# In[4]:


@dataclass
class Posting:
    doc_id: int
    frequency: Any = None
    
    #The following methods are used mainly for debug and tests.
    
    @classmethod 
    def from_string(cls, description:str):
        docId,payl=description.split(":")
        doc_id=int(docId)
        frequency=int(payl)
        return cls(doc_id, frequency)
    
    def write_to_disk(self,file_path:str,arg:str, offset:int=0)->None:
        """Function to open a file and write on it a single posting information in a specific position
        
        Args:
            file_path: the file name to be opened in append mode
            arg: indicates TYPE_DOC_ID or TYPE_FREQ the single information to be written
            offset: the position in bytes inside a file to be written
        """
        
        with open(file_path, 'ab') as file:
            return self.write_to_disk_from_opened_file(file,arg,offset)
        
    def write_to_disk_from_opened_file(self,file:BinaryIO,arg,offset:int=0):
        """Function to write on a opened file an information of a posting in a specific position
        
        Args:
            file: the file to be used
            arg: inidcates TYPE_DOC_ID or TYPE_FREQ to write a single information
            offset: the position in bytes inside a file to be written
            
        Returns:
               the next offset position in the file after writing the information 
        """
        file.seek(offset)
        if (arg==TYPE_DOC_ID):
            binary_data = struct.pack("i",self.doc_id)
        if (arg==TYPE_FREQ):
            binary_data = struct.pack("i",self.frequency)
    
        file.write(binary_data)
            
        return struct.calcsize('i')+offset


# In[5]:


class InvertedIndex:

    def __init__(self):
        self._index = defaultdict(list)
        
    def add_posting(self, term: str, doc_id: int, frequency: Any=None) -> None:
        """Adds a document to the posting list of a term.

        Args:
            term: the term to be added to the inveted index
            doc_id: the document id to be added linked to a specific term
            frequency: the frequency of a term inside a specific doc_id to be added 
            
        """
        # append new posting to the posting list
        if (self.get_postings(term)==None):
            self._index[term]=[]
        self._index[term].append(Posting(doc_id,frequency))
             
    def get_postings(self, term: str) -> List[Posting]:
        """Fetches the posting list for a given term.
        
        Args:
            term: the term to be found inside the inverted index

        Returns:
            the list of postings associated to the term
        """
        
        if (term in self._index):
            return self._index[term]
        return None
    
    def is_empty(self)->bool:
        """Check if there is no term in the inverted index."""
        return len(self.get_terms())==0
    
    def get_terms(self) -> List[str]:
        """Returns all unique terms in the index."""
        return self._index.keys() 
    
    def clear_structure(self)->None:
        """ It clears the inverted index data structure present in main memory."""
        self._index.clear()
    
    def get_structure(self)->None:
        """Returns the inverted index data structure."""
        return self._index
    
    
    @staticmethod
    def merge_posting_lists(posting_list_1:List[Posting],posting_list_2:List[Posting])->None:
        """ Given two posting lists, it merges the two list in one single posting list and return the result.
        Args:
            posting_list_1: the first posting list to be merged
            posting_list_2: the second posting list used to merge the first one
            
        Returns:
            unique posting list of the concatenation of the 2 in input
        """
        return posting_list_1+posting_list_2
    
    
    @staticmethod
    def compute_max_term_frequency_of_posting_list(posting_list:List[Posting]) -> int:
        """
        Given a postings list of a term, compute the maximum term frequency.
    
        Args:
            postings_list: A posting list containing doc_ids and frequency.
        """
        if not isinstance(posting_list, List):
            raise ValueError("Invalid postings list.")
    
        if len(posting_list) == 0:
            return 0
            
        max_freq = max(posting_list, key=lambda x: x.frequency)    
        return  max_freq.frequency  

    @staticmethod
    def write_to_files_a_posting_list(list_of_posting:List[Posting],compression_mode:bool,file_doc_ids:BinaryIO,file_freq:BinaryIO,offset_doc_ids:int,offset_freq:int)-> Tuple[int, int]:
        """Static method to write a posting list in 2 distinct files. 
           One file is used to save doc_ids and an other is used to save freqs.
        
        Args:
            list_of_posting: the posting list to be saved
            compression_mode: if the information should be compressed or not
            file_doc_ids: the file used to save doc_ids
            file_freq: the file used to save frequencies
            offset_doc_ids: the start offset position for writing the list of doc_ids
            offset_freq: the start offset position for writing the list of freq
        Returns:
            the new free offset position in the file_doc_ids after writing
            the new free offset position in the file_freq after writing
        
        """
        doc_ids=[posting.doc_id for posting in list_of_posting]
        freqs=[posting.frequency for posting in list_of_posting]
        
        file_doc_ids.seek(offset_doc_ids)  
        file_freq.seek(offset_freq)
           
        if (not compression_mode):
            packed_data = struct.pack('!{}i'.format(len(doc_ids)), *doc_ids)
            file_doc_ids.write(packed_data)

            packed_data = struct.pack('!{}i'.format(len(freqs)), *freqs)
            file_freq.write(packed_data)
            return offset_doc_ids+struct.calcsize('!{}i'.format(len(doc_ids))),offset_freq+struct.calcsize('!{}i'.format(len(freqs)))
            
        else:
            
            compressed_doc_ids=Compression.d_gap_compression(doc_ids)
            compressed_freq=Compression.unary_compression_integer_list(freqs)
            file_doc_ids.write(compressed_doc_ids)
            file_freq.write(compressed_freq)
            
            return offset_doc_ids+len(compressed_doc_ids),offset_freq+len(compressed_freq)
        
    @staticmethod
    def read_from_files_a_posting_list(file_doc_ids:BinaryIO,file_freq:BinaryIO,
                                       compression_mode:bool,
                                       offset_doc_ids:int,offset_freq:int,
                                       nr_postings:int,
                                       doc_ids_byte_size:int=0,freq_byte_size:int=0,
                                       min_doc_id:int=0)-> Tuple[List[Posting],int, int]:
        
        """Static method to read 'a number of postings' of a posting list from 2 distinct files:
           One file contains the saved doc_ids and the other contains the saved freqs.
           
        Args:
            file_doc_ids: the file where doc_ids are saved
            file_freq: the file where frequencies are saved
            compression_mode: to specify if the bytes to be read must be decompressed or not
            offset_doc_ids: the start offset position for reading the list of doc_ids
            offset_freq: the start offset position for reading the list of frequency
            nr_postings: indicates the number of elements to be read
            
            doc_ids_byte_size: used only if compression_mode is True instead of nr_postings and indicates the dimension in bytes of doc_ids to be read
            freq_byte_size: used only if compression_mode is True instead of nr_postings the dimension in bytes of freqs to be read
            min_doc_id: used only if compression_mode is True and indicates the number of elements to be read
            
           
        Returns:
            posting_list: read from the 2 files
            offset_doc_id: new offset of the read file doc_ids
            offeset_freqs: new offset of the read file freqs
        """
        
        file_doc_ids.seek(offset_doc_ids)  
        file_freq.seek(offset_freq)
        
        if (not compression_mode):
        
            bytes_to_read=struct.calcsize('!{}i'.format(nr_postings))
        
            packed_data = file_doc_ids.read(bytes_to_read)
            doc_ids = struct.unpack('!{}i'.format(nr_postings), packed_data)

            packed_data = file_freq.read(bytes_to_read)
            freqs = struct.unpack('!{}i'.format(nr_postings), packed_data)
            
            doc_ids_byte_size=bytes_to_read
            freq_byte_size=bytes_to_read

        else:
            #In this case the number of posting represents also the number of freq to decompress.
            freq_compressed_bytes = file_freq.read(freq_byte_size)
            freqs=Compression.unary_decompression_integer_list(freq_compressed_bytes,nr_postings)
            
            doc_ids_compressed_bytes = file_doc_ids.read(doc_ids_byte_size)
            doc_ids=Compression.d_gap_decompression(doc_ids_compressed_bytes,min_doc_id)
            
            
        posting_list=[]
        for doc_id, freq in zip(doc_ids, freqs):
            posting_list.append(Posting(doc_id,freq))
                
        return posting_list,offset_doc_ids+doc_ids_byte_size,offset_freq+freq_byte_size
        
    
    def write_to_block_all_index_in_memory(self,path_lexicon: str,path_doc_ids:str,path_freq:str)-> None:
        """ Function to write the overall index in main memory to a file "block" during the SPIMI phase.
            Pay attention, here the postings in a non compressed mode!
            
        Args:
            path_lexicon: the position where to write the block related to the temporal lexicon.
            path_doc_ids: the position where to write the block related to the temporal doc_ids.
            path_freq: the position where to write the block related to the temporal freqs.
            
        """
        sorted_lexicon=sorted(self._index.items())
        
        with open(path_freq, "ab") as f_freq:
            
            with open(path_doc_ids, "ab") as f_doc_id:
        
                with open(path_lexicon, "ab") as f_lexicon:

                    offset_lexicon=0
                    offset_doc_ids=0
                    offset_freq=0
                    for term,postings in sorted_lexicon:
                        #Istantiate a lexicon row
                        lexRow=LexiconRow(term,len(postings),0,0,0,0,0,offset_doc_ids,offset_freq,0,0)
                          
                        #Save posting list to specifics file
                        offset_doc_ids,offset_freq=InvertedIndex.write_to_files_a_posting_list(postings,False,f_doc_id,f_freq,offset_doc_ids,offset_freq)     
                        
                        #Save the related lexicon row.
                        offset_lexicon=lexRow.write_lexicon_row_on_disk_to_opened_file(f_lexicon,offset_lexicon)

    #Debugging output functions                     
    
    @staticmethod
    
    def write_to_file_a_posting_list_debug_mode(file_debug:TextIO,term:str, posting_list:List, new_term:bool) -> None:
        """ 
        This method write in human readable format the entire inverted index processed. It concatenates 
        the posting lists amongs blocks on the same output file.
        
        Args:
            file_debug: the file used for append contented on disk
            term: the term related to the posting_list
            posting_list: the elements to save on disk
            new_term: indicates if a new term comes or not, during the partial saving of the posting list.
            
        """

        if (new_term):
            file_debug.write("\n")
            file_debug.write(term)

        for posting in posting_list:
            file_debug.write(f" {posting.doc_id}")
            if posting.frequency:
                file_debug.write(f":{str(posting.frequency)}")
    
    
    
    
    def read_from_block_all_index_in_memory(self, path_lexicon: str,path_doc_ids:str, path_freq:str)-> None:
        """ Function to read an inverted index in main memory related to a specific lexicon file.
            This function is used for debug and test reasons.
        
        Args:
            path_lexicon: the position where to read the lexicon related to a specific inverted index
            path_doc_ids: the position where to read the information of doc_ids.
            path_freq: the position where to read the information of freq.
            
        Returns:
            
        """
        
        self.clear_structure()
        
        offset_lexicon=0
        offset_doc_id=0
        offset_freq=0
        
        with open(path_freq, "rb") as f_freq:
            with open(path_doc_ids, "rb") as f_doc_id:
                with open(path_lexicon, "rb") as f_lexicon:
                
                    #Initialize empty lexicon row.
                    lexiconTerm=LexiconRow("",0)
                    
                    while (True):
                        
                        offset_lexicon=lexiconTerm.read_lexicon_row_on_disk_from_opened_file(f_lexicon,offset_lexicon)
                        if(offset_lexicon==None):
                            #Here, I finished to read all the lexicon block.
                            return
                        
                        posting_list,offset_doc_id,offset_freq=InvertedIndex.read_from_files_a_posting_list(f_doc_id,f_freq,False,offset_doc_id,offset_freq,lexiconTerm.dft)
                                                                                                         
                        for posting in posting_list:
                            self.add_posting(lexiconTerm.term,posting.doc_id,posting.frequency)
                           
    def write_to_block_debug_mode(self,file_name_index: str) -> None:
        """ Write the inverted index (in memory) in lexicographical oreder into a file_name_index on disk human readable.
            It is used just for debugging the spimi phase.
        Args:
            file_name_index: the name of the file where the inverted index will be written in clear
            
        """
        sorted_lexicon=sorted(self._index.items())
        with open(file_name_index, "w") as f:
            for term,postings in sorted_lexicon:
                f.write(term)
                for posting in postings:
                    f.write(f" {posting.doc_id}")
                    if posting.frequency:
                        f.write(f":{str(posting.frequency)}")
                f.write("\n") 

