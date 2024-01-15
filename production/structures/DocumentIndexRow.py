#!/usr/bin/env python
# coding: utf-8

# In[2]:


import struct
from typing import BinaryIO


# In[3]:


# In[6]:


class DocumentIndexRow:

    STR_SIZE_DOC_INDEX_ROW = '30s i'
    SIZE_DOC_INDEX_ROW = struct.calcsize(STR_SIZE_DOC_INDEX_ROW)
    
    def __init__(self, doc_id:int, doc_no: str, text: str) -> None:
        '''
            This constructor receives a document number and the content of the document, and save
            the first parameter and the length of the second (that represents the document length).

            Parameters:
                doc_id (int): Document number handled internally
                doc_no (str): Document name received from external collection
                text (str): Content of the document.
    
            Returns:
                None
        '''
        if not isinstance(doc_no, str) or not isinstance(text, str):
            raise ValueError("doc_id must be an integer, doc_no must be a str and text must be a string.")
        
        self.doc_id = doc_id
        self.doc_no = doc_no.ljust(30)
        self.document_length = self.count_words(text)

    def count_words(self, text: str) -> int:
        """
            Count the number of tokens in a document.
    
            Parameters:
                text (str): Content of the document.
    
            Returns:
                int: Number of tokens in the document.
        """
        if not isinstance(text, str):
            raise ValueError("text must be a string.")

        # empty string
        if not text.strip():
            return 0
            
        return len(text.split())
    
    def to_string(self) -> str:    
        """ Join in a string the content of the row. 

         Returns:
            str: String representation of the row.
        """
        string = ' '.join([str(self.doc_no), str(self.document_length)])
        return string  

    def read_doc_index_row_on_disk(self, file:BinaryIO, offset:int):
        """
        Read the row data from a binary file on disk.

        Parameters:
            file (BinaryIO): Binary file object.
            offset (int): Offset in the file.

        Returns:
            int: Updated offset after reading the data.
        """
        file.seek(offset)  
        bytesLetti = file.read(self.SIZE_DOC_INDEX_ROW)

        if(not bytesLetti):
            return None
        try: 
            doc_no, doc_length = struct.unpack(self.STR_SIZE_DOC_INDEX_ROW, bytesLetti)
            self.doc_no=str(doc_no.decode('utf-8')).strip()
            self.document_length = doc_length
            
        except struct.error as e:
            print(f"Error unpacking data: {e}")

        return offset + self.SIZE_DOC_INDEX_ROW



    def write_doc_index_row_on_disk(self, file:BinaryIO, offset:int = 0):
        """
        Write the row data to a binary file on disk.

        Parameters:
            file (BinaryIO): Binary file object.
            offset (int): Offset in the file.

        Returns:
            int: Updated offset after writing the data.
        """
        file.seek(offset)

        binary_data = struct.pack(self.STR_SIZE_DOC_INDEX_ROW,self.doc_no.encode('utf-8'),
                                  self.document_length)

        file.write(binary_data)

        return self.SIZE_DOC_INDEX_ROW + offset





# DEBUG
    def write_debug(self,file_path:str,offset:int=0):
        with open(file_path, 'ab') as file:
            return self.write_doc_index_row_on_disk(file,offset)

    def read_debug(self,file_path:str,offset:int):
        with open(file_path, 'rb') as file:
            return self.read_doc_index_row_on_disk(file,offset)


# In[13]:


#Todo adjust tests.

def test_doc_index_row_pack():
    lr = DocumentIndexRow(3,"0","what do you doing") 
    lr2 = DocumentIndexRow(5,"1","how are you my friend")
    lr3 = DocumentIndexRow(8,"2","hello HELLO")
    
    lr.write_debug("Doc_index_debug.bin")
    lr2.write_debug("Doc_index_debug.bin")
    lr3.write_debug("Doc_index_debug.bin") # at this point, the file .bin contains 3 pairs
                
    lr2.read_debug("Doc_index_debug.bin", 0) # lr2 assume i valori nel file dall'offset 0 all'8, quindi prende i valori di lr
    assert lr2.doc_id == 3
    assert lr2.doc_no == "0"
    assert lr2.document_length == 4 # length of "what do you doing"
    
    lr.read_debug("Doc_index_debug.bin", 88) # lr assume i valori dall'offset 88 al 24, quindi quelli di lr3
    
    print(lr.doc_id)
    print(lr.doc_no)
    
    assert lr.doc_id == 8 
    assert lr.doc_no == "2"
    assert lr.document_length == 2  # length of "hello HELLO"

#test_doc_index_row_pack()

