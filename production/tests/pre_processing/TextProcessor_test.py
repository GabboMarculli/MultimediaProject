#!/usr/bin/env python
# coding: utf-8

# In[1]:

import re
import sys
sys.path.append('../../')  # Go up two folders to the project root

from pre_processing.TextProcessor import TextProcessor 


# # Tests

# In[2]:


# In[6]:


TEST_SENTENCES=[
    "This is a sentence with multiple spaces  and punctuation!",
    "https://en.wikipedia.org/wiki/List_of_Unicode_characters ciao",
    "The first websiteâThe Manhattan Project:",
    "Each of these types of communitiesâ <html> prova </html>",
    "There are special characters like @, #, $, %, and ^ in this sentence.",
    "",
    "      .................   !!!!!! @#&                    ",
    " !%£&/  ($£(/  £()",
    "The $sun is shining! brightly                  ..... in the sky&&."
]

EXPECTED_SENTENCES_WITHOUT_STEMMING_AND_STOP_WORDS =[
    "this is a sentence with multiple spaces and punctuation",
    "ciao",
    "the first website the manhattan project",
    "each of these types of communities prova",
    "there are special characters like and in this sentence",
    "",
    "",
    "",
    "the sun is shining brightly in the sky"
]

anotherLanguage = [
    "Questa è una frase con spazi multipli e punteggiatura!",               # In italian
    "https://it.wikipedia.org/wiki/Elenco_dei_caratteri_Unicode ciao",
    "Il primo sito webâIl Progetto Manhattan:",
    "Ognuno di questi tipi di comunitàâ <html> prova </html>",
    "Ci sono caratteri speciali come @, #, $, % e ^ in questa frase.",
]

expected_sentences = [
    "questa una frase con spazi multipli e punteggiatura",
    "ciao",
    "il primo sito web il progetto manhattan",
    "ognuno di questi tipi di comunit prova",
    "ci sono caratteri speciali come e in questa frase",
]


# In[18]:

# test without stemming and stopword
proc = TextProcessor(False)

def test_without_flags():
	for i in range(0, len(TEST_SENTENCES)): # english
		assert proc.process_text(TEST_SENTENCES[i]) == EXPECTED_SENTENCES_WITHOUT_STEMMING_AND_STOP_WORDS[i]
        
	for i in range(0, len(anotherLanguage)): # italian
		assert proc.process_text(anotherLanguage[i]) == expected_sentences[i]

def test_return_multiple_tokens():
	assert proc.process_text(anotherLanguage[0],True)==["questa","una","frase","con","spazi","multipli","e","punteggiatura"]
	assert proc.process_text(anotherLanguage[1],True)==["ciao"]


# In[10]:


# WITH STOP WORDS REMOVING AND STEMMING

text_processor = TextProcessor(True)

def test_single_functionalities():
    # Test for regexp
    assert re.sub(text_processor.reg_exp_html_tags, "", "<html>This is an <b>example</b> text.</html>") == "This is an example text."
    assert re.sub(text_processor.reg_exp_usernames, "", "Hello @user123, how are you?") == "Hello , how are you?"
    assert re.sub(text_processor.reg_exp_web_link_pattern, "", "Visit our website: https://www.example.com") == "Visit our website: "
    assert re.sub(text_processor.reg_exp_punctuation, "", "This is a sentence with @ special characters!") == "This is a sentence with  special characters"
    
    # Test for stemming and stopword in english, italin and spanish
    assert text_processor.stem_text(["running", "jumped", "swimming"]) == ["run", "jump", "swim"]
    assert text_processor.remove_stopwords(["this", "is", "a", "test"]) == ["test"]
    assert text_processor.stem_text(["programmazione", "divertente", "complicata"]) == ["programmazion", "divertent", "complicata"]
    assert text_processor.stem_text(["programación", "divertida", "complicada"]) == ["programación", "divertida", "complicada"]
    assert text_processor.remove_stopwords(["esto", "es", "una", "prueba"]) == ["esto", "es", "una", "prueba"]


