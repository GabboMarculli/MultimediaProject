#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import ipytest
#import import_ipynb

import sys
sys.path.append('../../')  # Go up two folders to the project root

from utilities.Compression import Compression 


# In[2]:


#import ipytest

#ipytest.autoconfig()


# # Tests

# In[3]:

def test_unary_compression_integer_list():
    
    assert bytearray() == Compression.unary_compression_integer_list([])
    assert bytearray() == Compression.unary_compression_integer_list([-1,0,-3])
    assert bytearray(b'\xf0')==Compression.unary_compression_integer_list([5])
    assert bytearray(b'\x00') == Compression.unary_compression_integer_list([1,1,1,1])
    assert bytearray(b'\x00\x00') == Compression.unary_compression_integer_list([1,1,1,1,1,1,1,1,1])
    assert bytearray(b'\xde\xfc') == Compression.unary_compression_integer_list([3,5,7])
    assert bytearray(b'\xde\xfc\x90') == Compression.unary_compression_integer_list([3,5,7,1,2,1,2])
    assert bytearray(b'\xff\xc8') == Compression.unary_compression_integer_list([11,1,2])
    

def test_unary_decompression_integer_list():
    
    assert Compression.unary_decompression_integer_list(bytearray(),0)==[]
    assert Compression.unary_decompression_integer_list(bytearray(b'\x00'),3)==[1,1,1]
    assert Compression.unary_decompression_integer_list(bytearray(b'\x00'),4)==[1,1,1,1]
    assert Compression.unary_decompression_integer_list(bytearray(b'\x00\x00'),9)==[1,1,1,1,1,1,1,1,1]
    assert Compression.unary_decompression_integer_list(bytearray(b'\xde\xfc'),3)==[3,5,7]
    assert Compression.unary_decompression_integer_list(bytearray(b'\xde\xfc\x90'),7)==[3,5,7,1,2,1,2]
    assert Compression.unary_decompression_integer_list(bytearray(b'\xff\xc8'),3)==[11,1,2]
    
    
def test_variable_byte_compression_integer():
    
    assert Compression.variable_byte_compression_integer(-1)==None
    assert Compression.variable_byte_compression_integer(0)==None
    assert Compression.variable_byte_compression_integer(5)==bytearray(b'\x05')
    assert Compression.variable_byte_compression_integer(39)==bytearray(b'\x27')
    assert Compression.variable_byte_compression_integer(129)==bytearray(b'\x01\x81')
    assert Compression.variable_byte_compression_integer(255)==bytearray(b'\x01\xff')
    assert Compression.variable_byte_compression_integer(1055307)==bytearray(b'\x40\xb4\xcb')
    
    
def test_variable_byte_compression_integer_list():
    
    assert Compression.variable_byte_compression_integer_list([])==bytearray()
    assert Compression.variable_byte_compression_integer_list([5,-1,0])==bytearray(b'\x05')
    assert Compression.variable_byte_compression_integer_list([5,2,3,4,1,6])==bytearray(b'\x05\x02\x03\x04\x01\x06')
    assert Compression.variable_byte_compression_integer_list([5,39,129,255,1055307])==bytearray(b'\x05\x27\x01\x81\x01\xff\x40\xb4\xcb')
    
    
def test_variable_byte_decompression_integer_list():
    
    assert Compression.variable_byte_decompression_integer_list(bytearray())==[]
    assert Compression.variable_byte_decompression_integer_list(bytearray(b'\x05'))==[5]
    assert Compression.variable_byte_decompression_integer_list(bytearray(b'\x05\x02\x03\x04\x01\x06'))==[5,2,3,4,1,6]
    assert Compression.variable_byte_decompression_integer_list(bytearray(b'\x05\x27\x01\x81\x01\xff\x40\xb4\xcb'))==[5,39,129,255,1055307]

    
def test_d_gap_compression():
    
    assert Compression.d_gap_compression([])==bytearray()
    assert Compression.d_gap_compression([1567])==bytearray(b'\x01')
    assert Compression.d_gap_compression([39])==bytearray(b'\x01')
    assert Compression.d_gap_compression([1,2,3,4,5,6])==bytearray(b'\x01\x01\x01\x01\x01\x01')
    assert Compression.d_gap_compression([5,7,8,10,12,24])==bytearray(b'\x01\x02\x01\x02\x02\x0c')
    
def test_d_gap_decompression():
    
    assert Compression.d_gap_decompression(bytearray(b'\x01'),39)==[39]
    assert Compression.d_gap_decompression(bytearray(b'\x01'),1567)==[1567]
    assert Compression.d_gap_decompression(bytearray(b'\x01\x01\x01\x01\x01\x01'),1)==[1,2,3,4,5,6]
    assert Compression.d_gap_decompression(bytearray(b'\x01\x01\x01\x01\x01\x01'),5)==[5,6,7,8,9,10]
    assert Compression.d_gap_decompression(bytearray(b'\x01\x02\x01\x02\x02\x0c'),5)==[5,7,8,10,12,24]