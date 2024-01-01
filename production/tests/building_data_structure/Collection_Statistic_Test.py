#!/usr/bin/env python
# coding: utf-8

# In[1]:



import sys
import os
sys.path.append('../../')  # Go up two folders to the project root

import building_data_structures.CollectionStatistics as coll_stat


# In[2]:



def test_save_statistics():
    # Parametri di esempio
    num_documents = 8800000
    num_distinct_terms = 456230
    sum_document_lengths = 12300234

    if os.path.exists("Collection_statistics.txt"):
        os.remove("Collection_statistics.txt")
    
    # Creazione di un oggetto Collection_statistics e salvataggio delle statistiche
    collection_statistics = coll_stat.Collection_statistics("Collection_statistics.txt", num_documents, num_distinct_terms, sum_document_lengths)
    collection_statistics.save_statistics("Collection_statistics.txt")

    # Lettura del file e verifica del contenuto
    with open("Collection_statistics.txt", "r") as f:
        lines = f.readlines()

    name_values = [tuple(line.strip().split(":")) for line in lines]
    
    for name, value in name_values:
        if name == "Document Index Size":
            assert int(value) == num_documents
        elif name == "Vocabulary Size":
            assert int(value) == num_distinct_terms
        elif name == "Sum Document length":
            assert int(value) == sum_document_lengths
    
    try:
        bad_collection_statistics = coll_stat.Collection_statistics(-4, 100, 100)
    except ValueError as e:
        assert str(e) == "Values must be positive."

    try:
        bad_collection_statistics = coll_stat.Collection_statistics(100, 100, -2)
    except ValueError as e:
        assert str(e) == "Values must be positive."

    try:
        bad_collection_statistics = coll_stat.Collection_statistics(100, 100, "file.txt")
    except ValueError as e:
        assert str(e) == "Values must be integer."
        
    os.remove("Collection_statistics.txt")


# In[3]:




def test_binary_mode():
    
    if os.path.exists("coll_stat.bin"):
        os.remove("coll_stat.bin")
    
    coll = coll_stat.Collection_statistics("coll_stat.bin", 50, 60, 70)

    assert coll.num_documents == 50
    assert coll.num_distinct_terms == 60
    assert coll.sum_document_lengths == 70
    
    coll.write_binary_mode()
    
    coll2 = coll_stat.Collection_statistics("coll_stat.bin")

    assert coll2.num_documents == 0
    assert coll2.num_distinct_terms == 0
    assert coll2.sum_document_lengths == 0
    
    coll2.read_binary_mode()
    
    assert coll2.num_documents == 50
    assert coll2.num_distinct_terms == 60
    assert coll2.sum_document_lengths == 70
    
    os.remove("coll_stat.bin")

