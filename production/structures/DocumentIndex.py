#!/usr/bin/env python
# coding: utf-8

# In[1]:


from typing import List
from collections import defaultdict

import sys
sys.path.append('../')  # Go up two folders to the project root

from typing import BinaryIO,TextIO

#from utilities import General_Utilities as Utilities
import utilities.General_Utilities as Utilities
import structures.DocumentIndexRow as doc_ind_row


# In[2]:


class DocumentIndex(Utilities.Singleton):
    def __init__(self):
        if self._index is None:
            self._index = defaultdict(doc_ind_row.DocumentIndexRow)
            self.number_of_documents = 0 
            self.total_document_length = 0

    def add_document(self, doc_id: int, doc_no:str, text: str) -> None:
        """Adds a document to the document index."""
        if not isinstance(doc_id, int) or not isinstance(text, str):
            raise ValueError("doc_id must be an integer and text must be a string.")
            
        if (self.get_document(doc_id)==None):
            self._index[doc_id]=[]
        row = doc_ind_row.DocumentIndexRow(doc_id,doc_no,text)
        self._index[doc_id] = row

        # Update the statistics about total number of documents in the document index and total document length
        self.number_of_documents = self.number_of_documents + 1 
        self.total_document_length = self.total_document_length + row.document_length
             
    def get_document(self, doc_id: int) -> doc_ind_row.DocumentIndexRow:
        """Fetches a row from the document index"""
        if not isinstance(doc_id, int):
            raise ValueError("doc_id must be an integer.")
            
        if (doc_id in self._index):
            return self._index[doc_id]
        return None
    
    def is_empty(self) -> bool:
        """Check if there are no documents in the document index."""
        return len(self.get_document_ids()) == 0
    
    def get_document_ids(self) -> List[str]:
        """Returns all unique document IDs in the index."""
        return list(self._index.keys()) 
    
    def clear_structure(self):
        """ It clears the document index data structure."""
        self._index.clear()
        #self.number_of_documents = 0
        #self.total_document_length = 0
    
    def get_structure(self):
        """Returns the document index data structure."""
        return self._index
    
    # scrivo su disco, sul file "file_name" il contenuto della struttura dati "struct"
    def write_document_index_to_file_debug(self,file:TextIO) -> None:
        """ Write to the disk, to the file 'file_name', the content of the data structure _index saved internally."""
        for index, term in enumerate(self._index.keys()):
            file.write(self._index[term].to_string())

            if index != len(self._index.keys()) - 1:
                file.write("\n")

        file.write("\n")
    
    
    def write_document_index_to_file(self,file:BinaryIO,offset:int)->int:
        """ Write to the disk, to the file passed as argument, the content of the data structure _index saved internally.
            
            Returns: the byte offset free after writing on disk. 
        
        """
        for index, term in enumerate(self._index.keys()):
            offset=self._index[term].write_doc_index_row_on_disk(file,offset)
        return offset
  

