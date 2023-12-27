#!/usr/bin/env python
# coding: utf-8

# In[4]:


import psutil
import difflib
import gzip
from io import BytesIO


# In[1]:


def get_available_memory()-> int:
    """
        Function to compute the available memory at runtime.
    Return
        The available memory in bytes 
    """
    # Get available memory in bytes
    available_memory = psutil.virtual_memory().available
    
    # Convert bytes to a more human-readable format
    available_memory_str = psutil.virtual_memory().available / (1024**3)  
    
    print(f"Available memory: {available_memory} bytes")
    print(f"Available memory: {available_memory_str:.2f} GB")
    
    return available_memory


def get_memory_available()->int:
    return psutil.virtual_memory().available

def get_memory_usage()->int:
    process = psutil.Process()
    return process.memory_info().rss



def get_memory_in_GB(num_bytes:int)->str:
    return str(round(num_bytes/(1024**3),2))+" GB"


# In[ ]:


def print_diff(string1:str, string2:str):
    """
        Given two strings outputs the difference between them in a pretty format.
    """
    d = difflib.Differ()
    diff = d.compare(string1.splitlines(), string2.splitlines())
    print('\n'.join(diff))

# Example strings
#string1 = "This is a sample text."
#string2 = "This is an example text."

# Print the differences
#print_diff(string1, string2)


# In[2]:


#Used for compression tests

def write_binary_file(binary_element:bytearray,file_path:str="binary_file.txt"):
    # Open the file in binary write mode ('wb')
    with open(file_path, 'wb') as file:
        file.write(binary_element)
        
def read_binary_file(file_path):
    with open(file_path, 'rb') as file:
        # Write the byte array to the file
        all_data=file.read()
        return all_data
    
# Define a function to write the integers to a file in append mode
def write_integers_to_file(filename, integer_list):
    with open(filename, 'a') as file:
        for integer in integer_list:
            file.write(str(integer))


# In[ ]:


def compress_list_of_strings_in_gzip_file(list_of_strings, output_file):
    """
        Compress a list of strings and write to a gzip file.

    Args:
        strings: List of strings to be compressed.
        output_file: Path to the output gzip file.
    """
    with gzip.open(output_file, 'wb') as f:
        for string in list_of_strings:
            # Convert string to bytes
            string_bytes = string.encode('utf-8')
            f.write(string_bytes)


# In[ ]:


class Singleton: 
    # Private variable to hold the unique instance of the class
    _instance = None
    """
        Checks if the instance already exists and returns the existing instance.
        If the instance does not exist, it creates a new instance and returns it.
    """
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._index = None
        return cls._instance
def create_folder(folder_name: str) -> None :
    """ Create a folder called "folder_name" """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


# In[16]:


def read_words_from_file(file_path):
    with open(file_path, 'r') as file:
        words = [line.strip() for line in file]
    return words

def merge_and_produce_unique_english_stop_words_file(file1_name:str,file2_name:str):
    # Read words from the two files
    words_from_file1 = read_words_from_file(file1_name)
    words_from_file2 = read_words_from_file(file2_name)

    # Concatenate the two lists of words removing duplicates
    concatenated_words = set(sorted(words_from_file1+words_from_file2))
    print("# Words: "+str(len(concatenated_words)))
    concatenated_words=sorted(concatenated_words)
   
    with open("english_stop_words.txt", 'w') as file:
        for string in concatenated_words:
            file.write(f"{string}\n")
            
#File1 comes from https://countwordsfree.com/stopwords
#File2 comes from https://www.kaggle.com/datasets/rowhitswami/stopwords/
#merge_and_produce_unique_english_stop_words_file("stop_words_english.txt","stopwords.txt")

