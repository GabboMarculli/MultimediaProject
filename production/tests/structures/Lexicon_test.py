#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import import_ipynb
from collections import OrderedDict
from random import randint

import os
import shutil
import sys
sys.path.append('../../')  # Go up two folders to the project root

from structures.Lexicon import Lexicon
from structures.LexiconRow import LexiconRow
from pre_processing.Decompress_collection import Collection_Reader
from building_data_structures.IndexBuilder import IndexBuilder 


# In[2]:


# import pytest
# import ipytest

# ipytest.autoconfig()

DIR_TEMP_FOLDER="TEMP"
DIR_LEXICON="LEXICON"
DIR_DOC_INDEX="DOC_INDEX"
DIR_INVERTED_INDEX="INV_INDEX"


# In[3]:


#%%ipytest

def test_lexicon_add_term():
    capacity = 5
    
    test_documents=["doc0"+"\t"+" testterm testterm testterm testterm testterm testterm testterm testterm testterm testterm",
                    "doc1"+"\t"+" term1 rrr",
                    "doc2"+"\t"+" term2 term2",
                    "doc3"+"\t"+" term3 term3 term3",
                    "doc4"+"\t"+" term4 term4 term4 term4"
                   ]
    
    indexBuilder=IndexBuilder(True,False,Collection_Reader("",-1,-1,False,False,test_documents))
    indexBuilder.single_pass_in_memory_indexing(15000000)
    indexBuilder.index_merging()
    
    
    
    lexicon = Lexicon(capacity,"../Structures/LEXICON/lexicon.bin","../Structures/DOC_INDEX/collection_statistics.bin")
    assert lexicon.is_empty()
    
    lex_row = LexiconRow("testterm", 10)
    lexicon.add_term(lex_row)

    key = "testterm".ljust(lex_row.MAX_TERM_LENGTH)

    assert len(lexicon._vocabulary) == 1
    assert lexicon._vocabulary == lexicon.get_structure()
    
    assert lexicon.get_terms(key).term == key
    assert lexicon.get_terms(key).term == lex_row.term
    assert lexicon.get_terms(key).dft == lex_row.dft

    assert not lexicon.is_empty()

    # Add 100 row to lexicon and test that:
    # - size remains lower or equal than 5 all the time
    # - structure follow the "LRU" cache replacement policy
    lexicon.add_term(LexiconRow("term1", 1))
    lexicon.add_term(LexiconRow("term2", 2))
    lexicon.add_term(LexiconRow("term3", 3))
    lexicon.add_term(LexiconRow("term4", 4))
    for i in range(5, 100):
        random_term = f"term{i}"
        lex_row = LexiconRow(random_term, i)
    
        lexicon.add_term(lex_row)
        assert len(lexicon.get_structure()) <= 5
        
        counter = capacity - 1
        for elem in lexicon.get_structure().values():
            assert elem.term == f"term{int(i - counter)}".ljust(lex_row.MAX_TERM_LENGTH)
            counter = counter - 1   


    lexicon.clear_structure()
    assert lexicon.is_empty()
    
    lexicon.close_file()
    
    if os.path.exists(DIR_LEXICON):
        shutil.rmtree(DIR_LEXICON)
                
    if os.path.exists(DIR_INVERTED_INDEX):
        shutil.rmtree(DIR_INVERTED_INDEX)
    
    if os.path.exists(DIR_DOC_INDEX):
        shutil.rmtree(DIR_DOC_INDEX)
    
    if os.path.exists(DIR_TEMP_FOLDER):
        shutil.rmtree(DIR_TEMP_FOLDER)
    
    test_documents=["doc0"+"\t"+" aaaaa ttt",
                    "doc1"+"\t"+" bbbbb rrr",
                    "doc2"+"\t"+" ccccc jjj",
                    "doc3"+"\t"+" happiness"]
    
    
    indexBuilder=IndexBuilder(True,False,Collection_Reader("",-1,-1,False,False,test_documents))
    indexBuilder.single_pass_in_memory_indexing(15000000)
    indexBuilder.index_merging()

    lexicon2 = Lexicon(capacity,"../Structures/LEXICON/lexicon.bin","../Structures/DOC_INDEX/collection_statistics.bin")
    
    found_entry = lexicon2.find_entry("random_word_not_present_in_lexicon")
    assert found_entry == None
    found_entry = lexicon2.find_entry("happiness")
    assert found_entry.term == "happiness".ljust(lex_row.MAX_TERM_LENGTH)

    assert lexicon2.is_empty()
    lex_row = lexicon2.get_entry("happiness")
    assert not lexicon2.is_empty()

    key = "happiness".ljust(lex_row.MAX_TERM_LENGTH)
    assert lexicon2.get_terms(key).term == key
    assert lexicon2.get_terms(key).term == lex_row.term
    assert lexicon2.get_terms(key).dft == lex_row.dft
    
    lexicon2.close_file()
    
    if os.path.exists(DIR_LEXICON):
        shutil.rmtree(DIR_LEXICON)
                
    if os.path.exists(DIR_INVERTED_INDEX):
        shutil.rmtree(DIR_INVERTED_INDEX)
    
    if os.path.exists(DIR_DOC_INDEX):
        shutil.rmtree(DIR_DOC_INDEX)
    
    if os.path.exists(DIR_TEMP_FOLDER):
        shutil.rmtree(DIR_TEMP_FOLDER)

