#!/usr/bin/env python
# coding: utf-8

# In[1]:


import heapq
import bisect
from typing import List, Tuple, BinaryIO
from io import BufferedReader

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


DIR_INVERTED_INDEX="../building_data_structures/INV_INDEX"
PATH_FINAL_DOC_IDS="doc_ids.bin"
PATH_FINAL_FREQ="freq.bin"
PATH_FINAL_BLOCK_DESCRIPTOR="block_descriptors.bin"
DIR_LEXICON="../building_data_structures/LEXICON"
PATH_FINAL_LEXICON="lexicon.bin"

DIR_DOC_INDEX="../building_data_structures/DOC_INDEX"
PATH_COLLECTION_STATISTICS="collection_statistics.bin"


# In[3]:


class Max_Score:
    lexicon: Lexicon 
    collection_statistics: Collection_statistics
    scorer: Scoring
    
    file_DocIds: BinaryIO
    file_Freq: BinaryIO 
    file_blocks: BinaryIO 
    file_lexicon: BinaryIO

    posting_readers_list: List[Tuple[Posting_List_Reader, float]] = []
    top_k_documents: List[Tuple[float, int]] = []
    
    def __init__(self):
        self.lexicon = Lexicon(512)
        self.collection_statistics = Collection_statistics(DIR_DOC_INDEX+"/"+PATH_COLLECTION_STATISTICS)
        self.collection_statistics.read_binary_mode()
        self.scorer = Scoring(self.collection_statistics)
        # ############### VALUTARE SE APRIRE TUTTE LE POSTING UNA SOLA VOLTA NEL COSTRUTTORE E CHIUDERLE A FINE PROGRAMMA PER RISPARMIARE TEMPO
        # self.open_all_posting_lists()
    
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

    def initialize_and_sort_posting_lists(self,tokens: List[str], scoring_function: str) -> None:
        """
        Initializes posting lists for the given tokens, sorted by term upper bound (from smallest to highest).

        Args:
            tokens (List[str]): List of query tokens.
        """
        for token in tokens:
            term_lexicon_row = self.lexicon.get_entry(token)
            
            if term_lexicon_row is not None:
                term_lexicon_row.compute_term_upper_bound()
                
                if scoring_function == "tfidf":
                    term_upper_bound = term_lexicon_row.maxTFIDF
                elif scoring_function == "bm25":
                    term_upper_bound = term_lexicon_row.maxBM25
                else:
                    raise ValueError("Not supported scoring function")

                dft = term_lexicon_row.dft
                reader = Posting_List_Reader(term_lexicon_row, False, self.file_DocIds, self.file_Freq, self.file_blocks)
                self.posting_readers.append({"reader": reader, "term_upper_bound": term_upper_bound, "dft": dft})

        self.posting_readers.sort(key=lambda x: x.get("term_upper_bound", float('inf')))
        
        for reader in self.posting_readers:
            next(reader["reader"])

    
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
            
    def min_doc(self, index_first_essential_posting_lists:int) -> Tuple[int, int, int]:
        """
        Retrieves the minimum document ID and its frequency among the current documents in all essential posting lists.

        Returns:
            Tuple[int, int]: Tuple containing the minimum document ID and its frequency.
        """
        end, _ = self.all_lists_exhausted()

        # Check if all readers have reached the end of the list
        if end == True:
            return -1,-1, -1

        current_docs = [{"reader": self.posting_readers[i]["reader"].get_current_posting(), "dft": self.posting_readers[i]["dft"]} for i in range(index_first_essential_posting_lists, len(self.posting_readers))]

        # Fetch only not null documents
        valid_docs = [doc for doc in current_docs if doc["reader"] is not None]

        if not valid_docs:
            return -1, -1

        # Retrieve the documents with min doc_id
        min_doc = min(valid_docs, key=lambda x: x["reader"].doc_id)

        # Return the minimum doc_id and its frequency
        return min_doc["reader"].doc_id, min_doc["reader"].frequency, min_doc["dft"]
        
    def process_essential_lists_daat(self, index_first_essential_posting_lists:int, doc_to_process: int, scoring_function:str, dft: int) -> float:
        """
        Process the essential posting lists to calculate the partial score for a document.
    
        Arguments:
            index_first_essential_posting_lists (int): Index of the first essential posting list.
            doc_to_process (int): Document ID to process.
            scoring_function (str): Scoring function to use.
    
        Returns:
            float: Partial score for the document.
        """
        partial_score = 0

        for i in range(index_first_essential_posting_lists, len(self.posting_readers)):                
            if self.posting_readers[i]["reader"].get_current_posting() is not None and self.posting_readers[i]["reader"].get_current_posting().doc_id == doc_to_process:
                partial_score = partial_score + self.scorer.choose_scoring_function(scoring_function, doc_to_process, self.posting_readers[i]["reader"].get_current_posting().frequency, dft)
                try:
                    next(self.posting_readers[i]["reader"])
                except StopIteration:
                    continue

        return partial_score
    
    def get_index_first_essential_posting_list(self, current_threshold: float) -> int:
        """
        Find the index of the first essential posting list based on the current threshold.
    
        Arguments:
            current_threshold (float): Current threshold value.
    
        Returns:
            int: Index of the first essential posting list, or -1 if not found.
        """
        summed_scores = 0

        for index, reader in enumerate(self.posting_readers):
            summed_scores = summed_scores + reader["term_upper_bound"]

            if summed_scores > current_threshold:
                return index

        return -1

    """
    get the scores for the input document, given by the non-essential posting list in the array list of the sorted lists
    """
    def process_non_essential_lists_with_skipping(self, first_essential_pl_index: int, doc_to_process: int, scoring_function: str, dft: int) -> float:
        """
        Process non-essential posting lists, skipping documents up to doc_to_process, and calculate the non-essential score.
    
        Arguments:
            first_essential_pl_index (int): Index of the first essential posting list.
            doc_to_process (int): Document ID to process.
            scoring_function (str): Scoring function to use.
    
        Returns:
            float: Non-essential score for the document.
        """
        nonEssentialScore = 0

        for i in range(0, first_essential_pl_index):
            if self.posting_readers[i]["reader"] is not None and self.posting_readers[i]["reader"].get_current_posting().doc_id == doc_to_process:
                nonEssentialScore = nonEssentialScore + self.scorer.choose_scoring_function(scoring_function, doc_to_process, self.posting_readers[i]["reader"].get_current_posting().frequency, dft)
                
                try:
                    next(self.posting_readers[i]["reader"])
                except StopIteration:
                    continue
                    
                continue
    
            posting = self.posting_readers[i]["reader"].nextGeq(doc_to_process)
            if posting != -1 and posting == doc_to_process:
               nonEssentialScore = nonEssentialScore + self.scorer.choose_scoring_function(scoring_function, doc_to_process, posting.frequency, dft)
               try:
                    next(self.posting_readers[i]["reader"])
               except StopIteration:
                    continue

        return nonEssentialScore

    def compute_non_essential_tub(self, first_essential_pl_index: int) -> float:
        """
        Compute the sum of term upper bounds for all non-essential posting lists.
    
        Arguments:
            first_essential_pl_index (int): Index of the first essential posting list.
    
        Returns:
            float: Sum of term upper bounds for non-essential posting lists.
        """
        # Sum the term upper bounds for all non-essential posting lists and save them in non_essential_tub
        non_essential_tub = 0
        for i in range(first_essential_pl_index):
            if self.posting_readers[i] is not None:
                non_essential_tub += self.posting_readers[i]["term_upper_bound"]

        return non_essential_tub
        
    def update_heap(self, k: int, document_upper_bound: float, doc_to_process: int, curr_threshold: float) -> float:
        """
        Update the MinHeap with the current document's information.
    
        Arguments:
            k (int): Size of the MinHeap.
            document_upper_bound (float): Upper bound score for the document.
            doc_to_process (int): Document ID to process.
            curr_threshold (float): Current threshold value.
    
        Returns:
            float: Updated threshold value.
        """
        # Check if the MinHeap is full
        heapq.heappush(self.top_k_documents, (document_upper_bound, doc_to_process)) 
    
        # Keep the priority queue of size k.
        if len(self.top_k_documents) > k:
            _, new_threshold_candidate = heapq.heappop(self.top_k_documents)

            # Restituisci il nuovo threshold solo se è inferiore al threshold corrente
            return min(new_threshold_candidate, curr_threshold)
        else:
            return curr_threshold        
    
    def scoreQuery(self, k: int, scoring_function: str, tokens: List[str], isConjunctive: bool) -> List[Tuple[float, int]]:
        """
        Score the given query using a specified scoring function and return the top-k results.
    
        Args:
            k (int): The number of top results to retrieve.
            scoring_function (str): The scoring function to use (e.g., "tfidf", "bm25").
            tokens (List[str]): List of query tokens.
            isConjunctive (bool): Flag indicating whether to use conjunctive mode.
    
        Returns:
            List[Tuple[float, int]]: List of tuples containing the score and document ID for the top-k results.
        """
        self.open_all_posting_lists()
        self.reset_lists()
        self.initialize_and_sort_posting_lists(tokens, scoring_function)

        # Initialization of current threshold to enter the MinHeap of the results
        curr_threshold = -1
        curr_threshold_has_been_updated = True
        first_essential_pl_index = 0

        while True:
            try:
                partial_score, document_upper_bound = 0, 0

                # Variable to store the sum of term upper bounds of non-essential posting lists
                non_essential_tub = 0
                
                # Check if we must update the division in essential and non-essential posting lists
                if curr_threshold_has_been_updated:
                    # Divide posting lists to be scored into essential and non-essential posting lists
                    first_essential_pl_index = self.get_index_first_essential_posting_list(curr_threshold)

                    if first_essential_pl_index == -1:
                        break

                # Search for the minimum docid to be scored among essential posting lists
                doc_to_process, _ , dft = self.min_doc(first_essential_pl_index)
    
                # Check if there is no docid to be processed
                if doc_to_process == -1:
                    break

                # if conjunctive_mode:
                #     doc_to_process = next_geq(doc_to_process)
                #     if doc_to_process == -1:
                #        break

                non_essential_tub = self.compute_non_essential_tub(first_essential_pl_index)
                partial_score = self.process_essential_lists_daat(first_essential_pl_index, doc_to_process, scoring_function, dft)
                document_upper_bound = non_essential_tub + partial_score

                # Check if non-essential posting lists must be processed or not
                if document_upper_bound > curr_threshold:
                    # Process non-essential posting list skipping all documents up to doc_to_process
                    non_essential_scores = self.process_non_essential_lists_with_skipping(first_essential_pl_index, doc_to_process, scoring_function, dft)
                    
                    # Update document upper bound
                    # document_upper_bound = document_upper_bound - non_essential_tub + non_essential_scores
                    document_upper_bound = partial_score + non_essential_scores
        
                    # Check if the document can enter the MinHeap
                    if document_upper_bound > curr_threshold:
                        curr_threshold = self.update_heap(k, document_upper_bound, doc_to_process, curr_threshold)
        
                # Check if the current threshold has been updated or not
                curr_threshold_has_been_updated = (curr_threshold == document_upper_bound)
            except StopIteration:             
                end, _ = self.all_lists_exhausted()
            
                if end == True:
                    curr_threshold = self.update_heap(k, document_upper_bound, doc_to_process, curr_threshold)
                    break  
                else:
                    continue 
                
            except Exception as e:
                print(f"Error during execution: {e}")
                break
    
        self.close_all_posting_lists()
        self.scorer.close_files()
        # self.top_k_documents.sort(key=lambda x: x[0], reverse= True)
        
        return self.top_k_documents

##############################################################################################
    def nextGEQ(self, docid_to_process: int) -> int:
        """
        Find the next document ID greater than or equal to the specified docid_to_process.
    
        Args:
            docid_to_process (int): Document ID to process.
    
        Returns:
            int: The next document ID greater than or equal to docid_to_process.
                 Returns -1 if no such document is found.
        """
        next_geq = docid_to_process # Initialize the candidate next document ID

        for i in range(len(self.posting_readers)): # Iterate over each posting list
            curr_posting_list = self.posting_readers[i]["reader"] # Get the i-th posting list

            # check if there are postings to iterate in the i-th posting list
            if curr_posting_list is not None:
                pointed_posting = curr_posting_list.get_current_posting() # Get the current pointed posting in the i-th posting list

                if pointed_posting is None: # If there are no more postings in the current list
                    return -1

                # If the current pointed posting has a doc_id less than docid_to_process,
                # move to the next posting with a doc_id greater than or equal to docid_to_process
                if pointed_posting.doc_id < next_geq:
                    # If there is no doc_id greater than or equal to docid_to_process in the current posting list, return -1
                    pointed_posting = curr_posting_list.nextGEQ(next_geq)

                    # check if in the current posting list there is no docid >= docidToProcess to be processed
                    if pointed_posting is None:
                        return -1

                # If the current posting list has a doc_id greater than docid_to_process,
                # update next_geq to the new candidate next docid and reset the loop index to check all posting lists again
                if pointed_posting.doc_id > next_geq:
                    next_geq = pointed_posting.doc_id
                    i = -1

        return next_geq


# In[4]:


# max_score = Max_Score()

# import time
# start_time = time.time()

# print(max_score.scoreQuery(10, "bm25", ["I", "am" ,"very", "hungry", "ciao"], False))
# print("ci ha messo: ", time.time() - start_time , " secondi")


# In[5]:


# list = []

# reader = "a"
# term_upper_bound = 15
# index_to_insert = bisect.bisect_left([entry[1] for entry in list], term_upper_bound)
# list.insert(index_to_insert, (reader, term_upper_bound))
# print(list)

# reader = "b"
# term_upper_bound = 20
# index_to_insert = bisect.bisect_left([entry[1] for entry in list], term_upper_bound)
# list.insert(index_to_insert, (reader, term_upper_bound))
# print(list)

# reader = "c"
# term_upper_bound = 5
# index_to_insert = bisect.bisect_left([entry[1] for entry in list], term_upper_bound)
# list.insert(index_to_insert, (reader, term_upper_bound))
# print(list)

# reader = "d"
# term_upper_bound = 2
# index_to_insert = bisect.bisect_left([entry[1] for entry in list], term_upper_bound)
# list.insert(index_to_insert, (reader, term_upper_bound))
# print(list)

# reader = "e"
# term_upper_bound = 17
# index_to_insert = bisect.bisect_left([entry[1] for entry in list], term_upper_bound)
# list.insert(index_to_insert, (reader, term_upper_bound))
# print(list)

# reader = "f"
# term_upper_bound = 12
# index_to_insert = bisect.bisect_left([entry[1] for entry in list], term_upper_bound)
# list.insert(index_to_insert, (reader, term_upper_bound))
# print(list)


# In[6]:


# max_sc = Max_Score()
# max_sc.open_all_posting_lists()
# max_sc.reset_lists()
# max_sc.initialize_and_sort_posting_lists(["cat","dog"], "tfidf")

# # Divide posting lists to be scored into essential and non-essential posting lists
# first_essential_pl_index = max_sc.get_index_first_essential_posting_list(-1)

# print("first_essential_pl_index: ", first_essential_pl_index)

# doc_to_process, freq, dft = max_sc.min_doc(first_essential_pl_index)

# print("doc_to_process: ", doc_to_process)
# print("freq: ", freq)
# print("dft: ", dft)

