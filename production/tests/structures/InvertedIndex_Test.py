#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ipytest
#import import_ipynb
import os

import sys
sys.path.append('../../')  # Go up two folders to the project root


from structures.InvertedIndex import Posting, InvertedIndex
from structures.DocumentIndex import DocumentIndex


# # Tests

# In[2]:


# import ipytest

# ipytest.autoconfig()


# In[3]:


#%%ipytest

#Testing Posting methods

def test_posting_data_structure():
    posting_1=Posting(4,5)
    
    assert posting_1.doc_id==4
    assert posting_1.frequency==5
    
    posting_2=Posting.from_string("1:45")
    assert posting_2.doc_id==1
    assert posting_2.frequency==45
    
    
    posting1=Posting.from_string("1:2")
    posting2=Posting.from_string("56:98")
 
    assert posting1.doc_id==1
    assert posting1.frequency==2
    assert posting2.doc_id==56
    assert posting2.frequency==98
   
    
def test_posting_write_to_disk():
    
    posting1=Posting(1,2)
    
    if os.path.exists("prova.bin"):
        os.remove("prova.bin")
    
    #Write a posting at position 0.
    new_free_offset=posting1.write_to_disk("prova.bin","type_doc_id",0)
    
    #Read it again and check all field are correctly present in binary format.
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()
        assert len(binaryData)==4
        assert binaryData[0]==1
        assert new_free_offset==4 #integer dimension
        
    posting2=Posting(57,77)
    
    #Write a posting at position 4.
    new_free_offset=posting2.write_to_disk("prova.bin","type_doc_id",4)
    
    with open("prova.bin", 'rb') as file:
        binaryData=file.read()
        assert len(binaryData)==4*2
        assert binaryData[0]==1
        assert binaryData[4]==57
        assert new_free_offset==4*2 #integer dimension
        
    os.remove("prova.bin") 


# In[8]:


#%%ipytest
#Test InvertedIndex Datastructure and methods

def test_inverted_index_data_structure_and_main_methods():
    ind = InvertedIndex()
    ind.add_posting("term", 1, 1)
    ind.add_posting("term", 2, 4)
    
    # Testing existing term
    postings = ind.get_postings("term")
    assert len(postings) == 2
    assert postings[0].doc_id == 1
    assert postings[0].frequency == 1
    assert postings[1].doc_id == 2
    assert postings[1].frequency == 4
   
    # Testing non-existent term
    assert ind.get_postings("xyx") is None
    
    #Test is_empty and clear_structure and get_structure
    assert ind.is_empty() == False
    ind.clear_structure()
    assert ind.is_empty() ==True
    assert ind.get_postings("term") == None
    ind.add_posting("term", 57, 4)
    ind2=ind.get_structure()
    assert ind.get_postings("term")[0].doc_id==ind2["term"][0].doc_id and ind.get_postings("term")[0].frequency==ind2["term"][0].frequency
    
    #Test vocabulary
    ind = InvertedIndex()
    ind.add_posting("term1", 1)
    ind.add_posting("term2", 1)
    ind.add_posting("term3", 2)
    ind.add_posting("term2", 3)
    assert set(ind.get_terms()) == set(["term1", "term2", "term3"])
    
    
    postingList_1=[Posting(1,2),Posting(2,5),Posting(6,7)]
    postingList_2=[Posting(14,3)]
    
    assert InvertedIndex.merge_posting_lists(postingList_1,postingList_2)==postingList_1+postingList_2
    
    assert InvertedIndex.compute_max_term_frequency_of_posting_list(postingList_1)==7
    assert InvertedIndex.compute_max_term_frequency_of_posting_list(postingList_2)==3
    assert InvertedIndex.compute_max_term_frequency_of_posting_list([])==0
    
    
def test_write_to_files_a_posting_list():
    
    posting_list=[Posting(1,1524),Posting(2,91),Posting(6,101)]
    
    if os.path.exists("doc_ids.bin"):
        os.remove("doc_ids.bin")
    
    if os.path.exists("freq.bin"):
        os.remove("freq.bin")
    
    file_doc_ids=open("doc_ids.bin", 'ab') 
    file_freq=open("freq.bin", 'ab')
    
    new_doc_ids_offset,new_freq_offset=InvertedIndex.write_to_files_a_posting_list(posting_list,False,file_doc_ids,file_freq,0,0)
    
    file_doc_ids.close()  
    file_freq.close()
    
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    doc_id_contents=file_doc_ids_read.read()
    freq_contents=file_freq_read.read()
    
    file_doc_ids_read.close()
    file_freq_read.close()
    
    assert new_doc_ids_offset==4*len(posting_list)
    assert new_freq_offset==4*len(posting_list)
    
    assert doc_id_contents[0]==0
    assert doc_id_contents[1]==0
    assert doc_id_contents[2]==0
    assert doc_id_contents[3]==1
    
    assert doc_id_contents[4]==0
    assert doc_id_contents[5]==0
    assert doc_id_contents[6]==0
    assert doc_id_contents[7]==2
    
    assert doc_id_contents[8]==0
    assert doc_id_contents[9]==0
    assert doc_id_contents[10]==0
    assert doc_id_contents[11]==6
    
    
    assert freq_contents[0]==0
    assert freq_contents[1]==0
    assert freq_contents[2]==5
    assert freq_contents[3]==244
    
    assert freq_contents[4]==0
    assert freq_contents[5]==0
    assert freq_contents[6]==0
    assert freq_contents[7]==91
    
    assert freq_contents[8]==0
    assert freq_contents[9]==0
    assert freq_contents[10]==0
    assert freq_contents[11]==101
    
    #Adding new element and save it on disk.
    
    posting_list_new=[Posting(14,3)]
    
    
    file_doc_ids=open("doc_ids.bin", 'ab') 
    file_freq=open("freq.bin", 'ab')
    
    new_doc_ids_offset,new_freq_offset=InvertedIndex.write_to_files_a_posting_list(posting_list_new,False,file_doc_ids,file_freq,new_doc_ids_offset,new_freq_offset)
    
    file_doc_ids.close()  
    file_freq.close()
    
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    doc_id_contents=file_doc_ids_read.read()
    freq_contents=file_freq_read.read()
    
    file_doc_ids_read.close()
    file_freq_read.close()
    
    assert new_doc_ids_offset==4*len(posting_list)+4*len(posting_list_new)
    assert new_freq_offset==4*len(posting_list)+4*len(posting_list_new)
    
    #The same test as before, nothing should be changed.
    
    assert doc_id_contents[0]==0
    assert doc_id_contents[1]==0
    assert doc_id_contents[2]==0
    assert doc_id_contents[3]==1
    
    assert doc_id_contents[4]==0
    assert doc_id_contents[5]==0
    assert doc_id_contents[6]==0
    assert doc_id_contents[7]==2
    
    assert doc_id_contents[8]==0
    assert doc_id_contents[9]==0
    assert doc_id_contents[10]==0
    assert doc_id_contents[11]==6
    
    
    assert freq_contents[0]==0
    assert freq_contents[1]==0
    assert freq_contents[2]==5
    assert freq_contents[3]==244
    
    assert freq_contents[4]==0
    assert freq_contents[5]==0
    assert freq_contents[6]==0
    assert freq_contents[7]==91
    
    assert freq_contents[8]==0
    assert freq_contents[9]==0
    assert freq_contents[10]==0
    assert freq_contents[11]==101
    
    #Testing new element already added.
    
    assert doc_id_contents[12]==0
    assert doc_id_contents[13]==0
    assert doc_id_contents[14]==0
    assert doc_id_contents[15]==14
    
    assert freq_contents[12]==0
    assert freq_contents[13]==0
    assert freq_contents[14]==0
    assert freq_contents[15]==3
    
    os.remove("doc_ids.bin")
    os.remove("freq.bin")
    
    
    #Testing the same thing but with compression true
    
    posting_list=[Posting(1,3),Posting(2,5),Posting(6,7)]
    
    file_doc_ids=open("doc_ids.bin", 'ab') 
    file_freq=open("freq.bin", 'ab')
    
    new_doc_ids_offset,new_freq_offset=InvertedIndex.write_to_files_a_posting_list(posting_list,True,file_doc_ids,file_freq,0,0)
    
    file_doc_ids.close()  
    file_freq.close()
    
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    doc_id_contents=file_doc_ids_read.read()
    freq_contents=file_freq_read.read()
    
    file_doc_ids_read.close()
    file_freq_read.close()
    
    #Remember for doc_id used d-gap compression
    assert new_doc_ids_offset==3
    assert new_freq_offset==2
    
    assert len(doc_id_contents)==3
    assert doc_id_contents[0]==1
    assert doc_id_contents[1]==1
    assert doc_id_contents[2]==4
    
    #Remember for freq used unary compression
    assert freq_contents[0]==222
    assert freq_contents[1]==252
   
    new_posting_list_new=[Posting(14,1)]
    
    file_doc_ids=open("doc_ids.bin", 'ab') 
    file_freq=open("freq.bin", 'ab')
    
    new_doc_ids_offset,new_freq_offset=InvertedIndex.write_to_files_a_posting_list(new_posting_list_new,True,file_doc_ids,file_freq,new_doc_ids_offset,new_freq_offset)
    
    file_doc_ids.close()  
    file_freq.close()
    
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    doc_id_contents=file_doc_ids_read.read()
    freq_contents=file_freq_read.read()
    
    file_doc_ids_read.close()
    file_freq_read.close()
    
    #Remember for doc_id used d-gap compression
    assert new_doc_ids_offset==4
    assert new_freq_offset==3
    
    assert len(doc_id_contents)==4
    assert doc_id_contents[0]==1
    assert doc_id_contents[1]==1
    assert doc_id_contents[2]==4
    assert doc_id_contents[3]==1
    
    #Remember for freq used unary compression
    assert freq_contents[0]==222
    assert freq_contents[1]==252
    assert freq_contents[2]==0
    
    os.remove("doc_ids.bin")
    os.remove("freq.bin")
    
       
def test_read_from_files_a_posting_list():
   
    if os.path.exists("doc_ids.bin"):
        os.remove("doc_ids.bin")
    
    if os.path.exists("freq.bin"):
        os.remove("freq.bin")
    
    posting_list=[Posting(1,3),Posting(2,5),Posting(6,7)]
    
    file_doc_ids=open("doc_ids.bin", 'ab') 
    file_freq=open("freq.bin", 'ab')
    
    new_doc_ids_offset,new_freq_offset=InvertedIndex.write_to_files_a_posting_list(posting_list,False,file_doc_ids,file_freq,0,0)
    
    file_doc_ids.close()  
    file_freq.close()
    
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    loaded_posting_list,new_doc_offset,new_freq_offset=InvertedIndex.read_from_files_a_posting_list(file_doc_ids_read,file_freq_read,False,0,0,3)
    
    file_doc_ids_read.close()
    file_freq_read.close()
    
    assert len(loaded_posting_list)==len(posting_list)
    
    assert new_doc_offset==4*len(loaded_posting_list)
    assert new_freq_offset==4*len(loaded_posting_list)
    assert loaded_posting_list[0].doc_id==posting_list[0].doc_id
    assert loaded_posting_list[0].frequency==posting_list[0].frequency
    assert loaded_posting_list[1].doc_id==posting_list[1].doc_id
    assert loaded_posting_list[1].frequency==posting_list[1].frequency
    assert loaded_posting_list[2].doc_id==posting_list[2].doc_id
    assert loaded_posting_list[2].frequency==posting_list[2].frequency
    
    
    #Read just a subset of posting from the second pos to third.
    
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    loaded_posting_list,new_doc_offset,new_freq_offset=InvertedIndex.read_from_files_a_posting_list(file_doc_ids_read,file_freq_read,False,4,4,2)
    
    file_doc_ids_read.close()
    file_freq_read.close()
    
    
    assert len(loaded_posting_list)==len(posting_list)-1
    
    assert loaded_posting_list[0].doc_id==posting_list[1].doc_id
    assert loaded_posting_list[0].frequency==posting_list[1].frequency
    assert loaded_posting_list[1].doc_id==posting_list[2].doc_id
    assert loaded_posting_list[1].frequency==posting_list[2].frequency

    os.remove("doc_ids.bin")
    os.remove("freq.bin")
    
    #Do the same but considering compression
    
    posting_list=[Posting(1,3),Posting(2,5),Posting(6,7)]
    
    file_doc_ids=open("doc_ids.bin", 'ab') 
    file_freq=open("freq.bin", 'ab')
    
    new_doc_ids_offset,new_freq_offset=InvertedIndex.write_to_files_a_posting_list(posting_list,True,file_doc_ids,file_freq,0,0)
    
    file_doc_ids.close()  
    file_freq.close()
    
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    #This information should arrive from block descriptor
    doc_id_size=new_doc_ids_offset
    freq_size=new_freq_offset
    min_doc_id=1
    
    loaded_posting_list,new_doc_offset,new_freq_offset=InvertedIndex.read_from_files_a_posting_list(file_doc_ids_read,file_freq_read,True,0,0,3,doc_id_size,freq_size,min_doc_id)
    
    file_doc_ids_read.close()
    file_freq_read.close()
    
    assert len(loaded_posting_list)==len(posting_list)
    
    #Remember for doc_id used d-gap compression
    assert new_doc_offset==3
    #Remember for freq used unary compression
    assert new_freq_offset==2
    
    assert loaded_posting_list[0].doc_id==posting_list[0].doc_id
    assert loaded_posting_list[0].frequency==posting_list[0].frequency
    assert loaded_posting_list[1].doc_id==posting_list[1].doc_id
    assert loaded_posting_list[1].frequency==posting_list[1].frequency
    assert loaded_posting_list[2].doc_id==posting_list[2].doc_id
    assert loaded_posting_list[2].frequency==posting_list[2].frequency

    os.remove("doc_ids.bin")
    os.remove("freq.bin")
    
    
    
def test_write_to_block_all_index_in_memory():
    
    ind=InvertedIndex()
    ind.add_posting("ciao", 1, 5)
    ind.add_posting("ciao", 2, 3)
    
    ind.add_posting("dado", 1, 8)
    ind.add_posting("dado", 3, 1)
    
    ind.add_posting("penna", 4, 1)
    ind.add_posting("penna", 5, 3)
    ind.add_posting("penna", 6, 1)
    
    docIndex=DocumentIndex()
    docIndex.add_document(1,"doc1","ttttt")
    docIndex.add_document(2,"doc2","ttttt")
    docIndex.add_document(3,"doc3","bbbbb")
    docIndex.add_document(4,"doc4","bbbbb")
    docIndex.add_document(5,"doc4","sssss")
    docIndex.add_document(6,"doc4","ccccc")
    
    
    ind.write_to_block_all_index_in_memory(docIndex,"lexicon.bin","doc_ids.bin","freq.bin")
    
    assert os.path.exists("lexicon.bin")==True
    assert os.path.exists("doc_ids.bin")==True
    assert os.path.exists("freq.bin")==True
    
    file_lexicon_read=open("lexicon.bin", 'rb') 
    file_doc_ids_read=open("doc_ids.bin", 'rb') 
    file_freq_read=open("freq.bin", 'rb')
    
    
    byteLexicon=file_lexicon_read.read()
    byteDoc_ids=file_doc_ids_read.read()
    byteFreq=file_freq_read.read()
    

    file_lexicon_read.close()
    file_doc_ids_read.close()
    file_freq_read.close()
    
    #Just to check if lexicon file is not empty and contains the three terms.
    
    #Correct lexicon term saved.
    
    assert str(byteLexicon[0:4])=="b'ciao'"
    assert str(byteLexicon[100:104])=="b'dado'"
    assert str(byteLexicon[200:205])=="b'penna'"
    
    #Tot postings.
    assert byteLexicon[32]==2
    assert byteLexicon[132]==2
    assert byteLexicon[232]==3
    
    #Other checks are done in LexiconRow File
    
    assert byteDoc_ids[0]==0
    assert byteDoc_ids[1]==0
    assert byteDoc_ids[2]==0
    assert byteDoc_ids[3]==1
    
    assert byteDoc_ids[4]==0
    assert byteDoc_ids[5]==0
    assert byteDoc_ids[6]==0
    assert byteDoc_ids[7]==2
    
    assert byteDoc_ids[8]==0
    assert byteDoc_ids[9]==0
    assert byteDoc_ids[10]==0
    assert byteDoc_ids[11]==1
    
    assert byteDoc_ids[12]==0
    assert byteDoc_ids[13]==0
    assert byteDoc_ids[14]==0
    assert byteDoc_ids[15]==3
    
    assert byteDoc_ids[19]==4
    assert byteDoc_ids[23]==5
    assert byteDoc_ids[27]==6
    
    assert byteFreq[0]==0
    assert byteFreq[1]==0
    assert byteFreq[2]==0
    assert byteFreq[3]==5
    
    assert byteFreq[4]==0
    assert byteFreq[5]==0
    assert byteFreq[6]==0
    assert byteFreq[7]==3
    
    assert byteFreq[8]==0
    assert byteFreq[9]==0
    assert byteFreq[10]==0
    assert byteFreq[11]==8
    
    assert byteFreq[12]==0
    assert byteFreq[13]==0
    assert byteFreq[14]==0
    assert byteFreq[15]==1
    
    assert byteFreq[19]==1
    assert byteFreq[23]==3
    assert byteFreq[27]==1
    
    if os.path.exists("lexicon.bin"):
        os.remove("lexicon.bin")
           
    if os.path.exists("doc_ids.bin"):
        os.remove("doc_ids.bin")
        
    if os.path.exists("freq.bin"):
        os.remove("freq.bin")    
    
    
    
def test_read_from_block_all_index_in_memory():
    
    ind=InvertedIndex()
    ind.add_posting("ciao", 1, 5)
    ind.add_posting("ciao", 2, 3)
    
    ind.add_posting("dado", 1, 8)
    ind.add_posting("dado", 3, 1)
    
    ind.add_posting("penna", 4, 1)
    ind.add_posting("penna", 5, 3)
    ind.add_posting("penna", 6, 1)
    
    docIndex=DocumentIndex()
    docIndex.add_document(1,"doc1","ttttt")
    docIndex.add_document(2,"doc2","ttttt")
    docIndex.add_document(3,"doc3","bbbbb")
    docIndex.add_document(4,"doc4","bbbbb")
    docIndex.add_document(5,"doc4","sssss")
    docIndex.add_document(6,"doc4","ccccc")
    
    ind.write_to_block_all_index_in_memory(docIndex,"lexicon.bin","doc_ids.bin","freq.bin")
    
    
    ind2=InvertedIndex()
    
    ind2.read_from_block_all_index_in_memory("lexicon.bin","doc_ids.bin","freq.bin")
    
    posting_ciao=ind2.get_postings("ciao".ljust(30))
    posting_dado=ind2.get_postings("dado".ljust(30))
    posting_penna=ind2.get_postings("penna".ljust(30))
    
    posting_nulla=ind2.get_postings("nulla".ljust(30))
    
    assert len(posting_ciao)==2
    assert len(posting_dado)==2
    assert len(posting_penna)==3
    assert posting_nulla==None
    
    assert posting_ciao[0].doc_id==1
    assert posting_ciao[1].doc_id==2
    
    assert posting_dado[0].doc_id==1
    assert posting_dado[1].doc_id==3
    
    assert posting_penna[0].doc_id==4
    assert posting_penna[1].doc_id==5
    assert posting_penna[2].doc_id==6
    
    assert posting_ciao[0].frequency==5
    assert posting_ciao[1].frequency==3
    
    assert posting_dado[0].frequency==8
    assert posting_dado[1].frequency==1
    
    assert posting_penna[0].frequency==1
    assert posting_penna[1].frequency==3
    assert posting_penna[2].frequency==1
    
    
    if os.path.exists("lexicon.bin"):
        os.remove("lexicon.bin")
           
    if os.path.exists("doc_ids.bin"):
        os.remove("doc_ids.bin")
        
    if os.path.exists("freq.bin"):
        os.remove("freq.bin")    

