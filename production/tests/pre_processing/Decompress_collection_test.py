#!/usr/bin/env python
# coding: utf-8

# In[1]:




import gzip
import sys
import os
sys.path.append('../../')  # Go up two folders to the project root

from pre_processing.Decompress_collection import Collection_Reader,execute_CPU_BOUND_preprocessing


# # Tests

# In[2]:





# In[3]:


tot_doc=[
"0     The pen is on the table",
"1     The day is very sunny",
"2     Goodmoring new article",
"3     A cat is faster then a dog",
"4     How are you",
"5     A boy is a man with low age",
"6     Lake Ontario is one of the biggest lake in the world",
"7     English is worst than Italian",
"8     Spiderman is the best superhero in Marvel universe",
"9     Last night I saw a Netflix series",
"10    A penny for your thoughts",
"11    Actions speak louder than words",
"12    All that glitters is not gold",
"13    Beauty is in the eye of the beholder",
"14    Birds of a feather flock together",
"15    Cleanliness is next to godliness",
"16    Don't count your chickens before they hatch",
"17    Every people cloud has a silver lining people",
"18    Fool me once shame on you fool me twice shame on me",
"19    Honesty is the best policy.",
"20    If the shoe fits, wear it",
"21    It's a piece of cake",
"22    Jump on the bandwagon",
"23    Keep your chin up",
"24    Let the cat out of the bag",
"25    Make a long story short",
"26    Necessity is the mother of invention",
"27    Once in a blue moon",
"28    Practice makes perfect",
"29    Read between the lines",
"30    The early bird catches people the worm",
"31    The pen is mightier than the sword",
"32    There's no smoke without fire",
"33    To each his own",
"34    Two heads are better than one",
"35    You can't have your cake and eat it too",
"36    A watched pot never boils",
"37    Beggars can't be choosers",
"38    Better late than never",
"39    Calm before the storm",
"40    Curiosity killed the cat",
"41    Every dog has its day",
"42    Great minds think alike",
"43    Hope for the best prepare for the worst",
"44    Ignorance is bliss.",
"45    It's the last straw that breaks the camel's back",
"46    Laugh and the world laughs with you weep and you weep alone",
"47    Money can't buy happiness",
"48    No news is good news",
"49    Out of sight out of mind",
"50    People who live in glass houses shouldn't throw stones",
"51    Rome wasn't built in a day",
"52    Silence is golden",
"53    The apple doesn't fall far from the tree",
"54    The more, the merrier",
"55    There's no place like home",
"56    Two wrongs don't make a right",
"57    When in Rome do as the Romans do",
"58    You reap what you sow",
"59    People people people"
]


# In[4]:


def test_execute_CPU_BOUND_preprocessing():
    
    lista_ritorno=execute_CPU_BOUND_preprocessing(0,tot_doc,False)
    
    assert len(lista_ritorno)==len(tot_doc)
    assert lista_ritorno[0]=="0 the pen is on the table"
    assert lista_ritorno[1]=="1 the day is very sunny"
    assert lista_ritorno[52]=="52 silence is golden"
    
    lista_ritorno=execute_CPU_BOUND_preprocessing(44,tot_doc,True)
    assert lista_ritorno[0]=="0 pen tabl"
    assert lista_ritorno[1]=="1 day sunni"
    assert lista_ritorno[52]=="52 silenc golden"
     


# In[5]:



def test_Collection_Reader_using_test_collection():
    
    #Testing the basic property of the iterator
    
    collection=Collection_Reader("",-1,-1,False,False,tot_doc)
    
    count=0
    for doc in collection:
        count+=1
    
    assert count==60
   
    collection=Collection_Reader("",-1,-1,False,False,tot_doc)
    doc1=next(collection)
    
    assert doc1=="0 the pen is on the table"
    
    doc2=next(collection)
    assert doc2=="1 the day is very sunny"
    
    for doc in collection:
        count+=1
    
    try:
        #Testing the Raise exception.
        next(collection)
    except:
        assert 1==1
    

    new_doc=[]
    new_doc.extend(tot_doc)
    new_doc[0]="qwertyuiopè*123c-asdada0\tThe pen is on the table"
    
    collection=Collection_Reader("",-1,-1,False,True,new_doc)
    assert next(collection)=="0 the pen is on the table"
    
    new_doc=[]
    new_doc.extend(tot_doc)
    new_doc[0]="qwertyuiopè*123c-asdada0\tThe pen is on the table"
    
    collection=Collection_Reader("",-1,-1,True,True,new_doc)
     
    doc1=next(collection)
    assert doc1 =="0 pen tabl"

    doc2=next(collection)
    assert doc2 =="1 day sunni"
        

    
def test_Collection_Reader_using_real_collection():
    
  
    if os.path.exists("prova.tar.gz"):
        os.remove("prova.tar.gz")

        
    
        
    with gzip.open("prova.tar.gz", 'wt') as gzip_file:
        for doc in tot_doc:
            gzip_file.write(doc + '\n')
    
    collection=Collection_Reader("./prova.tar.gz",5,1,False,False)
    
    count=0
    for doc in collection:
        count+=1
    
    assert count==61
    
    collection=Collection_Reader("./prova.tar.gz",5,1,False,False)
    
    doc1=next(collection)
    
    assert doc1=="0 the pen is on the table"
    
    doc2=next(collection)
    assert doc2=="1 the day is very sunny"
    
    
    for doc in collection:
        count+=1
    
    try:
        #Testing the Raise exception.
        next(collection)
    except:
        assert 1==1
        
    collection=Collection_Reader("./prova.tar.gz",5,1,True,False)
     
    doc1=next(collection)
    assert doc1 =="0 pen tabl"

    doc2=next(collection)
    assert doc2 =="1 day sunni"   
    
    for doc in collection:
        count+=1
    
    os.remove("prova.tar.gz")
    

    

