#!/usr/bin/env python
# coding: utf-8

# In[1]:



import os
import sys
sys.path.append('../../')  # Go up two folders to the project root


from structures.DocumentIndexRow import DocumentIndexRow


# In[2]:





# In[3]:




# TEST FOR "DOCUMENT INDEX ROW"
def test_document_index_row_structure():
    row = DocumentIndexRow(5,"doc_no_5", "Hello world")
    assert row.document_length == 2
    assert row.document_length == row.count_words("Hello world")
    assert row.doc_id == 5
    assert row.doc_no.strip()=="doc_no_5"
    assert row.to_string() == "5 doc_no_5                       2"

    row = DocumentIndexRow(6, "doc_no_6","Testing multiple words in a sentence.")
    assert row.document_length == 6
    assert row.to_string() == "6 doc_no_6                       6"

    # Empty document
    row = DocumentIndexRow(7,"doc_no_7", "")
    assert row.document_length == 0
    assert row.to_string() == "7 doc_no_7                       0"

    # "Doc_id" must be an integer
    try:
        row = DocumentIndexRow("ciao", "world","")
        1==0
    except ValueError as e:
        assert 1==1

    # "Text" must be a string
    try:
        row = DocumentIndexRow(8, 123,"")
        assert 1==0
    except ValueError as e:
        assert 1==1


    # Parameter for "count_words" must be a string.
    try:
        row.count_words(56)
        assert 1==0
    except ValueError as e:
        assert 1==1

    assert row.count_words("") == 0


# In[4]:




def test_write_doc_index_row_on_disk():
    
    d_ind_row = DocumentIndexRow(3,"doc_no_3","what do you doing")
    assert d_ind_row.doc_id == 3
    assert d_ind_row.doc_no.strip() == "doc_no_3"
    assert d_ind_row.document_length == 4  
    
    if os.path.exists("prova.bin"):
        os.remove("prova.bin")

    # write in position 0
    new_free_offset = d_ind_row.write_debug("prova.bin", 0)
    
    #Read it again and check all field are correctly present in binary format.
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()

        assert len(binaryData) == d_ind_row.SIZE_DOC_INDEX_ROW
        assert new_free_offset == d_ind_row.SIZE_DOC_INDEX_ROW
        
        assert binaryData[0]   == 3
        assert binaryData[40]   == 4
        assert binaryData[9]== 111 #d
        assert binaryData[10]==99 #o
        assert binaryData[11]==95 #c
        assert binaryData[12]==110 #_
        assert binaryData[13]==111 #n
        #....
        assert binaryData[20]==32 # white spaces
 

    d_ind_row2 = DocumentIndexRow(67,"doc_1","One Ring to rule them all, One Ring to find them, One Ring to bring them all, and in the darkness bind them.")  
    
    #Write a second block in the position returned from previous method.
    new_free_offset = d_ind_row2.write_debug("prova.bin", new_free_offset)
    
    #Read all what is returned, check that the previous block is still present and new block is stored correctly
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()
        
        assert len(binaryData)==d_ind_row.SIZE_DOC_INDEX_ROW*2
        
        assert binaryData[0]   == 3
        assert binaryData[40]   == 4
        
        assert new_free_offset==d_ind_row.SIZE_DOC_INDEX_ROW*2
        
        assert binaryData[8] == 100
        assert binaryData[12] == 110
        
    os.remove("prova.bin") 


def test_read_doc_index_row_on_disk():
    d_ind_row = DocumentIndexRow(3,"doc_3","what do you doing")
    d_ind_row2 = DocumentIndexRow(67,"doc_1","One Ring to rule them all, One Ring to find them, One Ring to bring them all, and in the darkness bind them.")  

    new_offset = d_ind_row.write_debug("prova.bin", 0)
    d_ind_row2.write_debug("prova.bin", new_offset)

    new_doc_index_row = DocumentIndexRow(50,"doc_50", "I am gonna make him an offer he can't refuse.")

    assert new_doc_index_row.doc_id == 50
    assert new_doc_index_row.document_length == 10
    
    new_doc_index_row.read_debug("prova.bin",0)
    
    assert new_doc_index_row.doc_id == 3
    assert new_doc_index_row.document_length == 4
    
    new_doc_index_row.read_debug("prova.bin",new_offset)
    
    assert new_doc_index_row.doc_id == 67
    assert new_doc_index_row.document_length == 23
    
    assert new_doc_index_row.read_debug("prova.bin",800) == None
    
    os.remove("prova.bin") 

