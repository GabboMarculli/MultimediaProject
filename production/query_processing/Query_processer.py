#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os

#import import_ipynb

import sys
sys.path.append('../')  # Go up two folders to the project root
from pre_processing.TextProcessor import TextProcessor
from query_processing.DAAT import DAAT
from query_processing.MaxScore import Max_Score


# In[7]:


inv_index_path = "../INV_INDEX"
lexicon_path = "../LEXICON"
doc_index_path = "../DOC_INDEX"

class Query_processer:
    def __init__(self, flag: bool):
        self.text_processor = TextProcessor(flag)
        self.daat = DAAT()
        #self.max_score = Max_Score()

    def check_files_for_query_processing(self) -> bool:
        """
            Check the existence and non-emptiness of directories 'INV_INDEX', 'LEXICON', and 'DOCUMENT_INDEX' and its files.
        
        Returns:
            bool
        """
        if os.path.exists(doc_index_path + "/" + "document_index.bin") and os.path.exists(doc_index_path + "/" + "collection_statistics.bin"):
            if os.path.exists(inv_index_path + "/" + "doc_ids.bin") and os.path.exists(inv_index_path + "/" + "freq.bin"):
                if os.path.exists(lexicon_path + "/" + "lexicon.bin"):
                    return True
                    
        return False
            
    def process_query(self, query:str, scoring_function: str, alg, k: int, isConjunctive:bool):
        if not self.check_files_for_query_processing(): # serve?
            print("The structures needed for executing the query are not present. Check they are located in the correct location.")
            return 

        if query == "":
            return []

        # process query
        tokens = self.text_processor.process_text(query, True)

        # elimino i duplicati
        tokens = list(set(tokens))

        #print("Prima dello score sono a: ", time.time() - start, " secondi")
        if alg == "daat":
            result = self.daat.scoreQuery(k, scoring_function, tokens, isConjunctive)
        else:
            result = self.max_score.scoreQuery(k, scoring_function, tokens, isConjunctive)

        return [item[1] for item in result]    # torna solo i documenti


# In[10]:


import time

queries = [
    "",
    "the american restaurant dinner",
    "I love Nicola Tonellotto",
    "What to see in Paris",
    "Simple recipes for dinner",
    "How to lose weight in a healthy way",
    "Weekend weather forecast",
    "Best summer vacation destinations",
    "How to cook pasta with pesto",
    "Tips for improving productivity at work",
    "Advice for better sleep",
    "Latest news on the euro-dollar exchange rate",
    "Tips for caring for indoor plants",
    "Top 10 movies of all time",
    "Healthy breakfast ideas",
    "How to start a successful blog",
    "Interesting facts about space",
    "Popular workout routines",
    "Upcoming technology trends",
    "Book recommendations for summer reading",
    "DIY home decor projects",
    "Historical events that changed the world",
    "How to plan a budget-friendly trip",
    "Effective study techniques for exams",
    "Benefits of meditation",
    "Must-try local dishes in Italy",
    "Tips for staying motivated in the workplace",
    "Beginner's guide to coding",
    "Top fashion trends for the season",
    "Amazing places to visit in Japan",
    "Quick and healthy lunch ideas",
    "How to organize your workspace",
    "Cultural festivals around the world",
    "Natural remedies for common ailments",
    "Outdoor activities for a weekend getaway",
    "Famous works of art and their artists",
    "How to create a beautiful garden",
    "Mindfulness and stress reduction techniques",
    "Travel essentials for a road trip",
    "Benefits of regular exercise",
    "Interesting science experiments for kids",
    "Traditional dishes from different cuisines",
    "Inspirational quotes for daily motivation",
    "Tips for effective time management",
    "Guide to starting a small business",
    "Celestial events to watch for",
    "How to choose the right career path",
    "Budget-friendly home improvement ideas",
    "Famous historical figures and their contributions",
    "Unique hobbies to try",
    "Educational podcasts to listen to",
    "How to create a workout routine at home",
    "Exploring national parks and reserves",
    "Nutritious snacks for a busy lifestyle",
    "Crafting ideas for a rainy day",
    "Personal finance tips for young adults",
    "Latest trends in sustainable living",
    "Classic novels everyone should read",
    "Home workout equipment recommendations",
    "Techniques for effective public speaking",
    "Guide to understanding different art styles",
    "DIY beauty treatments at home",
    "Healthy habits for a balanced lifestyle",
    "Introduction to mindfulness meditation",
    "How to choose the perfect gift",
    "Career development strategies",
    "Popular board games for game night",
    "Famous landmarks and their history",
    "Tips for creating a productive morning routine",
    "World cuisines to explore through cooking",
    "Understanding the basics of investing",
    "Virtual travel experiences to try",
    "Simple and nutritious dinner recipes",
    "Cultural etiquette when traveling abroad",
    "Stress-relief techniques for a busy life",
    "Effective ways to improve communication skills",
    "Tips for organizing a successful event",
    "DIY projects for home organization",
    "Introduction to different musical genres",
    "How to plan a memorable celebration",
    "Guide to creating a personal budget",
    "Must-read books for personal growth"
]

query_processer = Query_processer(False)

#start_time = time.time()
#result = query_processer.process_query("the", "bm25", "daat", 7, False)
#elapsed_time = time.time() - start_time

#print(f"Query: {result}")
#print(f"Tempo impiegato per la query: {elapsed_time:.4f} secondi\n")

average = 0
for i, query in enumerate(queries):
     start_time = time.time()
     result = query_processer.process_query(query, "bm25", "daat", 7, False)
     elapsed_time = time.time() - start_time
     average += elapsed_time
     print(f"Query {i}: {result}")
     print(f"Tempo impiegato per la query: {elapsed_time:.4f} secondi\n")

print("Il tempo medio: ", average/82)
input("PREMI QUALSIASI TASTO")

# In[9]:


print(f"Query: {result}")
print(f"Tempo impiegato per la query: {elapsed_time:.4f} secondi\n")


# In[ ]:




