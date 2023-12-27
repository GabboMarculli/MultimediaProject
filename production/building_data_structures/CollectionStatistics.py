#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pickle


# In[5]:


class Collection_statistics:    
    def __init__(self,path_file:str, num_documents: int=0, num_distinct_terms: int=0, sum_document_lengths: int=0) -> None:
        """
        Initializes an instance of Collection_statistics.

        Args:
            path_file (string): the location where the info are stored.
            num_documents (int): Number of documents.
            num_distinct_terms (int): Number of distinct terms.
            sum_document_lengths (int): Sum of document lengths.
        """
        if not isinstance(num_documents, int) or not isinstance(num_distinct_terms, int) or not isinstance(sum_document_lengths, int):
            raise ValueError("Values must be integer.")
            
        if num_documents < 0 or num_distinct_terms < 0 or sum_document_lengths < 0:
            raise ValueError("Values must be positive.")
        
        self.num_documents=num_documents
        self.num_distinct_terms=num_distinct_terms
        self.sum_document_lengths=sum_document_lengths
        
        self.keys = ['Document Index Size','Vocabulary Size','Sum Document length']
        self.path_file=path_file

    def save_statistics(self,file_path:str) -> None:
        values = [self.num_documents,self.num_distinct_terms, self.sum_document_lengths]
        
        with open(file_path, "w") as f:
            for i, index in enumerate(self.keys):
                f.write(f"{self.keys[i]}: {values[i]}\n")

    def write_binary_mode(self) -> None:
        values = [self.num_documents, self.num_distinct_terms, self.sum_document_lengths]

        data = {"keys": self.keys, "values": values}
        serialized_data = pickle.dumps(data)
    
        with open(self.path_file, "wb") as f:
            f.write(serialized_data)

    def read_statistics(self) -> None:
        try:
            with open(self.path_file, "r") as f:
                lines = f.readlines()

            for line in lines:
                key, value = line.strip().split(": ")
                key = key.strip()
                value = int(value.strip())
                
                if key == 'Document Index Size':
                    self.num_documents = value
                elif key =='Vocabulary Size':
                    self.num_distinct_terms = value
                elif key =='Sum Document length':
                    self.sum_document_lengths == value
                    
        except FileNotFoundError:
            print(f"File {self.path_file} not found.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
    
    def read_binary_mode(self) -> None:
        with open(self.path_file, "rb") as f:
            serialized_data = f.read()

        data = pickle.loads(serialized_data)
        keys = data["keys"]
        values = data["values"]

        self.num_documents=values[0]
        self.num_distinct_terms=values[1]
        self.sum_document_lengths=values[2]
    
    def get_average_Document_Length(self) -> float:
        """
            Returns the average document length based on the document index (doc_index).
        """   
        return self.sum_document_lengths / self.num_documents   

