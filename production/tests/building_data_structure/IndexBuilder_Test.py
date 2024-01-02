#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import import_ipynb
import os
import shutil

import sys
sys.path.append('../../')  # Go up two folders to the project root

from structures.InvertedIndex import Posting, InvertedIndex
from building_data_structures.IndexBuilder import IndexBuilder 
from structures.DocumentIndex import DocumentIndex
from pre_processing.Decompress_collection import Collection_Reader


# # Tests

# In[2]:


# import ipytest

# ipytest.autoconfig()


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


# %%ipytest

#Test InvertedIndex and Posting datastructures

def test_inverted_index_data_structure_and_methods():
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
    
def test_posting_data_structure():
    posting_1=Posting(4,5)
    
    assert posting_1.doc_id==4
    assert posting_1.frequency==5
    
    posting_2=Posting.from_string("1:45")
    assert posting_2.doc_id==1
    assert posting_2.frequency==45


# In[5]:


# %%ipytest

#In this part I'm gonna test the local structure for saving an entire inverted index in main memory.
#If this structure and its method is ok, then I can use it to simplfy further testing for complex documents.


def test_index_building():

    #Test buildInMemoryIndex
    
    test_documents=[
    "0\t this is a random sentence without punctuation",
    "1\t python is a versatile programming language",
    "2\t the quick brown fox jumps over the lazy dog",
    "3\t coding is a creative and logical process",
    "4\t sunsets are a beautiful sight to behold",
    "5\t coffee is a popular beverage around the world",
    "6\t music has the power to evoke emotions",
    "7\t books transport readers to different worlds",
    "8\t kindness and compassion make the world better",
    "9\t the moonlight reflects on the calm lake in the night the vision is awesome",
    "10\t nature provides solace and tranquility",
    "11\t imagination knows no boundaries",
    "12\t friendship is a treasure worth cherishing",
    "13\t happiness is found in simple moments",
    "14\t laughter is contagious and brings joy is better for all"
    ]
    
    
    
    indexBuilder=IndexBuilder(False,False,Collection_Reader("",-1,-1,False,False,test_documents))
    index=indexBuilder.build_in_memory_index(test_documents)
    
    assert len(index.get_postings("is"))==8 
    assert index.get_postings("is")[2].doc_id==3 and index.get_postings("is")[2].frequency==1
    assert index.get_postings("is")[7].doc_id==14 and index.get_postings("is")[7].frequency==2
    
    assert len(index.get_postings("python"))==1 
    assert index.get_postings("python")[0].doc_id==1 and index.get_postings("python")[0].frequency==1
    
    assert len(index.get_postings("the"))==5 
    assert index.get_postings("the")[4].doc_id==9 and index.get_postings("the")[4].frequency==4
    
    assert len(index.get_postings("friendship"))==1 
    assert index.get_postings("friendship")[0].doc_id==12
    assert index.get_postings("friendship")[0].frequency==1
    
    if os.path.exists(DIR_LEXICON):
        shutil.rmtree(DIR_LEXICON)
                
    if os.path.exists(DIR_INVERTED_INDEX):
        shutil.rmtree(DIR_INVERTED_INDEX)
    
    if os.path.exists(DIR_DOC_INDEX):
        shutil.rmtree(DIR_DOC_INDEX)
    
    if os.path.exists(DIR_TEMP_FOLDER):
        shutil.rmtree(DIR_TEMP_FOLDER)
    


# In[6]:


# %%ipytest


#The goal of this test is not to test if text_processing or compression is done, but just to consider
# if all the necessary data structure are created correctly and finally that the result is consistent with
# the method created above.

def test_correctness_of_spimi_plus_merging_with_multiple_block_size_creation_of_files(): 
     
        test_documents=[
        "0\t this is a random sentence without punctuation",
        "1\t python is a versatile programming language",
        "2\t the quick brown fox jumps over the lazy dog",
        "3\t coding is a creative and logical process",
        "4\t sunsets are a beautiful sight to behold",
        "5\t coffee is a popular beverage around the world",
        "6\t music has the power to evoke emotions",
        "7\t books transport readers to different worlds",
        "8\t kindness and compassion make the world better",
        "9\t the moonlight reflects on the calm lake in the night the vision is awesome",
        "10\t nature provides solace and tranquility",
        "11\t imagination knows no boundaries",
        "12\t friendship is a treasure worth cherishing",
        "13\t happiness is found in simple moments",
        "14\t laughter is contagious and brings joy is better for all"
        ]
        
        
        
        indexBuilder=IndexBuilder(True,False,Collection_Reader("",-1,-1,False,False,test_documents))
        indexBuilder.single_pass_in_memory_indexing(500)
        indexBuilder.index_merging()
    
        #Check if directories exists and are full of files
        
        if os.path.exists(DIR_TEMP_FOLDER):
            assert 1==1
        else:
            assert 1==-1
            
        if os.path.exists(DIR_DOC_INDEX):
            assert 1==1
        else:
            assert 1==2
        
        if os.path.exists(DIR_INVERTED_INDEX):
            assert 1==1
        else:
            assert 1==3
        
        if os.path.exists(DIR_LEXICON):
            assert 1==1
        else:
            assert 1==4
            
        directory_list=[DIR_TEMP_DOC_ID,DIR_TEMP_FREQ,DIR_TEMP_LEXICON]
        
        #Check if all the files inside TEMP are present and not empty: so this means that SPIMI has done its job correctly.
        for directory_name in directory_list:
            directory_path = os.path.join(DIR_TEMP_FOLDER, directory_name)

            if os.path.exists(directory_path) and os.path.isdir(directory_path):
                print(f"Checking files in directory: {directory_name}")

                # List all files in the directory
                files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

                if not files:
                    print(f"No files found in directory: {directory_name}")
                    assert 1==5
                else:
                    for filename in files:
                        file_path = os.path.join(directory_path, filename)
                        if os.path.getsize(file_path) > 0:
                            print(f"{filename} in {directory_name} is not empty.")
                            assert 1==1
                        else:
                            print(f"{filename} in {directory_name} is either empty or doesn't exist.")
                            assert 1==6
            else:
                print(f"Directory {directory_name} either doesn't exist or is not a directory.")
                assert 1==7
        
        #Test if debug is printed and considered.
        i=0
        for file in os.listdir(directory_path):
            if (file not in directory_list):
                i+=1
        assert i!=0
        
        #Check if all the files inside DOC_INDEX are present and not empty: so this means that SPIMI has done its job correctly.
        file_list=[PATH_COLLECTION_STATISTICS,PATH_COLLECTION_STATISTICS_DEBUG,PATH_FINAL_DOCUMENT_INDEX,PATH_FINAL_DOCUMENT_INDEX_DEBUG]
        
        i=0
        for file_name in file_list:
            nuovo_file=os.path.join(DIR_DOC_INDEX,file_name)
            if os.path.exists(nuovo_file) and os.path.getsize(nuovo_file) > 0:
                i+=1
        assert i==len(file_list)
        
        #Check if all the files inside INV_INDEX are present and not empty: so this means that MERGER has done its job correctly.
        
        file_list=[PATH_FINAL_DOC_IDS,PATH_FINAL_FREQ,PATH_FINAL_BLOCK_DESCRIPTOR,PATH_FINAL_INVERTED_INDEX_DEBUG]
        
        i=0
        for file_name in file_list:
            nuovo_file=os.path.join(DIR_INVERTED_INDEX,file_name)
            if os.path.exists(nuovo_file) and os.path.getsize(nuovo_file) > 0:
                i+=1
        assert i==len(file_list)        
          
        #Check if all the files inside LEXICON are present and not empty: so this means that MERGER has done its job correctly.
        
        file_list=[PATH_FINAL_LEXICON,PATH_FINAL_LEXICON_DEBUG]
        
        i=0
        for file_name in file_list:
            nuovo_file=os.path.join(DIR_LEXICON,file_name)
            if os.path.exists(nuovo_file) and os.path.getsize(nuovo_file) > 0:
                i+=1
        
        assert i==len(file_list) 
        
        if os.path.exists(DIR_LEXICON):
            shutil.rmtree(DIR_LEXICON)

        if os.path.exists(DIR_INVERTED_INDEX):
            shutil.rmtree(DIR_INVERTED_INDEX)

        if os.path.exists(DIR_DOC_INDEX):
            shutil.rmtree(DIR_DOC_INDEX)

        if os.path.exists(DIR_TEMP_FOLDER):
            shutil.rmtree(DIR_TEMP_FOLDER)
        
    


# In[7]:


# %%ipytest

#Here using the previous data structure to check if using spimi + merging it obtains the same result.
def test_correctness_of_spimi_plus_merging_with_multiple_block_size_content_of_index():
    
    
    test_documents=[
    "0\t this is a random sentence without punctuation",
    "1\t python is a versatile programming language",
    "2\t the quick brown fox jumps over the lazy dog",
    "3\t coding is a creative and logical process",
    "4\t sunsets are a beautiful sight to behold",
    "5\t coffee is a popular beverage around the world",
    "6\t music has the power to evoke emotions",
    "7\t books transport readers to different worlds",
    "8\t kindness and compassion make the world better",
    "9\t the moonlight reflects on the calm lake in the night the vision is awesome",
    "10\t nature provides solace and tranquility",
    "11\t imagination knows no boundaries",
    "12\t friendship is a treasure worth cherishing",
    "13\t happiness is found in simple moments",
    "14\t laughter is contagious and brings joy is better for all"
    ]
    
    
    
    indexBuilder=IndexBuilder(True,False,Collection_Reader("",-1,-1,False,False,test_documents))
    indexBuilder.single_pass_in_memory_indexing(500)
    indexBuilder.index_merging()
    
    
    ind_read_from_disk=InvertedIndex()
    
    i=0
    with open(DIR_INVERTED_INDEX+"\\"+PATH_FINAL_INVERTED_INDEX_DEBUG, "r") as file:
        for line in file:
            if (i==0): #In debug mode skip the first line.
                i+=1
                continue
            term=line.split()[0]
            postings_str_lst=line.split()[1:]

            for posting in  postings_str_lst:
                doc_id,freq=posting.split(":")
                ind_read_from_disk.add_posting(term,int(doc_id),int(freq))
            i+=1
    
    assert len(ind_read_from_disk.get_postings("is"))==8 
    assert ind_read_from_disk.get_postings("is")[2].doc_id==3 and ind_read_from_disk.get_postings("is")[2].frequency==1
    assert ind_read_from_disk.get_postings("is")[7].doc_id==14 and ind_read_from_disk.get_postings("is")[7].frequency==2

    assert len(ind_read_from_disk.get_postings("python"))==1 
    assert ind_read_from_disk.get_postings("python")[0].doc_id==1 and ind_read_from_disk.get_postings("python")[0].frequency==1

    assert len(ind_read_from_disk.get_postings("the"))==5 
    assert ind_read_from_disk.get_postings("the")[4].doc_id==9 and ind_read_from_disk.get_postings("the")[4].frequency==4

    assert len(ind_read_from_disk.get_postings("friendship"))==1 
    assert ind_read_from_disk.get_postings("friendship")[0].doc_id==12
    assert ind_read_from_disk.get_postings("friendship")[0].frequency==1
    
    
    if os.path.exists(DIR_LEXICON):
        shutil.rmtree(DIR_LEXICON)
                
    if os.path.exists(DIR_INVERTED_INDEX):
        shutil.rmtree(DIR_INVERTED_INDEX)
    
    if os.path.exists(DIR_DOC_INDEX):
        shutil.rmtree(DIR_DOC_INDEX)
    
    if os.path.exists(DIR_TEMP_FOLDER):
        shutil.rmtree(DIR_TEMP_FOLDER)


# In[8]:


# %%ipytest

#Check if the datastructure contains the correct informations

#Here using the previous data structure to check if using spimi + merging it obtains the same result.
def test_correctness_of_spimi_plus_merging_with_multiple_block_size_content_of_index():
    
    
    test_documents=[
    "doc0\t this is a random sentence without punctuation",
    "doc1\t python is a versatile programming language",
    "doc2\t the quick brown fox jumps over the lazy dog"

    ]
    
    
    #I care to reset it because it has been decided to be defined as singleton...
    docI=DocumentIndex()
    docI.number_of_documents=0
    docI.total_document_length=0
    
    indexBuilder=IndexBuilder(True,False,Collection_Reader("",-1,-1,False,False,test_documents))
    indexBuilder.single_pass_in_memory_indexing(500)
    indexBuilder.index_merging()
    
    
    ind_read_from_disk=InvertedIndex()
    
    i=0
    with open(DIR_INVERTED_INDEX+"\\"+PATH_FINAL_INVERTED_INDEX_DEBUG, "r") as file:
        for line in file:
            if (i==0): #In debug mode skip the first line.
                i+=1
                continue
            term=line.split()[0]
            postings_str_lst=line.split()[1:]

            for posting in  postings_str_lst:
                doc_id,freq=posting.split(":")
                ind_read_from_disk.add_posting(term,int(doc_id),int(freq))
            i+=1
    
    assert len(ind_read_from_disk.get_postings("is"))==2 
    assert ind_read_from_disk.get_postings("is")[1].doc_id==1 and ind_read_from_disk.get_postings("is")[1].frequency==1

    assert len(ind_read_from_disk.get_postings("python"))==1 
    assert ind_read_from_disk.get_postings("python")[0].doc_id==1 and ind_read_from_disk.get_postings("python")[0].frequency==1

    assert len(ind_read_from_disk.get_postings("the"))==1 
    assert ind_read_from_disk.get_postings("the")[0].doc_id==2 and ind_read_from_disk.get_postings("the")[0].frequency==2

    #Check if document statistic contains the right number of values
    path_coll_stat=os.path.join(DIR_DOC_INDEX,PATH_COLLECTION_STATISTICS_DEBUG)
    
    lines_read=[]
    with open(path_coll_stat, "r") as file:
        for line in file:
            lines_read.append(line)
    
    expected_output=["Document Index Size: 3\n","Vocabulary Size: 19\n","Sum Document length: 22\n"]
    
    for line,exp_output in zip(lines_read,expected_output):
        assert line==exp_output
    
    #Check if document index contains the right informations
    path_doc_index=os.path.join(DIR_DOC_INDEX,PATH_FINAL_DOCUMENT_INDEX_DEBUG)
    
    lines_read=[]
    with open(path_doc_index, "r") as file:
        for line in file:
            lines_read.append(line)
    
    expected_output=["0 doc0                           7\n","1 doc1                           6\n","2 doc2                           9\n"]
    
    for line,exp_output in zip(lines_read,expected_output):
        assert line==exp_output
    
    #Check if lexicon contains the right informations
    
    expected_output=["a                             \t2\t1\t0.176\t1.231\t1\t6\t0.074\t0\t0\t0\t8\t8\t1\n",
                     "brown                         \t1\t1\t0.477\t0.798\t1\t9\t0.166\t8\t8\t36\t4\t4\t1\n",
                     "dog                           \t1\t1\t0.477\t0.798\t1\t9\t0.166\t12\t12\t72\t4\t4\t1\n",
                     "fox                           \t1\t1\t0.477\t0.798\t1\t9\t0.166\t16\t16\t108\t4\t4\t1\n",
                     "is                            \t2\t1\t0.176\t1.231\t1\t6\t0.074\t20\t20\t144\t8\t8\t1\n",
                     "jumps                         \t1\t1\t0.477\t0.798\t1\t9\t0.166\t28\t28\t180\t4\t4\t1\n",
                     "language                      \t1\t1\t0.477\t0.798\t1\t6\t0.200\t32\t32\t216\t4\t4\t1\n",
                     "lazy                          \t1\t1\t0.477\t0.798\t1\t9\t0.166\t36\t36\t252\t4\t4\t1\n",
                     "over                          \t1\t1\t0.477\t0.798\t1\t9\t0.166\t40\t40\t288\t4\t4\t1\n",
                     "programming                   \t1\t1\t0.477\t0.798\t1\t6\t0.200\t44\t44\t324\t4\t4\t1\n",
                     "punctuation                   \t1\t1\t0.477\t0.798\t1\t7\t0.187\t48\t48\t360\t4\t4\t1\n",
                     "python                        \t1\t1\t0.477\t0.798\t1\t6\t0.200\t52\t52\t396\t4\t4\t1\n",
                     "quick                         \t1\t1\t0.477\t0.798\t1\t9\t0.166\t56\t56\t432\t4\t4\t1\n",
                     "random                        \t1\t1\t0.477\t0.798\t1\t7\t0.187\t60\t60\t468\t4\t4\t1\n",
                     "sentence                      \t1\t1\t0.477\t0.798\t1\t7\t0.187\t64\t64\t504\t4\t4\t1\n",
                     "the                           \t1\t2\t0.477\t1.039\t2\t9\t0.246\t68\t68\t540\t4\t4\t1\n",
                     "this                          \t1\t1\t0.477\t0.798\t1\t7\t0.187\t72\t72\t576\t4\t4\t1\n",
                     "versatile                     \t1\t1\t0.477\t0.798\t1\t6\t0.200\t76\t76\t612\t4\t4\t1\n",
                     "without                       \t1\t1\t0.477\t0.798\t1\t7\t0.187\t80\t80\t648\t4\t4\t1\n"
                    ]
    
    path_lexicon=os.path.join(DIR_LEXICON,PATH_FINAL_LEXICON_DEBUG)
    lines_read=[]
    i=0
    with open(path_lexicon, "r") as file:
        for line in file:
            if (i==0):
                i+=1
                continue
            lines_read.append(line)
            i+=1
            
    for line,exp_output in zip(lines_read,expected_output):
        assert line==exp_output 
    
    
    
    
    if os.path.exists(DIR_LEXICON):
        shutil.rmtree(DIR_LEXICON)
                
    if os.path.exists(DIR_INVERTED_INDEX):
        shutil.rmtree(DIR_INVERTED_INDEX)
    
    if os.path.exists(DIR_DOC_INDEX):
        shutil.rmtree(DIR_DOC_INDEX)
    
    if os.path.exists(DIR_TEMP_FOLDER):
        shutil.rmtree(DIR_TEMP_FOLDER)


# In[9]:


# %%ipytest

#Test if it works with different block size.
def test_correctness_of_spimi_plus_merging_with_multiple_block_size_content_of_index_with_different_blocks_size():
    
    
    test_documents=[
    "0\t this is a random sentence without punctuation",
    "1\t python is a versatile programming language",
    "2\t the quick brown fox jumps over the lazy dog",
    "3\t coding is a creative and logical process",
    "4\t sunsets are a beautiful sight to behold",
    "5\t coffee is a popular beverage around the world",
    "6\t music has the power to evoke emotions",
    "7\t books transport readers to different worlds",
    "8\t kindness and compassion make the world better",
    "9\t the moonlight reflects on the calm lake in the night the vision is awesome",
    "10\t nature provides solace and tranquility",
    "11\t imagination knows no boundaries",
    "12\t friendship is a treasure worth cherishing",
    "13\t happiness is found in simple moments",
    "14\t laughter is contagious and brings joy is better for all"
]

    
    
    #At each iteration it is aspected to obtain the same result for every possibile block size.
    for i in range(1,6):   #Test for different block size

        indexBuilder=IndexBuilder(True,False,Collection_Reader("",-1,-1,False,False,test_documents))
        indexBuilder.single_pass_in_memory_indexing(500*i)
        indexBuilder.index_merging()

        ind_read_from_disk=InvertedIndex()

        i=0
        with open(DIR_INVERTED_INDEX+"\\"+PATH_FINAL_INVERTED_INDEX_DEBUG, "r") as file:
            for line in file:
                if (i==0): #In debug mode skip the first line.
                    i+=1
                    continue
                term=line.split()[0]
                postings_str_lst=line.split()[1:]

                for posting in  postings_str_lst:
                    doc_id,freq=posting.split(":")
                    ind_read_from_disk.add_posting(term,int(doc_id),int(freq))
                i+=1

        assert len(ind_read_from_disk.get_postings("is"))==8 
        assert ind_read_from_disk.get_postings("is")[2].doc_id==3 and ind_read_from_disk.get_postings("is")[2].frequency==1
        assert ind_read_from_disk.get_postings("is")[7].doc_id==14 and ind_read_from_disk.get_postings("is")[7].frequency==2

        assert len(ind_read_from_disk.get_postings("python"))==1 
        assert ind_read_from_disk.get_postings("python")[0].doc_id==1 and ind_read_from_disk.get_postings("python")[0].frequency==1

        assert len(ind_read_from_disk.get_postings("the"))==5 
        assert ind_read_from_disk.get_postings("the")[4].doc_id==9 and ind_read_from_disk.get_postings("the")[4].frequency==4

        assert len(ind_read_from_disk.get_postings("friendship"))==1 
        assert ind_read_from_disk.get_postings("friendship")[0].doc_id==12
        assert ind_read_from_disk.get_postings("friendship")[0].frequency==1
        
    if os.path.exists(DIR_LEXICON):
        shutil.rmtree(DIR_LEXICON)
                
    if os.path.exists(DIR_INVERTED_INDEX):
        shutil.rmtree(DIR_INVERTED_INDEX)
    
    if os.path.exists(DIR_DOC_INDEX):
        shutil.rmtree(DIR_DOC_INDEX)
    
    if os.path.exists(DIR_TEMP_FOLDER):
        shutil.rmtree(DIR_TEMP_FOLDER)


# In[ ]:




