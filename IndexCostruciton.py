#!/usr/bin/env python
# coding: utf-8

# In[11]:


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


# In[12]:


tot_doc=[
            "The pen is on the table",
            "The day is very sunny",
            "Goodmoring new article",
            "A cat is faster then a dog",
            "How are you",
            "A boy is a man with low age",
            "Lake Ontario is one of the biggest lake in the world",
            "English is worst than Italian",
            "Spiderman is the best superhero in Marvel universe",
            "Last night I saw a Netflix series",
            "A penny for your thoughts",
            "Actions speak louder than words",
            "All that glitters is not gold",
            "Beauty is in the eye of the beholder",
            "Birds of a feather flock together",
            "Cleanliness is next to godliness",
            "Don't count your chickens before they hatch",
            "Every people cloud has a silver lining people",
            "Fool me once shame on you fool me twice shame on me",
            "Honesty is the best policy.",
            "If the shoe fits, wear it",
            "It's a piece of cake",
            "Jump on the bandwagon",
            "Keep your chin up",
            "Let the cat out of the bag",
            "Make a long story short",
            "Necessity is the mother of invention",
            "Once in a blue moon",
            "Practice makes perfect",
            "Read between the lines",
            "The early bird catches people the worm",
            "The pen is mightier than the sword",
            "There's no smoke without fire",
            "To each his own",
            "Two heads are better than one",
            "You can't have your cake and eat it too",
            "A watched pot never boils",
            "Beggars can't be choosers",
            "Better late than never",
            "Calm before the storm",
            "Curiosity killed the cat",
            "Every dog has its day",
            "Great minds think alike",
            "Hope for the best prepare for the worst",
            "Ignorance is bliss.",
            "It's the last straw that breaks the camel's back",
            "Laugh and the world laughs with you weep and you weep alone",
            "Money can't buy happiness",
            "No news is good news",
            "Out of sight out of mind",
            "People who live in glass houses shouldn't throw stones",
            "Rome wasn't built in a day",
            "Silence is golden",
            "The apple doesn't fall far from the tree",
            "The more, the merrier",
            "There's no place like home",
            "Two wrongs don't make a right",
            "When in Rome do as the Romans do",
            "You reap what you sow",
            "People people people"]


# In[26]:


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
        
#NON USATA PER ORA
@dataclass
class Posting_List_Location:
    pos: int
    payload: Any = None

        
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
    
    #def write_to_file(self, filename_index: str) -> None:
    #    """Saves the index to a textfile."""
    #    with open(filename_index, "w") as f:
    #        for term, postings in self._index.items():
    #            f.write(term)
    #            for posting in postings:
    #                f.write(f" {posting.doc_id}")
    #                if posting.payload:
    #                    f.write(f":{str(posting.payload)}")
    #            f.write("\n")
    
    
    def write_to_block(self,filename_index: str) -> None:
        
        sorted_lexicon=sorted(ind._index.items())
        with open(filename_index, "w") as f:
            for term,postings in sorted_lexicon:
                f.write(term)
                if (term=='people'):
                    print (term,postings)
                for posting in postings:
                    f.write(f" {posting.doc_id}")
                    
                    if posting.payload:
                        f.write(f":{str(posting.payload)}")
                f.write("\n")
    
    def is_empty(self)->bool:
        return len(self.get_terms())==0
    
    def get_terms(self) -> List[str]:
        """Returns all unique terms in the index."""
        return self._index.keys() 
    
    def clearStructure(self):
        self._index.clear()
    
    def getStructure(self):
        return self._index
                
        


# In[27]:


#Altre funzioni di utilità non ancora considerate.

def count_lexicon_in_list_of_strings(string_list):
    return len(set([term for doc in tot_doc for term in doc.lower().split()]))

def read_integer_list_from_file(file_path):
    integer_list = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                integer_list.append(int(line.strip()))
        return integer_list
    except IOError as e:
        print(f"Error reading from {file_path}: {e}")
        return None

def write_integer_list_to_file(file_path, integer_list):
    try:
        with open(file_path, 'w') as file:
            for number in integer_list:
                file.write(str(number) + '\n')
        print(f"List of integers written to {file_path}")
    except IOError as e:
        print(f"Error writing to {file_path}: {e}")


# In[28]:


def appendListOfPostingFromString(current_postings:list, stringListPostingDescription:str):
    
    current_docIds=[]
    #print ("vado ad elaborare ")
    #print(stringListPostingDescription)
    if (len(current_postings)>0):
        current_docIds=[curr_posting.doc_id for curr_posting in current_postings]
    
    for postingStr in stringListPostingDescription: #postingStr è un singolo posting docId:freq
        posting=Posting(postingStr)
        #print ("POSTING LETTO!")
        #print (posting)
        if (posting.doc_id in current_docIds): #Se già presente una posting con docId, ci sommo la termFreq
            current_postings[current_docIds.index(posting.doc_id)]+=posting.payload 
        else:
            current_postings.append(Posting.from_string(postingStr))
                    
def appendTerm_Posting_ToFile(fileName:str,term:str,mergePostings:list):
    with open(fileName, "a") as f:
        f.write(term)
        print (term,mergePostings)
        for posting in mergePostings:
            f.write(f" {posting.doc_id}")
            if posting.payload:
                f.write(f":{str(posting.payload)}")
        f.write("\n")  
        
        
def check_all_block_are_read(lines:list)->bool:
    print ("Controllo che i file siano stati letti tutti..")
    for line in lines:
        print ("Linea :"+line)
        if line:
            return False
    return True


# In[29]:


#TEST

ind = InvertedIndex()

for doc in tot_doc:
    doc_id=tot_doc.index(doc)
    tc = Counter(doc.lower().split())  # dict with term counts
    for term, freq in tc.items():
        ind.add_posting(term, doc_id, freq)


# In[30]:


ind.get_postings("people")


# In[31]:


#Inizializzazione strutture e dimensioni

ind = InvertedIndex()
BLOCK_SIZE=2200
nr_block=0

DIR_FOLDER="TEMP"
OUTPUT_FILE="complete_inverted_index.txt"

if os.path.exists(DIR_FOLDER):
    shutil.rmtree(DIR_FOLDER)

os.makedirs(DIR_FOLDER)


#Sorta di map
#Mi vado a prendere termine per termine in ogni documento e finche c'è spazio nel blocco
# appendo docId e termFreq.

#Quando non c'è più spazio, vado a salvare sul disco e ripulisco la struttura.

for doc in tot_doc:
    doc_id=tot_doc.index(doc)
    tc = Counter(doc.lower().split())  # dict with term counts
    for term, freq in tc.items():
        #Free memory available
        if (sys.getsizeof(ind.getStructure()) > BLOCK_SIZE):
            print ("STOPPED",doc_id,term)
            #print (ind._index)
            #print (sys.getsizeof(ind.getStructure()))
            ind.write_to_block(DIR_FOLDER+"/lexicon_"+str(nr_block)+".txt")
            ind.clearStructure()
            #print (sys.getsizeof(ind.getStructure()))
            nr_block=nr_block+1 
        ind.add_posting(term, doc_id, freq)
        
#Infine mi salvo anche l'ultimo blocco.        
if (not ind.is_empty()):   
    ind.write_to_block(DIR_FOLDER+"/lexicon_"+str(nr_block)+".txt")


# In[32]:


#Sorta di reduce --> ri unisco tutti i blocchi risultati

file_paths = [DIR_FOLDER+"/"+f for f in os.listdir(DIR_FOLDER)]
#Apro tutti i blocchi in parallelo
input_files = [open(file, 'r') for file in file_paths]
#Leggo la prima linea di tutti i blocchi
lines=[file.readline().strip() for file in input_files]


if os.path.exists(DIR_FOLDER+"/"+OUTPUT_FILE):
    os.remove(DIR_FOLDER+"/"+OUTPUT_FILE)

while (not check_all_block_are_read(lines)):
    
    terms=[line.split()[0] if line else chr(1114111) for line in lines] #Lista di stringhe
    postings=[" ".join(line.split()[1:]) for line in lines] #Lista di stringhe

    #Stabilisco quale è il prossimo termine lessicograficamente più vicino da usare
    min_term=min(terms)
    #print("Nuovo termine minimo: "+min_term)
   
    #Unisco le varie posting degli stessi termini,le ordino e salvo su file.
    mergePostings=[]
    for i in range (0,len(postings)):
        if (min_term==terms[i]):  
            appendListOfPostingFromString(mergePostings,postings[i].split())

    mergePostings=sorted(mergePostings, key=operator.attrgetter('doc_id'))       

    appendTerm_Posting_ToFile(DIR_FOLDER+"/"+OUTPUT_FILE,min_term,mergePostings)

    #Avanzo nella scansione di 1 riga solo dei termini che ho considerato prima.

    for i in range (0,len(terms)):
        if (min_term==terms[i]):   
            lines[i]=input_files[i].readline().strip()
            #print (i,lines[i])

for file in input_files:
    file.close()   


# In[10]:


for file in input_files:
    file.close()


# In[29]:




