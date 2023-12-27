#!/usr/bin/env python
# coding: utf-8

# In[1]:


import gzip
import io
import os
import re
import math
import time
import concurrent.futures

import sys


from typing import TextIO, BinaryIO
from typing import List,Iterator

sys.path.append('../')

from pre_processing.TextProcessor import TextProcessor


# In[2]:


"""
    This class is used to avoid to load the entire data collection in memory and process a row at a time.
    In particular it is designed to load just a partial portion of the entire collection, then uncompress it
    and applying the pre-processing tecniques.
    It also gives the possibility to run a test-collection, all in complete transparency of the program who uses it.

"""

class Collection_Reader:
    
    __collection_file_name:str
         
    __escape_first_row_description:bool
    __use_steamming_and_remove_stop_words:bool    
        
    __num_parallel_processes:int
    __max_nr_of_documents_in_memory:int
  
    __text_processor:TextProcessor
    __collection_file: BinaryIO
        
    __documents:List[str]
    __finished:bool
        
    __test_mode:bool
    
    def __init__(self,path_collection_file_name:str,
                 max_nr_of_documents_in_memory:int,
                 num_parallel_processes:int,
                 use_steamming_and_remove_stop_words:bool,
                 escape_first_row_description:bool,
                 collection_test:List[str]=[]):    
        """ Constructor methods for initialization:

            Args:
                path_collection_file_name: the file location of the collection to be read.
                max_nr_of_documents_in_memory: specifies the number of maxium document to be load in main memory. 
                num_parallel_processes: specifies the number of parallel process to be used during execution of pre-processing stage, in order to speed up the elaboration
                use_steamming_and_remove_stop_words: a boolean indicating if using steamming_and_remove_stop_words
                escape_first_row_description: a boolean indicating if the first line of document should be treat differently
                collection_test: (optional) if present uses the collection indicated instead of the one indicated in path_collection_file_name
            
        """
        self.__text_processor = TextProcessor(use_steamming_and_remove_stop_words)
        self.__finished=False
        
        if (collection_test):
            self.__test_mode=True
            self.__num_parallel_processes=1
            
            
            if (escape_first_row_description):
                collection_test[0]="0\t"+self.__text_processor.process_text(re.sub(r".*?0\t", "", collection_test[0]))
                
                
            doc_pre_processed=[]
            for doc in collection_test:
                doc_pre_processed.append(self.__text_processor.process_text(doc))
            
            self.__documents=doc_pre_processed
            
        else:
            self.__test_mode=False
            
            self.__collection_file_name = path_collection_file_name
            self.__max_nr_of_documents_in_memory = max_nr_of_documents_in_memory
            self.__num_parallel_processes=num_parallel_processes
            self.__use_steamming_and_remove_stop_words=use_steamming_and_remove_stop_words

            if (self.__max_nr_of_documents_in_memory<=0):
                raise ValueError("Please enter a nr of documents >=1")
            
            if (self.__num_parallel_processes<=0):
                raise ValueError("Please enter a nr of parallel processes >=1")
            

            self.__text_processor = TextProcessor(use_steamming_and_remove_stop_words)
            self.__collection_file= gzip.open(self.__collection_file_name, 'rt', encoding='utf-8')
            self.__escape_first_row_description=escape_first_row_description

            if (escape_first_row_description):
                line = self.__collection_file.readline()
                result_string = "0\t"+self.__text_processor.process_text(re.sub(r".*?0\t", "", line))
            
                self.__documents=[result_string]
            else:
                self.__documents=[]
                
                
        print ("Collection_Reader Costructor")
        
        print ("Using: ")
        if (collection_test):
            print("Testing Mode : True")
            print("No. of documents in the test collection: "+str(len(collection_test)))
        else:
            print("Testing Mode: False ")
            print("Max Document in memory: "+str(self.__max_nr_of_documents_in_memory))
            print("No. of parallel processes: "+str(self.__num_parallel_processes))
            print("Use Stemming and stop word removal: "+str(self.__use_steamming_and_remove_stop_words))
        
        if (self.__num_parallel_processes>=2):
            print("No. of parallel processes>=2 be sure to executing  this program outside a jupyter notebook.")
            self.__executor=concurrent.futures.ProcessPoolExecutor(max_workers=self.__num_parallel_processes)
            
        else:
            print("No. of parallel processes=1, you can execute it also inside a jupyter notebook.")
        print("\n")
        
            
            
    def __close_collection_file(self)->None:
        self.__collection_file.close()
        self.__finished=True
      
    def __iter__(self)->None:
        return self
    
    def __next__(self):
        """
            This is the operator to call each time you want a new document from the collection.
            This method hide to the external, the logic in which a document is returned.
            If the max_nr_of_documents_in_memory is reached then it reads from collection disk,
            preprocess it, according to the TextProcessor logic module and saves into __documents list. 
        """
        if (self.__test_mode):
            #In test mode, the disk is not present and the collection is entirly present in memory, so just need a pop.
            if (self.__documents):
                return self.__documents.pop(0)
            else:
                raise StopIteration()
        else: 
            #In production, check first if there are documents in memory otherwise call the function to load from disk.
            if (self.__documents):
                return self.__documents.pop(0)
            
            if (not self.__documents and not self.__finished):
                return self.__read_part_of_collection()
            else:
                raise StopIteration()
            
            
    def __read_part_of_collection(self)->str:
        """ 
            This function is responsable for reading to the disk, preprocess the document,save it in local list and
            after returned on demand. This function is the most heavyest part so it is called only when no other document
            are present in memory.
            Pay attention: if this function is called inside a jupyter notebook, check if the number of processes are set to 1,
            if chosen >1 it does not run beacuse of the structure of a notebook.
            When number of processes>1 multiple parallel processes in a pool are handled by an executor in order to save time during
            the creation of the index.
              
        Returns:
            the first text document loaded and preprocessed from disk or None if all the documents on disk are read.
            
        """
        
        nr_doc=0
        max_doc_per_buffer=math.ceil(self.__max_nr_of_documents_in_memory/self.__num_parallel_processes)
        
        #Splitting the buffer of documents for each different process.
        current_buffer_index=0
        array_buffers = [list() for _ in range(self.__num_parallel_processes)]
        
        while(True):
           
            if (nr_doc==self.__max_nr_of_documents_in_memory):
                break
                
            line = self.__collection_file.readline()
            
            #Stop reading from disk contition
            if (line==""):
                self.__close_collection_file()
                break
            
            array_buffers[current_buffer_index].append(line)
            nr_doc+=1 
            
            if (nr_doc%(max_doc_per_buffer)==0):
                current_buffer_index+=1
                
        if (nr_doc!=0):
            
            #If execute NOT inside a jupyter notebook
            if (self.__num_parallel_processes>=2):
                # Submit processing tasks for each line

                #print("Prima submit executor")
                futures = {self.__executor.submit(execute_CPU_BOUND_preprocessing, i,buffer,self.__use_steamming_and_remove_stop_words): i for i,buffer in enumerate(array_buffers) if len(buffer)>0 }
                #print("Dopo submit executor")

                try:
                    # Wait for all tasks to complete
                    concurrent.futures.wait(futures)

                    #Join the results from different processes.
                    return_list=[]
                    for future in futures:
                        result = future.result()
                        return_list.extend(result)

                    self.__documents.clear()
                    self.__documents.extend(return_list)
                    for buffer in array_buffers:
                        buffer.clear()

                    return self.__documents.pop(0)
                except Exception as e:  
                    #print ("CATCH ESTERNO")
                    print(e)
                    
            else:
                #If execute inside a jupyter notebook, costrained to one single process.
                pre_processed_docs=execute_CPU_BOUND_preprocessing(0,array_buffers[0],self.__use_steamming_and_remove_stop_words)
                self.__documents=pre_processed_docs
        
                if (self.__documents):
                    return self.__documents.pop(0)
                
                return None
         
        #end_part_loop = time.time()
        
        #print("Doc_processed: "+str(nr_doc)+" time:"+str(end_part_loop-start_time_loop))
        


# In[3]:


#This is istantiated 1 time only and not for each process.
tp= TextProcessor(True)

def execute_CPU_BOUND_preprocessing(index,buffer,use_steamming_and_remove_stop_words)->List[str]:
    """ This function does simply an CPU bound task that consist in applying preprocessing to a specific document.
        Depending on the parameter passed it can simply execute pre-processing or additional appling steam and stop-word
        removal. Of course the benefit is obtained when it is used with the second option with multiple parallel processes.
    
    Args:
        index: just a number to differentiate in debug the number of process that is doing the job and how much time it takes.
        buffer: a list of string representing each element a different document to process
        use_steamming_and_remove_stop_words: boolean to indicate if using steamming and stop words removal
    
    Returns:
        A list of string represented each document preprocessed
    """
    
    try:

        #print ("START execute_CPU_BOUND_preprocessing "+str(index))
        array_return=[]
        tp.use_stemming_and_stop_words=use_steamming_and_remove_stop_words
        for line in buffer:
            pre_processed=tp.process_text(line)
            if (pre_processed.strip()!=""):
                array_return.append(pre_processed)        
       
    except Exception as e:  
        #print ("entro dentro il catch del execute_CPU_BOUND_preprocessing")
        print(e)

    finally:
        return array_return


# In[4]:


#Lasciare commentato, può tornare utile per vedere una riga specifica della collection,
#ci vorrà un pò ma perlomeno ci s'ha un modo già pronto.

# i=0
# with gzip.open("C:/Users/Davide/IR/collection.tar.gz", 'rt', encoding='utf-8') as gzipped_file:
#     while(True):
#         line = gzipped_file.readline()
#         if (line==""):
#             print("Fine lettura")
#             break
#         if (i==5):
#             print(line)
#             break
#         i+=1

