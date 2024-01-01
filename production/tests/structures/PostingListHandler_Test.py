#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import import_ipynb
import os
import shutil

import sys
sys.path.append('../../')  # Go up two folders to the project root

from structures.InvertedIndex import Posting,InvertedIndex

from structures.BlockDescriptor import BlockDescriptor
from structures.LexiconRow import LexiconRow
from structures.PostingListHandler import Posting_List_Reader
from building_data_structures.IndexBuilder import IndexBuilder 
from pre_processing.Decompress_collection import Collection_Reader


# # Tests

# In[2]:




# In[3]:


# Costants

DIR_TEMP_FOLDER="TEMP"
DIR_TEMP_DOC_ID="DOC_ID_TEMP"
DIR_TEMP_FREQ="FREQ_TEMP"
DIR_TEMP_LEXICON="LEXICON_TEMP"

DIR_LEXICON="LEXICON"
DIR_DOC_INDEX="DOC_INDEX"
DIR_INVERTED_INDEX="INV_INDEX"

PATH_FINAL_LEXICON="lexicon.bin"
PATH_FINAL_DOC_IDS="doc_ids.bin"
PATH_FINAL_FREQ="freq.bin"
PATH_FINAL_BLOCK_DESCRIPTOR="block_descriptors.bin"
PATH_FINAL_DOCUMENT_INDEX="document_index.bin"


PATH_COLLECTION_STATISTICS="collection_statistics.bin"
PATH_COLLECTION_STATISTICS_DEBUG="collection_statistics.txt"

PATH_FINAL_INVERTED_INDEX_DEBUG="inverted_index.txt"
PATH_FINAL_LEXICON_DEBUG="lexicon.txt"
PATH_FINAL_DOCUMENT_INDEX_DEBUG="document_index.txt"


# In[4]:


test_documents=[]
for i in range(0,10000):
    if (i%2==0):
        test_documents.append("doc"+str(i)+"\t"+" aaaaa ttt")
    else:
        test_documents.append("doc"+str(i)+"\t"+" bbbbb dddd")
        
indexBuilder=IndexBuilder(True,False,Collection_Reader("",-1,-1,False,False,test_documents))
indexBuilder.single_pass_in_memory_indexing(15000000)
indexBuilder.index_merging()



# In[6]:


# import time
# #Decomment for doing a manual testing.
# lexicon_file_path=os.path.join(DIR_LEXICON, PATH_FINAL_LEXICON)
# doc_id_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_DOC_IDS)
# freq_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_FREQ)
# block_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_BLOCK_DESCRIPTOR)

# lexicon_file=open(lexicon_file_path,"rb")
# doc_id_file=open(doc_id_file_path,"rb")
# freq_file=open(freq_file_path,"rb")
# block_file=open(block_file_path,"rb")


# term_bbb=LexiconRow("the",0)           
# term_bbb.read_lexicon_row_on_disk_from_opened_file(lexicon_file,term_bbb.SIZE_LEXICON_ROW*1062195)
# print(term_bbb.term)
# #bd=BlockDescriptor()
# #block_desc=bd.read_block_descriptor_on_disk_from_opened_file(block_file,0)



# pl_reader3=Posting_List_Reader(term_bbb,True,doc_id_file,freq_file,block_file)

# start=time.time()
# i=0
# for elem in pl_reader3:
#     i+=1
#     #print(elem)
# end=time.time()
# print(i)
# print ("TOT TIME: "+str(end-start))

# lexicon_file.close()
# doc_id_file.close()
# freq_file.close()
# block_file.close()


# In[5]:


#%%ipytest

def test_Posting_List_Reader():
    

    lexicon_file_path=os.path.join(DIR_LEXICON, PATH_FINAL_LEXICON)
    doc_id_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_DOC_IDS)
    freq_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_FREQ)
    block_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_BLOCK_DESCRIPTOR)
    
    
    lexicon_file=open(lexicon_file_path,"rb")
    doc_id_file=open(doc_id_file_path,"rb")
    freq_file=open(freq_file_path,"rb")
    block_file=open(block_file_path,"rb")
    
    
    term_aaa=LexiconRow("aaaaa",0)           
    term_aaa.read_lexicon_row_on_disk_from_opened_file(lexicon_file,0)

    
    pl_reader=Posting_List_Reader(term_aaa,False,doc_id_file,freq_file,block_file)
    
    assert pl_reader.get_total_blocks()==71
    assert pl_reader.get_current_block()==None
    assert pl_reader.get_current_posting()==None
    
    i=0
    for elem in pl_reader:
        i+=1
    
    #Check the posting list is traversed at blocks so methods
    # __next__ and __update_posting_list__ are working properly.
    assert i==5000
    
    try:
        next(pl_reader)
        assert 1==0
    except Exception as e: 
        assert 1==1
        
    pl_reader2=Posting_List_Reader(term_aaa,False,doc_id_file,freq_file,block_file)
    
    posting=next(pl_reader2)
    assert posting.doc_id==0
    assert posting.frequency==1
    
    posting=next(pl_reader2)
    
    assert posting.doc_id==2
    assert posting.frequency==1
    
    posting=next(pl_reader2)
    
    assert posting.doc_id==4
    assert posting.frequency==1
    
    
    pl_reader3=Posting_List_Reader(term_aaa,False,doc_id_file,freq_file,block_file)
    
    for i in range (1,80):
        posting=next(pl_reader3)
        
    assert pl_reader3.get_current_block().nr_postings==71
    assert pl_reader3.get_current_posting().doc_id==posting.doc_id
    assert pl_reader3.get_current_posting().frequency==posting.frequency
    
    assert pl_reader3.get_current_block().min_doc_id==142
    assert pl_reader3.get_current_block().max_doc_id==282
    
    
    #Do the same tests on other terms.
    
    term_bbb=LexiconRow("bbbbb",0)           
    term_bbb.read_lexicon_row_on_disk_from_opened_file(lexicon_file,term_bbb.SIZE_LEXICON_ROW)
    
    pl_reader=Posting_List_Reader(term_bbb,False,doc_id_file,freq_file,block_file)
    
    assert pl_reader.get_total_blocks()==71
    assert pl_reader.get_current_block()==None
    assert pl_reader.get_current_posting()==None
    
    
    
    i=0
    for elem in pl_reader:
        i+=1
    
    #Check the posting list is traversed at blocks so methods
    # __next__ and __update_posting_list__ are working properly.
    assert i==5000
    
    try:
        next(pl_reader)
        assert 1==0
    except Exception as e: 
        assert 1==1
        
    pl_reader2=Posting_List_Reader(term_bbb,False,doc_id_file,freq_file,block_file)
    
    posting=next(pl_reader2)
    assert posting.doc_id==1
    assert posting.frequency==1
    
    posting=next(pl_reader2)
    
    assert posting.doc_id==3
    assert posting.frequency==1
    
    posting=next(pl_reader2)
    
    assert posting.doc_id==5
    assert posting.frequency==1
    
    
    pl_reader3=Posting_List_Reader(term_bbb,False,doc_id_file,freq_file,block_file)
    
    for i in range (1,80):
        posting=next(pl_reader3)
        
    assert pl_reader3.get_current_block().nr_postings==71
    assert pl_reader3.get_current_posting().doc_id==posting.doc_id
    assert pl_reader3.get_current_posting().frequency==posting.frequency
    
    assert pl_reader3.get_current_block().min_doc_id==143
    assert pl_reader3.get_current_block().max_doc_id==283
    
    
    lexicon_file.close()
    doc_id_file.close()
    freq_file.close()
    block_file.close()
    


# In[6]:


#%%ipytest
def test_Posting_List_Reader_NEXT_GEQ():
    
    
    lexicon_file_path=os.path.join(DIR_LEXICON, PATH_FINAL_LEXICON)
    doc_id_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_DOC_IDS)
    freq_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_FREQ)
    block_file_path=os.path.join(DIR_INVERTED_INDEX, PATH_FINAL_BLOCK_DESCRIPTOR)
    
    lexicon_file=open(lexicon_file_path,"rb")
    doc_id_file=open(doc_id_file_path,"rb")
    freq_file=open(freq_file_path,"rb")
    block_file=open(block_file_path,"rb")
    
    
    term_aaa=LexiconRow("aaaaa",0)           
    term_aaa.read_lexicon_row_on_disk_from_opened_file(lexicon_file,0)

    pl_reader=Posting_List_Reader(term_aaa,False,doc_id_file,freq_file,block_file)
    
    assert pl_reader.get_total_blocks()==71
    assert pl_reader.get_current_block()==None
    assert pl_reader.get_current_posting()==None
    
    
    current_posting=pl_reader.nextGEQ(80)
    
    assert current_posting!=None
    assert current_posting.doc_id==80
    assert current_posting.frequency==1
    
    #Test that if I pass a lower number of the current_one returns the current_one
    current_posting=pl_reader.nextGEQ(4)
    
    assert current_posting!=None
    assert current_posting.doc_id==80
    assert current_posting.frequency==1
    
    current_posting=pl_reader.nextGEQ(81)
    
    assert current_posting!=None
    assert current_posting.doc_id==82
    assert current_posting.frequency==1
    
    
    current_posting=pl_reader.nextGEQ(1850)
    assert current_posting!=None
    assert current_posting.doc_id==1850
    assert current_posting.frequency==1
    
    current_posting=next(pl_reader)
    assert current_posting!=None
    assert current_posting.doc_id==1852
    assert current_posting.frequency==1
    
    #Exceed the max number in the posting list but still remains on current_value not_replacing it.
    current_posting=pl_reader.nextGEQ(100000)
    assert current_posting==None
    
    current_posting=next(pl_reader)
    assert current_posting.doc_id==1854
    assert current_posting.frequency==1
    
    i=0
    for elem in pl_reader:
        i+=1
        
    current_posting=next(pl_reader)
    assert current_posting==None
    
    
    current_posting=pl_reader.nextGEQ(54)
    assert current_posting==None
    
    current_posting=pl_reader.nextGEQ(100000)
    assert current_posting==None
    
    
    lexicon_file.close()
    doc_id_file.close()
    freq_file.close()
    block_file.close()


# In[7]:


#%%ipytest
def test_fake_test_to_delete_folders():
    
    if os.path.exists(DIR_LEXICON):
        shutil.rmtree(DIR_LEXICON)
                
    if os.path.exists(DIR_INVERTED_INDEX):
        shutil.rmtree(DIR_INVERTED_INDEX)
    
    if os.path.exists(DIR_DOC_INDEX):
        shutil.rmtree(DIR_DOC_INDEX)
    
    if os.path.exists(DIR_TEMP_FOLDER):
        shutil.rmtree(DIR_TEMP_FOLDER)
        
    assert 1==1

