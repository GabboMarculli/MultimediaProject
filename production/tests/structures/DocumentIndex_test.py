#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import sys
sys.path.append('../../')  # Go up two folders to the project root


from structures.DocumentIndex import DocumentIndex 
from structures.DocumentIndexRow import DocumentIndexRow


# In[2]:




# In[3]:




#Pay attention: because of it has been declared as singleton variable, if you execute multiple times on the same jupyter
#notebook it will fail after the first execution time, unless you restart the notebook. Ask G.Marcuccetti

# TEST FOR "DOCUMENT INDEX"
def test_document_index_structure():
    doc = DocumentIndex()

    doc.add_document(1,"doc_name_1", "Information retrieval system")
    
    assert doc.is_empty() == False
    document = doc.get_document(1)
    assert document.doc_id==1
    assert document.doc_no.strip()=="doc_name_1"
    assert document.document_length == 3

    
    assert doc.number_of_documents == 1
    assert doc.total_document_length == 3

    doc.add_document(2, "doc_name2","Document index")
    doc.add_document(3, "doc_name3","My name is Pippo")
    assert doc.get_document(2).document_length == 2
    assert doc.get_document(3).document_length == 4

    assert doc.number_of_documents == 3
    assert doc.total_document_length == 9

    assert doc.get_document(5) is None

    doc.add_document(4, "","")
    assert doc.get_document(4).document_length == 0

    # create a copy of the structure and test if copy is equal
    doc_aux = doc.get_structure()
    assert doc.get_document(3).doc_id==doc_aux[3].doc_id and doc.get_document(3).document_length == doc_aux[3].document_length
    # test singleton
    doc2 = DocumentIndex()
    assert doc2.get_document(1).document_length == 3
    doc2.add_document(5,"doc_no_5","Test for singleton class")
    assert doc.get_document(5) == doc2.get_document(5)

    # test if "clear_structure" works
    assert doc.is_empty() == False
    doc.clear_structure()
    assert doc.is_empty() ==True

    # Try to pass "doc_id" as a string
    try:
        doc.add_document("hello", "hello","")
        assert 1==0
    except ValueError as e:
        assert 1==1

    # Try to pass "text" as a integer
    try:
        doc.add_document(5, 5,"")
        assert 1==0
    except ValueError as e:
        assert 1==1


# In[4]:



def test_write_document_index_to_file():
    
    if os.path.exists("prova.bin"):
        os.remove("prova.bin")
    
    doc = DocumentIndex()

    doc.add_document(1,"doc_name_1", "Information retrieval system")
    doc.add_document(2,"doc_name2", "Document index")
    
    try:
    
        file=open("prova.bin","ab")

        doc.write_document_index_to_file(file,0)
       
        file.close()
        

        file=open("prova.bin","rb")
        
        temp=file.read()
        print(temp)
        assert temp[0]==1
        assert temp[1]==0
        assert temp[2]==0
        assert temp[3]==0
        assert temp[4]==0
        assert temp[5]==0
        assert temp[6]==0
        assert temp[7]==0
        assert temp[8]==100 #d
        assert temp[9]==111 #o
        assert temp[10]==99 #c
        assert temp[11]==95 #_
        assert temp[12]==110 #n
        assert temp[13]==97 #a
        #....
        assert temp[30]==32 # white spaces
        assert temp[39]==0 # 
        assert temp[40]==3 # as the number of words in the sentence

        assert temp[52]==100 #d
        assert temp[53]==111 #o
        assert temp[54]==99 #c
        assert temp[55]==95 #_
        assert temp[56]==110 #n
        assert temp[57]==97 # a
        assert temp[58]==109 # m
        assert temp[59]==101 #e
        assert temp[60]==50 # 2
        assert temp[61]==32 #  white space
    
        file.close()
        
        
    except Exception as e:   
            print (e) 
    finally:
        file.close()
        
    
    if os.path.exists("prova.bin"):
        os.remove("prova.bin")
    

