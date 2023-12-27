#!/usr/bin/env python
# coding: utf-8

# In[1]:


from typing import List,Tuple
import math
#import import_ipynb

import sys
sys.path.append('../')  # Go up two folders to the project root

#from utilities import General_Utilities as Utilities
import utilities.General_Utilities as Utilities


# In[2]:


"""
    This class is used in the project to implement integer compression.
    It contains static methods for compressing and uncompressing integer / list of integers.
    There are three kind of implementation of compression algorithms:
    
        - Unary Compression, it is used for term_freq posting list compression.
        - Variable Byte Compresson, it is used for compressing a single gap of a doc_id inside the d-gap list.
        - D-Gap Compression, it is used to compress a list of doc_ids gaps. 
"""
class Compression:
    
    def unary_compression_integer_list(integer_list:list) -> bytearray:
        """ Given a list of integers, returns a compressed version of the list in binary using
            Unary Compression.
            
            Given an integer x>0, the unary coding consists of (x-1) '1' and a final '0'.
            Ex. the number 7 is coded as '1111110'
        
            Args:
                integer_list: the list of integers that have to be compressed.
            
            Returns:
                the bytearray of the compressed list.
                the number of bytes needed to store a compressed list.
        """
        num_bit=0
        #Check and count how many bits are needed to represent the list.
        for integer in integer_list:
            if (integer<=0):
                print("Integer lower equal then 0",integer)
                return bytearray()
            num_bit+=integer
    
        #Then I count how many bytes I need to represent the list.
        num_bytes=num_bit//8+(1 if num_bit%8 !=0 else 0)

        #Structure to represent bits of the compressed list
        compressed_list=bytearray([0]*num_bytes)

        #Variables to take count of what are the bit and byte I'm currently working.
        current_byte=0
        current_bit=0

        for integer in integer_list:

            for i in range(0,integer):

                if (current_bit==8):
                    current_byte+=1
                    current_bit=0

                if (i==(integer-1)):
                    #In this case, I leave a position to the '0' last bit.
                    current_bit+=1
                    continue

                # The mask has a size of a byte and it consists of one '1' in the current_bit position and '0' in others.
                compressed_list[current_byte]=compressed_list[current_byte] | (1<<7-current_bit)
                current_bit+=1    
                
        return compressed_list
    
    

    def unary_decompression_integer_list(binary_data:bytearray, total_integers:int)->List[int]:
        """ Given a list of bytes and a total number of integers to read, it uncompresses the list of bytes and 
            decode the corresponding integers returning as a list of integers.

            Args:
                binary_data: binary representation of the compressed list
                total_integers: the total number of integers to be read
                
            Returns:
                the list of decompressed integers 
        """
        
        uncompressed_list=[]   

        max_mask=0b11111111
        current_integer=0
        
        #Read binary data at blocks of 1 byte.
        for data in binary_data:
            
            #First check if the entire byte is set to '1', in order to speed up a little the decompression.
            if (data==max_mask):
                current_integer+=8
            else:
                #This is the case where at least a '0' is present inside the byte.
                for index in range(0,8):
                    if (data & (1<<7-index)==0):
                        #I have found the '0' so I can add the decompressed integer to the list.
                        uncompressed_list.append(current_integer+1)

                        #Check if I finish to read all the integers.
                        if (len(uncompressed_list)==total_integers):
                            break

                        current_integer=0
                    else:
                        current_integer+=1
                        
        return uncompressed_list
    
    
     
    def variable_byte_compression_integer(num:int)->bytearray:
        """ Given an integer, it compresses the number using Variable Byte Encoding and returns 
            a compressed representation of the number. 
            
            Here a short summarization of what it does:
                the number is written in sup(log2(number+1)) bytes following the convention
                going from right-to-left "least significance to most significance part"
                fill all the bytes with the binary representation of the number in the first 7 positions
                if the byte is the most signicant then fill the first significant bit with '0'
                else fill the first significant bit with '1'
                # ex. 129 can be represented as: 
                #         position:   76543210 76543210
                #   representation:   00000001 10000001
                
            Args:
                num: the number to be compressed
                
            Returns:
                the compress representation in byte array of the number
                
        """

        if (num<=0):
            print("Integer lower equal then 0",num)
            return None

        compressed_integer=bytearray()
        
        #From the least significative to most significative
        while num>0:
            byte = num % 128
            num //= 128
            if num > 0:
                # Set the most significant bit to 1 except for the last byte
                byte |= 1<<7   
            #Put always in the first position sliding the others
            compressed_integer.insert(0, byte)
        return compressed_integer



    def variable_byte_compression_integer_list(integer_list:list)->bytearray:
        """ Given a list of integers, returns a compressed version of the list in binary using
            Variable Byte Compression.
        
            Args:
                integer_list: the list of integers that have to be compressed
                
            Returns:
                the bytearray of the compressed list
        """
        compressed_integer_list=bytearray()
        for integer in integer_list:
            compressedInteger=Compression.variable_byte_compression_integer(integer)
            if (compressedInteger!=None):
                compressed_integer_list.extend(compressedInteger)
        return compressed_integer_list
        
    
    def variable_byte_decompression_integer_list(binary_data:bytearray)->List[int]:
        """ Given a list of bytes, it uncompresses that list and decode 
             the corresponding integers returning the result in a list.

            Args:
                binary_data: binary representation of the compressed list
                
            Returns:
                the list of decompressed integers
                
        """
        uncompressed_list=[]
        current_integer=0

        for index,data in enumerate(binary_data):

            mask=0b01111111
            if (data & 1<<7 !=0):
                #It's the case of most significant bit set to '1', the continuation byte. Blanking the most significant bit
                data=data&mask 

                #Summing the other part considering the position in the continuation.
                current_integer=current_integer*128+data 
            else:
                #It's the case of most significant bit set to '0', the stop byte.

                #Except for the first byte read, when encountered a stop byte, append the previous integer to the list.
                if (index!=0): 
                    uncompressed_list.append(current_integer)

                current_integer=data

        #Append the last decompressed integer
        if len(binary_data) != 0:
            uncompressed_list.append(current_integer)

        return uncompressed_list
    
    
    def d_gap_compression(integer_list:list)->bytearray:
        """ Given a list of SORTED integers, it calculate the gap between numbers
            and compress it using variable_byte_compression.
            Pay attention any check is done if the list is not sorted.

                Args:
                    integer_list: the list of integers to be compressed

                Returns:
                    the bytearray of the compressed list  
        """

        if (len(integer_list)==0):
            return bytearray()

        if (len(integer_list)==1):
            return Compression.variable_byte_compression_integer_list([1])

        last_val=integer_list[0]
        d_gap_list=[1]

        for integer in integer_list[1:]:
            gap=integer-last_val
            last_val=integer
            d_gap_list.append(gap)

        return Compression.variable_byte_compression_integer_list(d_gap_list)


    def d_gap_decompression(binary_data: bytearray, starting_point: int) -> List:
        """ Given a list of bytes, it uncompresses that list using variable_byte_compression.
            The list obtained is the list of d-gaps so it is converted in actual doc_id numbers
            and it is returned.
            
                Args:
                    binary_data: the list of bytes to be decompressed

                Returns:
                    the final list of decompressed integers 
        """
        d_gap_list = Compression.variable_byte_decompression_integer_list(binary_data)
        if (d_gap_list==1):
            return [starting_point]
        return [starting_point] + [starting_point := starting_point + gap for gap in d_gap_list[1:]]
    


# # Example of usage

# In[3]:


import random

def generate_a_list_of_random_integers_save_compressed_and_uncompressed_using_unary(file_path:str="random_integers.txt"):
    # Generate a list of 10000000 random integers between 0 and 20
    random_integers = [random.randint(1, 20) for _ in range(10000000)]
    Utilities.write_integers_to_file(file_path, random_integers) #save not compressed
    
    binary=Compression.unary_compression_integer_list(random_integers)
    Utilities.write_binary_file(binary,"random_integers.bin")
   
    binary2=Utilities.read_binary_file("random_integers.bin")
    random_integers2=Compression.unary_decompression_integer_list(binary2,len(random_integers))
    
    if (random_integers!=random_integers2):
        print("Something goes wrong. This should never appear")

def generate_a_list_of_random_integers_save_compressed_and_uncompressed_using_variable_byte_encoding(file_path:str="incremental_integers.txt"):
    
    # Generate a list of 10000000 incremental integers
    incremental_integers = [i for i in range(1,10000000)]
    Utilities.write_integers_to_file(file_path, incremental_integers) #save not compressed
    
    binary=Compression.variable_byte_compression_integer_list(incremental_integers)
    Utilities.write_binary_file(binary,"incremental_integers.bin")
    
    binary2=Utilities.read_binary_file("incremental_integers.bin")
    incremental_integers2=Compression.variable_byte_decompression_integer_list(binary2)
    
    if (incremental_integers!=incremental_integers2):
        print("Something goes wrong. This should never appear")
        
#generate_a_list_of_random_integers_save_compressed_and_uncompressed_using_unary()
#generate_a_list_of_random_integers_save_compressed_and_uncompressed_using_variable_byte_encoding()


# In[ ]:




