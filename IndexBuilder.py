#!/usr/bin/env python
# coding: utf-8

# In[3]:


import ipytest
import re

import sys
import shutil
import os
import operator

import time

from typing import List, Dict, Union, Any, Callable
from collections import Counter, defaultdict,OrderedDict
from dataclasses import dataclass


# In[4]:


# Since this is a simple data class, intializing it can be abstracted with
# the use of dataclass decorator.
# https://docs.python.org/3/library/dataclasses.html

@dataclass
class Posting:
    doc_id: int
    payload: Any = None
    
    @classmethod 
    def from_string(cls, description:str):
        docId,payl=description.split(":")
        doc_id=int(docId)
        payload=int(payl)
        return cls(doc_id, payload)
               
class InvertedIndex:

    def __init__(self):
        self._index = defaultdict(list)
        
    def add_posting(self, term: str, doc_id: int, payload: Any=None) -> None:
        """Adds a document to the posting list of a term."""
        # append new posting to the posting list
        if (self.get_postings(term)==None):
            self._index[term]=[]
        self._index[term].append(Posting(doc_id,payload))
             
    def get_postings(self, term: str) -> List[Posting]:
        """Fetches the posting list for a given term."""
        if (term in self._index):
            return self._index[term]
        return None
    
    def write_to_block(self,file_name_index: str) -> None:
        """ Write the inverted index in lexicographical oreder into a file_name_index on disk."""
        sorted_lexicon=sorted(self._index.items())
        with open(file_name_index, "w") as f:
            for term,postings in sorted_lexicon:
                f.write(term)
                for posting in postings:
                    f.write(f" {posting.doc_id}")
                    if posting.payload:
                        f.write(f":{str(posting.payload)}")
                f.write("\n")
    
    def is_empty(self)->bool:
        """Check if there is no term in the inverted index."""
        return len(self.get_terms())==0
    
    def get_terms(self) -> List[str]:
        """Returns all unique terms in the index."""
        return self._index.keys() 
    
    def clear_structure(self):
        """ It clears the inverted index data structure."""
        self._index.clear()
    
    def get_structure(self):
        """Returns the inverted index data structure."""
        return self._index


# In[5]:


class IndexBuilder:
    
    MAX_CHARATER=chr(1114111)
    
    OUTPUT_FILE_FORMAT=".txt"
    NAME_DOC_IDS_FILE="docIds"
    NAME_TERM_FREQ_FILE="termFreq"
    
    def __init__(self):
        print ("Index Builder costructor")
        #self._invertedIndex = InvertedIndex()

    def build_in_memory_index(self,list_of_documents:list)->InvertedIndex:
        """Given a list of document, build an Inverted Index in main Memory (RAM) and return it."""
        invertedIndex = InvertedIndex()
        for doc in list_of_documents:
            doc_id=list_of_documents.index(doc)
            tc = Counter(doc.lower().split())  # dict with term counts, QUI USARE DIRETTAMENTE IL CONTENUTO GIA' PRE-PROCESSATO
            for term, freq in tc.items():
                invertedIndex.add_posting(term, doc_id, freq)
        return invertedIndex


    def build_block_sort_base_indexing(self,list_of_documents:list,output_file_name:str,block_size: int=2200,split_results_in_files:bool=False, delete_intermediete_results:bool=True)-> None:
        """ Given a list of document, build an Inverted Index exploiting both Memory(RAM) at blocks and Disk. 
            It saves the entire structure on disk at location output_file_name.
            The file structure is like term doc_id:term_freq
               
         Args:
            list_of_documents: List of document to be processed.
            output_file_name: The location of where the structure is saved.
            block_size: The size of the block to elaborate in main memory and store on disk as intermediate result.
            split_results_in_files: Specify if you want or not the inderted index in two different files: the doc_ids file and the term_freq file
            delete_intermediete_results: Flag to remove partial results at the end of the procedure or not.
         
        """

        ind = InvertedIndex()
        nr_block=0

        DIR_FOLDER="TEMP"

        if os.path.exists(DIR_FOLDER):
            shutil.rmtree(DIR_FOLDER)

        os.makedirs(DIR_FOLDER)

    
        if (split_results_in_files):
            if os.path.exists(output_file_name+"_"+self.NAME_DOC_IDS_FILE+self.OUTPUT_FILE_FORMAT):
                os.remove(output_file_name+"_"+self.NAME_DOC_IDS_FILE+self.OUTPUT_FILE_FORMAT)
            
            if os.path.exists(output_file_name+"_"+self.NAME_TERM_FREQ_FILE+self.OUTPUT_FILE_FORMAT):
                os.remove(output_file_name+"_"+self.NAME_TERM_FREQ_FILE+self.OUTPUT_FILE_FORMAT)
        else:
            if os.path.exists(output_file_name+self.OUTPUT_FILE_FORMAT):
                os.remove(output_file_name+self.OUTPUT_FILE_FORMAT)
    
        #Map phase - read all the documents and write the index at blocks on disk when memory is full, cleaning the memory data structure.

        for doc in list_of_documents:
            doc_id=list_of_documents.index(doc)
            tc = Counter(doc.lower().split())  # dict with term counts, QUI USARE DIRETTAMENTE IL CONTENUTO GIA' PRE-PROCESSATO
            for term, freq in tc.items():
                if (sys.getsizeof(ind.get_structure()) > block_size):  #Free memory available
                    ind.write_to_block(DIR_FOLDER+"/lexicon_"+str(nr_block)+".txt")
                    ind.clear_structure()
                    nr_block=nr_block+1 
                ind.add_posting(term, doc_id, freq)
                
        #Finally, saving the last remaing block.       
        if (not ind.is_empty()):   
            ind.write_to_block(DIR_FOLDER+"/lexicon_"+str(nr_block)+".txt")


        # ----  Second part ----

        #Reduce phase --> merging all the blocks (multi-way merge sort) in one unique result and save it on disk. 
                       
        try:
            file_paths = [DIR_FOLDER+"/"+f for f in os.listdir(DIR_FOLDER)] 
            input_files = [open(file, 'r') for file in file_paths]  #Open all the blocks in parallel
            lines=[file.readline().strip() for file in input_files] #Read the first line of each block

            while (not self.__check_all_blocks_are_read(lines)):

                terms=[line.split()[0] if line else self.MAX_CHARATER for line in lines] #Contains a list of strings: the terms present at each line read in the blocks, if file is over put the max-unicode charater
                postings=[" ".join(line.split()[1:]) for line in lines] #Contains a list of strings: the postings present at each line read in the blocks.

                min_term=min(terms)  #Enstablishing what is the term to be considered: the term lexicografical ordered.

                #Merging the postings with the same min term
                mergePostings=[]
                for i in range (0,len(postings)):
                    if (min_term==terms[i]):  
                        self.__decode_string_posting_list_and_merge_to_current(mergePostings,postings[i].split())

                #Sorting by doc_id   
                mergePostings=sorted(mergePostings, key=operator.attrgetter('doc_id'))    
                self.__write_term_posting_list_to_disk(output_file_name,min_term,mergePostings,split_results_in_files)

                #Advance on reading the files in parallel only for blocks where was present the last min term.
                lines=[input_files[i].readline().strip() if (min_term==terms[i]) else lines[i] for i in range (0,len(terms))] 
        except Exception as e:   
            raise e
        finally:
            #Be sure to close all the opened files in parallel
            for file in input_files:
                file.close()  

        if (delete_intermediete_results):
            shutil.rmtree(DIR_FOLDER)

    
    #Private methods: all utilities used inside main methods to make code more readable.
    
    def __check_all_blocks_are_read(self,lines:list)->bool:
        """ This method is used to check whether all files opened in parallel have been completely read or not
            It checks the contents that have been read to determine the condition.
            
            Args:
                 lines: A list of lines(str) read before.
        """
        for line in lines:
            if line:
                return False
        return True
    
    
    def __decode_string_posting_list_and_merge_to_current(self,current_postings_list:list, new_string_posting_list:str):
        """ This method is used for adding/merging a posting list in string format to the list of current_postings. 
            This method check if current_postings already contains a posting with a doc_id, in that case the term_freq is sum
            otherwise the posting is append to the current_postings.
            
            Args:
                current_postings_list: the actual posting list
                new_string_posting_list: the new posting list to be merged in string format ex. doc_id_1:term_freq_1 doc_id_2:term_freq_2  
        """
        current_docIds=[] #Used to store and retrieve rapidly the actual doc_id in the current_postings_list
        if (len(current_postings_list)>0):
            current_docIds=[curr_posting.doc_id for curr_posting in current_postings_list]
        
        for posting_str in new_string_posting_list: #posting_str is a single posting in the form "docId:freq"
            posting=Posting.from_string(posting_str)
            if (posting.doc_id in current_docIds): 
                current_postings_list[current_docIds.index(posting.doc_id)]+=posting.payload 
            else:
                current_postings_list.append(posting)
        
    def __write_term_posting_list_to_disk(self,file_name:str,term:str,merged_postings_list:list,split_results_in_files:bool):
        """ This method is used to write in a file on disk in append mode a full entry of the lexicon in the format ex.
            term doc_id_1:term_freq_1 doc_id_2:term_freq_2 doc_id_3:term_freq_3 ... 
            
            Args:
                file_name: the name of the output file 
                term: the lexicon term
                merged_postings_list: the full merged posting list
                split_results_in_files: Specify if you want or not the inderted index in two different files: the doc_ids file and the term_freq file
        """
       
        
        if(not split_results_in_files):
            with open(file_name+self.OUTPUT_FILE_FORMAT, "a") as f:
                f.write(term)
                for posting in merged_postings_list:
                    f.write(f" {posting.doc_id}")
                    if posting.payload:
                        f.write(f":{str(posting.payload)}")
                f.write("\n")
        else:
            
             with open(file_name+"_"+self.NAME_DOC_IDS_FILE+self.OUTPUT_FILE_FORMAT, "a") as f:
                for index, posting in enumerate(merged_postings_list):
                    f.write(str(posting.doc_id))
                    if index != len(merged_postings_list) - 1:
                        f.write(",")
                f.write("\n")
            
             with open(file_name+"_"+self.NAME_TERM_FREQ_FILE+self.OUTPUT_FILE_FORMAT, "a") as f:
                for index, posting in enumerate(merged_postings_list):
                    f.write(str(posting.payload))
                    if index != len(merged_postings_list) - 1:
                        f.write(",")
                f.write("\n")


# In[ ]:





# # Tests

# In[6]:


import ipytest

ipytest.autoconfig()


# In[7]:


get_ipython().run_cell_magic('ipytest', '', '\n#Test InvertedIndex and Posting datastructures\n\ndef test_inverted_index_data_structure_and_methods():\n    ind = InvertedIndex()\n    ind.add_posting("term", 1, 1)\n    ind.add_posting("term", 2, 4)\n    \n    # Testing existing term\n    postings = ind.get_postings("term")\n    assert len(postings) == 2\n    assert postings[0].doc_id == 1\n    assert postings[0].payload == 1\n    assert postings[1].doc_id == 2\n    assert postings[1].payload == 4\n   \n    # Testing non-existent term\n    assert ind.get_postings("xyx") is None\n    \n    #Test is_empty and clear_structure and get_structure\n    assert ind.is_empty() == False\n    ind.clear_structure()\n    assert ind.is_empty() ==True\n    assert ind.get_postings("term") == None\n    ind.add_posting("term", 57, 4)\n    ind2=ind.get_structure()\n    assert ind.get_postings("term")[0].doc_id==ind2["term"][0].doc_id and ind.get_postings("term")[0].payload==ind2["term"][0].payload\n    \n    #Test vocabulary\n    ind = InvertedIndex()\n    ind.add_posting("term1", 1)\n    ind.add_posting("term2", 1)\n    ind.add_posting("term3", 2)\n    ind.add_posting("term2", 3)\n    assert set(ind.get_terms()) == set(["term1", "term2", "term3"])\n    \ndef test_posting_data_structure():\n    posting_1=Posting(4,5)\n    \n    assert posting_1.doc_id==4\n    assert posting_1.payload==5\n    \n    posting_2=Posting.from_string("1:45")\n    assert posting_2.doc_id==1\n    assert posting_2.payload==45')


# In[8]:


test_documents=[
    "this is a random sentence without punctuation",
    "python is a versatile programming language",
    "the quick brown fox jumps over the lazy dog",
    "coding is a creative and logical process",
    "sunsets are a beautiful sight to behold",
    "coffee is a popular beverage around the world",
    "music has the power to evoke emotions",
    "books transport readers to different worlds",
    "kindness and compassion make the world better",
    "the moonlight reflects on the calm lake",
    "nature provides solace and tranquility",
    "imagination knows no boundaries",
    "friendship is a treasure worth cherishing",
    "happiness is found in simple moments",
    "laughter is contagious and brings joy"
]


# In[9]:


get_ipython().run_cell_magic('ipytest', '', '\nindexBuilder=IndexBuilder()\n\ntest_documents=[\n    "this is a random sentence without punctuation",\n    "python is a versatile programming language",\n    "the quick brown fox jumps over the lazy dog",\n    "coding is a creative and logical process",\n    "sunsets are a beautiful sight to behold",\n    "coffee is a popular beverage around the world",\n    "music has the power to evoke emotions",\n    "books transport readers to different worlds",\n    "kindness and compassion make the world better",\n    "the moonlight reflects on the calm lake in the night the vision is awesome",\n    "nature provides solace and tranquility",\n    "imagination knows no boundaries",\n    "friendship is a treasure worth cherishing",\n    "happiness is found in simple moments",\n    "laughter is contagious and brings joy is better for all"\n]\n\n\ndef test_index_building():\n\n    #Test buildInMemoryIndex\n    \n    index=indexBuilder.build_in_memory_index(test_documents)\n    \n    assert len(index.get_postings("is"))==8 \n    assert index.get_postings("is")[2].doc_id==3 and index.get_postings("is")[2].payload==1\n    assert index.get_postings("is")[7].doc_id==14 and index.get_postings("is")[7].payload==2\n    \n    assert len(index.get_postings("python"))==1 \n    assert index.get_postings("python")[0].doc_id==1 and index.get_postings("python")[0].payload==1\n    \n    assert len(index.get_postings("the"))==5 \n    assert index.get_postings("the")[4].doc_id==9 and index.get_postings("the")[4].payload==4\n\n\n    \n    \n    #Test Blocked Sort-Based Indexing\n    \n    for i in range(1,6):   #Test for different block size\n        \n        indexBuilder.build_block_sort_base_indexing(test_documents,"complete_inverted_index_TEST"+str(i),500*i,False,True)\n\n        #After testing the correctness of in memory index\n        #for this short document collection I read the output file and store it in main memory, \n        #then check the correct presence of terms and postings.\n\n        ind_read_from_disk=InvertedIndex()\n        with open("complete_inverted_index_TEST"+str(i)+indexBuilder.OUTPUT_FILE_FORMAT, "r") as file:\n            for line in file:\n\n                term=line.split()[0]\n                postings_str_lst=line.split()[1:]\n\n                for posting in  postings_str_lst:\n                    doc_id,freq=posting.split(":")\n                    ind_read_from_disk.add_posting(term,int(doc_id),int(freq))\n\n\n        assert len(ind_read_from_disk.get_postings("is"))==8 \n        assert ind_read_from_disk.get_postings("is")[2].doc_id==3 and ind_read_from_disk.get_postings("is")[2].payload==1\n        assert ind_read_from_disk.get_postings("is")[7].doc_id==14 and ind_read_from_disk.get_postings("is")[7].payload==2\n\n        assert len(ind_read_from_disk.get_postings("python"))==1 \n        assert ind_read_from_disk.get_postings("python")[0].doc_id==1 and ind_read_from_disk.get_postings("python")[0].payload==1\n\n        assert len(ind_read_from_disk.get_postings("the"))==5 \n        assert ind_read_from_disk.get_postings("the")[4].doc_id==9 and ind_read_from_disk.get_postings("the")[4].payload==4\n    ')


# # Example of usage

# In[10]:


# tot_doc=[
#             "The pen is on the table",
#             "The day is very sunny",
#             "Goodmoring new article",
#             "A cat is faster then a dog",
#             "How are you",
#             "A boy is a man with low age",
#             "Lake Ontario is one of the biggest lake in the world",
#             "English is worst than Italian",
#             "Spiderman is the best superhero in Marvel universe",
#             "Last night I saw a Netflix series",
#             "A penny for your thoughts",
#             "Actions speak louder than words",
#             "All that glitters is not gold",
#             "Beauty is in the eye of the beholder",
#             "Birds of a feather flock together",
#             "Cleanliness is next to godliness",
#             "Don't count your chickens before they hatch",
#             "Every people cloud has a silver lining people",
#             "Fool me once shame on you fool me twice shame on me",
#             "Honesty is the best policy.",
#             "If the shoe fits, wear it",
#             "It's a piece of cake",
#             "Jump on the bandwagon",
#             "Keep your chin up",
#             "Let the cat out of the bag",
#             "Make a long story short",
#             "Necessity is the mother of invention",
#             "Once in a blue moon",
#             "Practice makes perfect",
#             "Read between the lines",
#             "The early bird catches people the worm",
#             "The pen is mightier than the sword",
#             "There's no smoke without fire",
#             "To each his own",
#             "Two heads are better than one",
#             "You can't have your cake and eat it too",
#             "A watched pot never boils",
#             "Beggars can't be choosers",
#             "Better late than never",
#             "Calm before the storm",
#             "Curiosity killed the cat",
#             "Every dog has its day",
#             "Great minds think alike",
#             "Hope for the best prepare for the worst",
#             "Ignorance is bliss.",
#             "It's the last straw that breaks the camel's back",
#             "Laugh and the world laughs with you weep and you weep alone",
#             "Money can't buy happiness",
#             "No news is good news",
#             "Out of sight out of mind",
#             "People who live in glass houses shouldn't throw stones",
#             "Rome wasn't built in a day",
#             "Silence is golden",
#             "The apple doesn't fall far from the tree",
#             "The more, the merrier",
#             "There's no place like home",
#             "Two wrongs don't make a right",
#             "When in Rome do as the Romans do",
#             "You reap what you sow",
#             "People people people"]


# indexBuilder=IndexBuilder()
# #ii=indexBuilder.build_in_memory_index(tot_doc)
# indexBuilder.build_block_sort_base_indexing(tot_doc,"complete_inverted_index",2220,False,True)


# In[ ]:




