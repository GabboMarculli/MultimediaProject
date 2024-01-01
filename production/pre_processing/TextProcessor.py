#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import SnowballStemmer

from typing import List
import time
import re

import sys
sys.path.append('../')  # Go up two folders to the project root
from utilities.General_Utilities import read_words_from_file 


# In[6]:


"""
    This class is used in the project to implement pre-processing text elaboration.
    It contains several methods for text cleaning, stemming and stop word removal.
"""
class TextProcessor:
    
    def __init__(self, use_stemming_and_stop_words_removal:bool):
        self.use_stemming_and_stop_words = use_stemming_and_stop_words_removal # flag to enable stemming and stop_words_removal
        
        #Regular expression used to clean a raw text.
        self.reg_exp_punctuation = r'[^\w\s]|_'
        self.reg_exp_html_tags=r'<[^>]+>'
        self.reg_exp_hashtags = r'#\w+' 
        self.reg_exp_usernames = r'@\w+'
        self.control_char_pattern=r'[^\x00-\x7F]+'
        self.reg_exp_web_link_pattern=r'https*://\S+|www.\S+'
        
        #A faster an improved version of PorterStemmer
        self.stemmer = SnowballStemmer("english")
        
        #Initialize the list of all English stopwords
        #Use the default NLTK stopword + additional stopwords find on the web and grouped in a single file.
        stop_word_list=[]
        try:
            stop_word_list=read_words_from_file("../utilities/english_stop_words.txt")
        except Exception as e:   
            print("Stopword file english_stop_words.txt not imported")
        self.stop_words=set(stopwords.words("english")+stop_word_list)
        
        #print(self.stop_words)
        #print(len(self.stop_words))
            
    def process_text(self, text:str, return_tokens = False)->str:
        """ Process a text by cleaning, tokenizing, removing stopwords and stemming(optionally).
            This is the main method called from outside, during the processing of all the documents.

            Args:
                text: The text to be processed.
            Returns:
                The processed text after cleaning, tokenizing, removing stopwords, and stemming.
        """
        
        # Remove special characters
        text = self.clean_text(text)
        
        # To handle case of empty string
        if not text:
            return text

        # Transform the document in a list of tokens
        tokenizer = RegexpTokenizer(r'\w+')
        word_tokens = tokenizer.tokenize(text)

        # Remove stopwords and apply stemming.
        if self.use_stemming_and_stop_words:
            word_tokens = self.remove_stopwords(word_tokens)
            word_tokens = self.stem_text(word_tokens)

        # Transform and return the list of tokens in a document (unique string)
        if return_tokens == True:
            return word_tokens
            
        return ' '.join(word_tokens)

    def stem_text(self, tokens:List[str])->List[str]:
        """Apply Stemming on a list of tokens using English language.
        
        Args:
            tokens: List of tokens to be stemmed.
        Returns:
            The list of tokens after stemming based on the provided language. 
        """
        
        # Do stem for each tokens in the list
        return [self.stemmer.stem(word) for word in tokens]

    def remove_stopwords(self, tokens:List[str]):
        """Remove stopwords from a list of stop words tokens in English language.

        Args:
            tokens: List of tokens to be processed.
            language: The language used to identify the stopwords.
        Returns:
            The list of tokens after removing the stopwords based on the provided language. 
            If the language is not supported, the function returns the original tokens.
        """

        # If the tokens is in the list of stopwords, remove it
        return [word for word in tokens if word not in self.stop_words]
    
    def clean_text(self,text:str)->str:
        """Clean the text by converting to lowercase, replacing special characters.

        Args:
            text: The text to be cleaned.
        Returns:
            The cleaned text after converting to lowercase, replacing special characters, and removing emojis.
        """
        text = str(text).lower()

        # Replace special characters 
        text = re.sub(self.control_char_pattern, " ", text)
        
        combined_pattern = re.compile(self.reg_exp_html_tags+'|'+self.reg_exp_hashtags + '|' + self.reg_exp_punctuation + '|' + self.reg_exp_usernames + '|' + self.reg_exp_web_link_pattern)
        text = re.sub(combined_pattern, " ", text)

        #Collapse white spaces between words.
        text = re.sub(r'\s+', ' ', text)

        return text.strip()
    
    '''
    def lemmatize(self, tokens, language):
        lemmatizer = WordNetLemmatizer()
        
        lemmatized = [lemmatizer.lemmatize(w, language) 
                      for w in tokens]
        
        return lemmatized
    '''

