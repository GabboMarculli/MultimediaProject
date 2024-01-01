#!/usr/bin/env python
# coding: utf-8

# In[1]:


import struct
import math
from typing import BinaryIO,TextIO

#import import_ipynb
import sys
sys.path.append('../')  
import structures.DocumentIndex as doc_index


# In[4]:


class LexiconRow:
    
    
    MAX_TERM_LENGTH=30
    STR_SIZE_LEXICON_ROW='30s 2i 2f 2i 1f 3q 3i'
    SIZE_LEXICON_ROW=struct.calcsize(STR_SIZE_LEXICON_ROW)
    
    def __init__(self, term: str, dft: int=0, max_tf: int=0,idft: float=0, maxTFIDF:float=0, bm25dl:int=0, BM25Tf:int=0,
                 docidOffset:int=0,frequencyOffset:int=0,blockOffset:int=0,docidSize:int=0,frequencySize:int=0,numBlocks:int=1):
        
        self.term = term if (len(term)<self.MAX_TERM_LENGTH) else term[:self.MAX_TERM_LENGTH]
        self.term = self.term.ljust(self.MAX_TERM_LENGTH)
        
        # Document frequency of the term
        self.dft = dft
        
        # Max term frequency
        self.max_tf = max_tf
        
        # Inverse of document frequency of the term.              
        self.idft = 0
    
        # Max tfidf
        self.maxTFIDF = 0
        
        #For term upper bound bm25
        self.BM25Dl=1
        self.BM25Tf=0
        self.maxBM25=0
        
        self.docidOffset=docidOffset
        self.frequencyOffset=frequencyOffset
        self.blockOffset=0 # INDIRIZZO DEL PRIMO BLOCCO. FACENDO BLOCKOFFSET + numBlocks* DIMENSIONE BLOCCO POSSO CARICARE TUTTO IN MEMORIA
        
        self.docidSize=0
        self.frequencySize=0
        self.numBlocks=0 # QUANTI BLOCCHI SONO NECESSARI PER LA POSTING LIST DI QUESTO TERMINE
    
    @staticmethod   
    def to_string_header()->str:
        """ Used only for debug purposes."""
        return '\t'.join(["term","","","","dft","max_tf","idft","mTFIDF","BM25Tf","BM25Dl","mBM25","idOff","frOff","blkOff","docidSz","freqSz","numBlks"])
    
    def to_string(self)->str:
        """This function returns a string representation of a LexiconRow.
        
        Returns:
            a human readable string representation of the Lexicon Row
        """
        string = '\t'.join([str(self.term) , str(self.dft) , str(self.max_tf), "{:.3f}".format(self.idft),  
                           "{:.3f}".format(self.maxTFIDF), str(self.BM25Tf), str(self.BM25Dl),"{:.3f}".format(self.maxBM25),
                           str(self.docidOffset), str(self.frequencyOffset), str(self.blockOffset),
                           str(self.docidSize), str(self.frequencySize),str(self.numBlocks)])
        return string    
    
    def write_lexicon_row_on_disk_to_opened_file(self,file:BinaryIO,offset:int=0)->int:
        """This function writes on a specific position of an opened file a lexicon row information.
           
           Args:
               file: the file to store the lexicon row
               offset: the position inside the file to store the lexicon row
           Returns:
               the new offset free position after writing on the file
        """
        
        file.seek(offset)
       
        binary_data = struct.pack(self.STR_SIZE_LEXICON_ROW, 
                                      self.term.encode('utf-8'),
                                      self.dft,self.max_tf,
                                      self.idft, self.maxTFIDF,
                                      self.BM25Tf,self.BM25Dl,self.maxBM25,
                                      self.docidOffset, self.frequencyOffset,self.blockOffset,
                                      self.docidSize, self.frequencySize, self.numBlocks)
        file.write(binary_data)
            
        return self.SIZE_LEXICON_ROW+offset
        
    def read_lexicon_row_on_disk_from_opened_file(self,file:BinaryIO,offset:int)->int:
        """This function reads a lexicon row informations in a specific position from an opened file.
        
        Args:
            file: the file to read a lexicon row
            offset: the position inside the file to read the lexicon row
        
        Returns:
            the offset position after reading
            
        """
        file.seek(offset)  
        bytesLetti = file.read(self.SIZE_LEXICON_ROW)
        
        if(not bytesLetti):
            return None
            
        try:
            term,dft,max_tf,idft,maxTFIDF,BM25Tf,BM25Dl,maxBM25,docidOffset,frequencyOffset,blockOffset, docidSize,frequencySize,numBlocks = struct.unpack(self.STR_SIZE_LEXICON_ROW, bytesLetti)

            self.term=term.decode('utf-8')
            self.dft=dft
            self.idft=idft
            self.max_tf=max_tf
            self.maxTFIDF=maxTFIDF
            self.BM25Tf=BM25Tf
            self.BM25Dl=BM25Dl
            self.maxBM25=maxBM25
            self.docidOffset=docidOffset
            self.frequencyOffset=frequencyOffset
            self.docidSize=docidSize
            self.frequencySize=frequencySize
            self.numBlocks=numBlocks
            self.blockOffset=blockOffset
            
            
        except struct.error as e:
            print(f"Error unpacking data: {e}")
            
        return offset+self.SIZE_LEXICON_ROW
    
   
    #USED FOR DEBUGGING
    
    def write_lexicon_row_on_disk_debug_mode(self,file_debug:TextIO)->None:
        """This function opens a file and writes on a specific position a lexicon row information.
            This is used for debug and tests.
        
            Args:
               file_debug: the file to store the lexicon row
        """
        file_debug.write(self.to_string()+"\n")
    
    
    def write_lexicon_row_on_disk(self,file_path:str,offset:int=0)->int:
        """This function opens a file and writes on a specific position a lexicon row information.
            This is used for debug and tests.
        
            Args:
               file_path: the file to store the lexicon row
               offset: the position inside the file to store the lexicon row
            Returns:
                the new offset free position after writing
               
        """
        with open(file_path, 'ab') as file:
            return self.write_lexicon_row_on_disk_to_opened_file(file,offset)
        
   
    def read_lexicon_row_on_disk(self,file_path:str,offset:int)->int:
        """This function opens a file and reads in a specific position a lexicon row information.
            This is used for debug and tests.
        
            Args:
               file_path: the file to read a lexicon row
               offset: the position inside the file to read the lexicon row
            Returns:
                the offset position after reading
        """
        with open(file_path, 'rb') as file:
            return self.read_lexicon_row_on_disk_from_opened_file(file,offset)   
        
    def update_term_upper_bound_bm25(self, term_freq:int, doc_len: int) -> None:
        """
            This method is called during SPIMI: in this part we don't have available the total number of documents in the collection
            and the total documents length, so the idea is to take in consideration just the posting with term frequency and document length
            that maximize the ratio term frequency/document length. This max value for each block is used in the merger to determine the 
            real upper bound of a term.
            The result is updated inside the lexicon row.
            
            Args:
                term_freq: corresponds to the term frequency of a posting
                doc_len: the length of a specific document which the term lies in
        """
        
        if (self.BM25Dl==0):
            currentRatio=0
        else:
            currentRatio = self.BM25Tf/self.BM25Dl
    
        newRatio = term_freq / doc_len
        
        if newRatio > currentRatio:
            self.BM25Tf = term_freq
            self.BM25Dl = doc_len


# In[ ]:




