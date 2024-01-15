#!/usr/bin/env python
# coding: utf-8

# In[1]:


import heapq
from typing import List, Tuple
from io import BufferedReader
import os
import time

#import import_ipynb
import sys
sys.path.append('../')  # Go up two folders to the project root

from structures.DocumentIndex import DocumentIndex
from structures.Lexicon import Lexicon
from structures.PostingListHandler import Posting_List_Reader
from query_processing.Scoring import Scoring
from building_data_structures.CollectionStatistics import Collection_statistics
from structures.InvertedIndex import Posting


# In[2]:


DIR_INVERTED_INDEX="../INV_INDEX"
PATH_FINAL_DOC_IDS="doc_ids.bin"
PATH_FINAL_FREQ="freq.bin"
PATH_FINAL_BLOCK_DESCRIPTOR="block_descriptors.bin"
DIR_LEXICON="../LEXICON"
PATH_FINAL_LEXICON="lexicon.bin"

DIR_DOC_INDEX="../DOC_INDEX"
PATH_COLLECTION_STATISTICS="collection_statistics.bin"


# In[3]:


class DAAT():
    file_DocIds: BufferedReader
    file_Freq: BufferedReader
    file_blocks: BufferedReader
    posting_readers: List[Tuple[Posting_List_Reader, int]] = []
    top_k_documents: List[Tuple[float, int]] = []
    
    def __init__(self):
        self.lexicon = Lexicon(512,DIR_LEXICON+"/"+PATH_FINAL_LEXICON,DIR_DOC_INDEX+"/"+PATH_COLLECTION_STATISTICS)
        print("PASSO DI QUI")
        self.collection_statistics = Collection_statistics(DIR_DOC_INDEX+"/"+PATH_COLLECTION_STATISTICS)
        self.collection_statistics.read_binary_mode()
        self.scorer = Scoring(self.collection_statistics)
    
    def open_all_posting_lists(self) -> None: 
        self.file_DocIds = open(DIR_INVERTED_INDEX+"/"+PATH_FINAL_DOC_IDS, 'rb') 
        self.file_Freq = open(DIR_INVERTED_INDEX+"/"+PATH_FINAL_FREQ, 'rb') 
        self.file_blocks = open(DIR_INVERTED_INDEX+"/"+PATH_FINAL_BLOCK_DESCRIPTOR, 'rb')
        self.file_lexicon = open(DIR_LEXICON+"/"+PATH_FINAL_LEXICON, 'rb') 
        
        self.scorer.open_files()

    def reset_lists(self) -> None:
        # This list will contain pointer to the posting lists of all terms 
        self.posting_readers = []
        # This list will contain the k most relevant document
        self.top_k_documents = []

    def close_all_posting_lists(self):
        for file in [self.file_DocIds, self.file_Freq, self.file_blocks, self.file_lexicon]:
            file.close()      

    def scoreQuery(self, k: int, choice_function: str, tokens: List[str], isConjunctive: bool) -> List[Tuple[float, int]]:
        """
        Scores a query and returns the top-k documents.

        Args:
            k (int): The number of top documents to retrieve.
            choice_function (str): The scoring function to use.
            tokens (List[str]): List of query tokens.
            isConjunctive (bool): Whether the query is conjunctive.

        Returns:
            List[Tuple[float, int]]: List of top-k documents with their scores.
        """        
        tempo_inizio=time.time()
        self.open_all_posting_lists()
        self.reset_lists()
        tempo_fine=time.time()
        print("Tempo configuraazioni:"+str(tempo_fine-tempo_inizio))
        
        tempo_inizio=time.time()
        self.initialize_posting_lists(tokens)
        tempo_fine=time.time()
        
        print("Tempo ricerca binaria:"+str(tempo_fine-tempo_inizio))
        old_doc_id = -1 # used for the last posting list
        counter = 0
        tot_time=0
        tot_min=0
        tot_time_heap=0
        tempo_inizio_loop=time.time()
        while True:
            try:
                # Retrieve the minimum doc_id, the next to process
                tempo_inizio_min=time.time()
                docToProcess, term_freq, dft = self.min_doc()
                tempo_fine_min=time.time()
                tot_min+=tempo_fine_min-tempo_inizio_min
                #print("MIN_DOC:"+str(docToProcess))
                # Check if there are no other doc to process
                if docToProcess == -1:
                    break
                counter+=1
                # If i have read a new doc_id
                if docToProcess != old_doc_id:
                    term_freq = 0 # reset term_freq
                    old_doc_id = docToProcess # update old doc_id

                if isConjunctive:
                    current_docs = [reader["reader"] for reader in self.posting_readers if reader["reader"].get_current_posting() is not None]

                    # Check if the document is present in all posting lists
                    if any(post.get_current_posting().doc_id != docToProcess for post in current_docs):
                        for reader in current_docs: 
                            if reader.get_current_posting().doc_id == docToProcess: # next if doc_id equal to min_doc_id
                                next(reader)
                        continue
                tempo_inizio=time.time()
                for reader in self.posting_readers:
                    if reader["reader"].get_current_posting() is not None and reader["reader"].get_current_posting().doc_id == docToProcess:
                        term_freq += reader["reader"].get_current_posting().frequency
                        next(reader["reader"])
                tempo_fine=time.time()
                tot_time+=(tempo_fine-tempo_inizio)
                
                tempo_inizio_heap=time.time()
                self.update_heap(choice_function, docToProcess, term_freq, k, dft)
                tempo_fine_heap=time.time()
                tot_time_heap+=(tempo_fine_heap-tempo_inizio_heap)
                
            except StopIteration:
                    end, _ = self.all_lists_exhausted()
                
                    if end == True:
                        self.update_heap(choice_function, docToProcess, term_freq, k, dft)
                        break  
                    else:
                        continue  
            except Exception as e:
                print(f"Error during execution: {e}")
                break
        tempo_fine_loop=time.time()   
        
        self.close_all_posting_lists()
        self.scorer.close_files()
        print("TOT_READING:"+str(tot_time))
        print("counter:"+str(counter))
        print("TOT_MIN:"+str(tot_min))
        print("TOT_HEAP:"+str(tot_time_heap))
        print("TOT_LOOP:"+str(tempo_fine_loop-tempo_inizio_loop))
        return self.top_k_documents

    def initialize_posting_lists(self,tokens: List[str]) -> None:
        """
        Initializes posting lists for the given tokens.

        Args:
            tokens (List[str]): List of query tokens.
        """
        for token in tokens:
            term_lexicon_row = self.lexicon.get_entry(token)
        
            if term_lexicon_row is not None:
                dft = term_lexicon_row.dft
                reader = Posting_List_Reader(term_lexicon_row, False, self.file_DocIds, self.file_Freq,self.file_blocks)
                
                # passare anche  term_lexicon_row.docidOffset, term_lexicon_row.frequencyOffset? 
                self.posting_readers.append({"reader": reader, "dft": dft})
                
        for reader in self.posting_readers:
            try:
                next(reader["reader"])
            except StopIteration:
                continue

    def update_heap(self,choice_function: str, docToProcess: int, term_freq: int, k: int, dft:int) -> None:
        """
        Updates the priority queue (heap) with the latest document score.

        Args:
            choice_function (str): The scoring function to use.
            docToProcess (int): Document ID to process.
            term_freq (int): Term frequency in the document.
            k (int): The number of top documents to retrieve.
        """
        doc_score = self.scorer.choose_scoring_function(choice_function, docToProcess, term_freq, dft)
        
        # Add the element to the priority queue
        heapq.heappush(self.top_k_documents, (doc_score, docToProcess)) 
    
        # Keep the priority queue of size k.
        if len(self.top_k_documents) > k:
            heapq.heappop(self.top_k_documents) 

    def all_lists_exhausted(self) -> Tuple[bool, List[Posting]]:
        """
        Checks if all posting lists are exhausted.

        Returns:
            Tuple[bool, List[[Posting]]: Tuple containing a boolean indicating whether all lists are exhausted
            and a list of the current documents in each posting list.
        """
        # Read the next document from each posting list
        current_docs = [{"reader": reader["reader"].get_current_posting(), "dft": reader["dft"]} for reader in self.posting_readers]
        
        # Check if all readers have reached the end of the list
        return all(doc["reader"] is None for doc in current_docs), current_docs

    def min_doc(self) -> Tuple[int, int]:
        """
        Retrieves the minimum document ID and its frequency among the current documents in all posting lists.

        Returns:
            Tuple[int, int]: Tuple containing the minimum document ID and its frequency.
        """
        
        end, current_docs = self.all_lists_exhausted()
        
        if end == True:
            return -1, -1, -1

        # Fetch only not null documents                      
        valid_docs = [doc for doc in current_docs if doc["reader"] is not None]

        # Retrieve the documents with min doc_id
        min_doc = min(valid_docs, key=lambda x: x["reader"].doc_id)

        # Return the minimum doc_id and its frequency
        return min_doc["reader"].doc_id, min_doc["reader"].frequency, min_doc["dft"]


# In[4]:


# daat = DAAT()
# # my_list = ["dogs", "are","beautiful"]
# my_list = ["comparisonsof", "countrythe","gwine"]
# import time

# start_time = time.time()
# print(daat.scoreQuery(5, "bm25", ["gwine"] , False))
# print("ci ha messo: ", time.time() - start_time , " secondi")

# daat.open_all_posting_lists()
# daat.reset_lists()
# daat.initialize_posting_lists(my_list)

# term_lexicon_row = daat.lexicon.get_entry("comparisonsof")
# reader = Posting_List_Reader(term_lexicon_row, False, daat.file_DocIds, daat.file_Freq, daat.file_blocks)
# daat.posting_readers.append({"reader": reader, "dft": term_lexicon_row.dft})
# print(term_lexicon_row.dft)

# while True:
#     next(reader)
#     print(reader.get_current_posting())
#     print(reader.lexicon_elem.term)

# term_lexicon_row = daat.lexicon.get_entry("countrythe")
# reader = Posting_List_Reader(term_lexicon_row, False, daat.file_DocIds, daat.file_Freq, daat.file_blocks)
# next(reader)
# daat.posting_readers.append({"reader": reader, "dft": term_lexicon_row.dft})
# print(reader.lexicon_elem.term)
# print(term_lexicon_row.dft)
# print(reader.get_current_posting())

# term_lexicon_row = daat.lexicon.get_entry("gwine")
# reader = Posting_List_Reader(term_lexicon_row, False, daat.file_DocIds, daat.file_Freq, daat.file_blocks)
# next(reader)
# daat.posting_readers.append({"reader": reader, "dft": term_lexicon_row.dft})
# print(reader.lexicon_elem.term)
# print(term_lexicon_row.dft)
# print(reader.get_current_posting())

# file_path = "../building_data_structures/INV_INDEX/inverted_index.txt"
# with open(file_path, 'r', encoding='utf-8') as file:
#     for line_number, line in enumerate(file, start=1):
#         # 7098672:1 7921810:1 8185306:1
#         if "gwine" in line:
#             print(f"Trovata la parola colega alla riga {line_number}:\n{line}")
#         # 808155:1 808156:1
#         if "comparisonsof" in line:
#             print(f"Trovata la parola comparisonsof alla riga {line_number}:\n{line}")
#         # 472327:1 472334:1 908563:1 1791331:1
#         if "countrythe" in line:
#             print(f"Trovata la parola countrythe alla riga {line_number}:\n{line}")
#             break


# In[5]:


####################################################
# VALUTARE SE UNA CLASSE SIMILE RENDEREBBE PIU' LENTA/VELOCE L'ESECUZIONE
# Al posto di avere la lista top_k_documents e un parametro k 
####################################################

# class MinHeap:
#     def __init__(self, k: int):
#         self.heap = []
#         self.k = k

#     def push(self, item: Tuple[float, int]) -> None:
#         heapq.heappush(self.heap, item)
#         if len(self.heap) > self.k:
#             heapq.heappop(self.heap)


# In[6]:


# se facessi cosi???

# from queue import PriorityQueue

# class YourClass:
#     def __init__(self):
#         self.top_k_documents = PriorityQueue()

#     def update_heap(self, choice_function: str, docToProcess: int, term_freq: int, k: int) -> None:
#         doc_score = self.scorer.choose_scoring_function(choice_function, docToProcess, term_freq)
#         # Aggiungi l'elemento alla coda con priorità
#         self.top_k_documents.put((doc_score, docToProcess))

#         # Mantieni la coda con priorità di dimensione k
#         if self.top_k_documents.qsize() > k:
#             self.top_k_documents.get()


# In[9]:




