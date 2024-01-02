#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import import_ipynb
import os
import sys
sys.path.append('../../')  # Go up two folders to the project root


from structures.LexiconRow import LexiconRow 


# # Tests

# In[2]:


# import pytest
# import ipytest

# ipytest.autoconfig()


# In[8]:


#%%ipytest

#Remember the attributes of a LexiconRow

# self.term = self.term.ljust(self.MAX_TERM_LENGTH)
# self.dft 
# self.max_tf 
# self.idft
# self.maxTFIDF 
# self.docidOffset
# self.frequencyOffset
# self.blockOffset
# self.docidSize
# self.frequencySize
# self.numBlocks


# self, term: str, dft: int, max_tf: int=0, bm25dl:int=0, BM25Tf:int=0,
#                 docidOffset:int=0,frequencyOffset:int=0,blockOffset:int=0,docidSize:int=0,frequencySize:int=0,numBlocks:int=1):

def test_lexicon_row_data_structure():
    
    new_lexicon_row=LexiconRow("parola",5,80)
    
    assert new_lexicon_row.term=="parola".ljust(new_lexicon_row.MAX_TERM_LENGTH)
    assert new_lexicon_row.dft==5
    assert new_lexicon_row.max_tf==80
    assert new_lexicon_row.idft == 0
    assert new_lexicon_row.maxTFIDF == 0
    assert new_lexicon_row.docidOffset == 0
    assert new_lexicon_row.frequencyOffset == 0
    assert new_lexicon_row.blockOffset == 0
    assert new_lexicon_row.docidSize == 0
    assert new_lexicon_row.frequencySize == 0
    assert new_lexicon_row.numBlocks == 0
    
    if os.path.exists("prova.bin"):
        os.remove("prova.bin")
    
    new_free_offset=new_lexicon_row.write_lexicon_row_on_disk("prova.bin",0)
    
    #Read it again and check all field are correctly present in binary format.
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()
        
        assert len(binaryData)==new_lexicon_row.SIZE_LEXICON_ROW
        assert binaryData[0]== 112 #p
        assert binaryData[1]== 97 #a
        assert binaryData[2]== 114 #r
        assert binaryData[3]== 111 #o
        assert binaryData[4]== 108 #l
        assert binaryData[5]== 97 #a
        
        for i in range (6,30):
            assert binaryData[i]== 32 # white space

        assert binaryData[32] == 5
        assert binaryData[36] == 80

        for i in range(37, 52):
            assert binaryData[i] == 0
            
        for i in range(53, new_lexicon_row.SIZE_LEXICON_ROW):
            assert binaryData[i] == 0

    new_lexicon_row2=LexiconRow("parola2",4,60)
    new_free_offset=new_lexicon_row2.write_lexicon_row_on_disk("prova.bin",new_free_offset)
    
    #Read all what is returned, check that the previous block is still present and new block is stored correctly
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()
        
        assert len(binaryData)==new_lexicon_row2.SIZE_LEXICON_ROW*2

        assert binaryData[0]== 112 #p
        assert binaryData[1]== 97 #a
        assert binaryData[2]== 114 #r
        assert binaryData[3]== 111 #o
        assert binaryData[4]== 108 #l
        assert binaryData[5]== 97 #a
        
        for i in range (6,30):
            assert binaryData[i]== 32 # white space

        assert binaryData[32] == 5
        assert binaryData[36] == 80
      
        for i in range(37, 52):
            assert binaryData[i] == 0
            
        for i in range(53, new_lexicon_row.SIZE_LEXICON_ROW):
            assert binaryData[i] == 0
        
        

        # for "parola2"
        assert binaryData[100] == 112 #p
        assert binaryData[101] == 97 #a
        assert binaryData[102]== 114 #r
        assert binaryData[103]== 111 #o
        assert binaryData[104]== 108 #l
        assert binaryData[105]== 97 #a
        assert binaryData[106] == 50 #2
        
        for i in range (107,130):
            assert binaryData[i]== 32 # white space

        assert binaryData[132] == 4
        assert binaryData[136] == 60

        for i in range(137, 152):
            assert binaryData[i] == 0   
        
    empty_lexicon_row = LexiconRow("",0,0)
    full_lexicon_row=LexiconRow(term = "debug", dft = 10, max_tf = 20,docidOffset = 60, frequencyOffset = 70)

    os.remove("prova.bin") 
    new_free_offset=full_lexicon_row.write_lexicon_row_on_disk("prova.bin",0)
    empty_lexicon_row.read_lexicon_row_on_disk("prova.bin", 0)

    assert empty_lexicon_row.term == "debug".ljust(empty_lexicon_row.MAX_TERM_LENGTH)
    assert empty_lexicon_row.dft == 10
    assert empty_lexicon_row.max_tf == 20
    assert empty_lexicon_row.docidOffset == 60
    assert empty_lexicon_row.frequencyOffset == 70
    
    os.remove("prova.bin") 
    

