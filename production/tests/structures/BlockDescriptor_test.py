#!/usr/bin/env python
# coding: utf-8

# In[1]:



import os
import sys
sys.path.append('../../')  # Go up two folders to the project root


from structures.BlockDescriptor import BlockDescriptor 


# # Tests

# In[2]:

# In[3]:

#Remember the attributes of a block_descriptor

#nr_postings:int=0,
#offset_doc_ids:int=0,
#offset_freqs:int=0,
#doc_ids_bytes_size:int=0,
#freq_bytes_size:int=0,
#min_doc_id:int=0,
#max_doc_id:int=0

def test_write_block_descriptor_on_disk():
    
    b_d=BlockDescriptor(5,101,103,82,47,1,1002)
    
    assert b_d.nr_postings==5
    assert b_d.offset_doc_ids==101
    assert b_d.offset_freqs==103
    assert b_d.doc_ids_bytes_size==82
    assert b_d.freq_bytes_size==47
    assert b_d.min_doc_id==1
    assert b_d.max_doc_id==1002
    
    
    if os.path.exists("prova.bin"):
        os.remove("prova.bin")
    
    #Write a first block in the position 0
    new_free_offset=b_d.write_block_descriptor_on_disk("prova.bin",0)
    
    #Read it again and check all field are correctly present in binary format.
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()
        
        assert len(binaryData)==b_d.SIZE_BLOCK_DESCRIPTOR
        assert binaryData[0]==101
        assert binaryData[8]==103
        assert binaryData[16]==5
        assert binaryData[20]==82
        assert binaryData[24]==47
        assert binaryData[28]==1
        assert binaryData[32]==234  #1002 splitted in 11101010 (low sign)
        assert binaryData[33]==3    #1002 splitted in 11 (most sign)
        assert new_free_offset==b_d.SIZE_BLOCK_DESCRIPTOR
        
    b_d_1=BlockDescriptor(6,156,198,12506,17893,10,90)   
   
    #Write a second block in the position returned from previous method.
    new_free_offset=b_d_1.write_block_descriptor_on_disk("prova.bin",new_free_offset)
    
    #Read all what is returned, check that the previous block is still present and new block is stored correctly
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()
        
        assert len(binaryData)==b_d.SIZE_BLOCK_DESCRIPTOR*2
        assert binaryData[0]==101
        assert binaryData[8]==103
        assert binaryData[16]==5
        assert binaryData[20]==82
        assert binaryData[24]==47
        assert binaryData[28]==1
        assert binaryData[32]==234  #1002 splitted in 11101010 (low sign)
        assert binaryData[33]==3    #1002 splitted in 11 (most sign)
        
        assert new_free_offset==b_d.SIZE_BLOCK_DESCRIPTOR*2
        
        #The same as before
        
        assert binaryData[36]==156
        assert binaryData[44]==198
        assert binaryData[52]==6
        assert binaryData[56]==218 # 12506 splitted in 11011010 (low sign)
        assert binaryData[57]==48  # 12506 splitted in 110000 (most sign)
        assert binaryData[60]==229 # 17893 splitted in 11100101(low sign)
        assert binaryData[61]==69  # 17893 splitted in 1000101(most sign)
        assert binaryData[64]==10
        assert binaryData[68]==90 
    os.remove("prova.bin") 

    
def test_read_block_descriptor_on_disk():
    
    #Using previous tested write_block_descriptor_on_disk to write the same block as before.
    #Now checking if the datastructure si correctly read from file and populated in memory.
    b_d_1=BlockDescriptor(5,101,103,82,47,1,1002)
    b_d_2=BlockDescriptor(6,156,198,12506,17893,10,90)  
    
    new_offset=b_d_1.write_block_descriptor_on_disk("prova.bin",0)
    b_d_2.write_block_descriptor_on_disk("prova.bin",new_offset)
    
    new_block_descriptor_1=BlockDescriptor()
    new_block_descriptor_1.read_block_descriptor_on_disk("prova.bin",0)
    
    assert new_block_descriptor_1.nr_postings==b_d_1.nr_postings
    assert new_block_descriptor_1.offset_doc_ids==b_d_1.offset_doc_ids
    assert new_block_descriptor_1.offset_freqs==b_d_1.offset_freqs
    assert new_block_descriptor_1.doc_ids_bytes_size==b_d_1.doc_ids_bytes_size
    assert new_block_descriptor_1.freq_bytes_size==b_d_1.freq_bytes_size
    assert new_block_descriptor_1.min_doc_id==b_d_1.min_doc_id
    assert new_block_descriptor_1.max_doc_id==b_d_1.max_doc_id
    
    new_block_descriptor_2=BlockDescriptor()
    new_block_descriptor_2.read_block_descriptor_on_disk("prova.bin",new_offset)
    
    assert new_block_descriptor_2.nr_postings==b_d_2.nr_postings
    assert new_block_descriptor_2.offset_doc_ids==b_d_2.offset_doc_ids
    assert new_block_descriptor_2.offset_freqs==b_d_2.offset_freqs
    assert new_block_descriptor_2.doc_ids_bytes_size==b_d_2.doc_ids_bytes_size
    assert new_block_descriptor_2.freq_bytes_size==b_d_2.freq_bytes_size
    assert new_block_descriptor_2.min_doc_id==b_d_2.min_doc_id
    assert new_block_descriptor_2.max_doc_id==b_d_2.max_doc_id
    
    #Finally check if I try to read something at non valid offset position.
    assert new_block_descriptor_2.read_block_descriptor_on_disk("prova.bin",800) == None
    
    
    os.remove("prova.bin") 
    