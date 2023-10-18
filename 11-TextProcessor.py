# 11
# Stemming & Stopword Removal. Stemming and stopword removal should be implemented. For stemming, you can use any third-party library providing the Porter
# stemming algorithm or similar. For stopword removal, you can use any english stopwords list available on the Web. Ideally, your program should have a compile 
# flag that allows you to enalbe/disble stemming & stopword removal.

import string
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import demoji

class TextProcessor:
    def __init__(self, use_stemming=True, use_stopwords=True):
        self.use_stemming = use_stemming # flag per abilitare o disabilitare 
        self.use_stopwords = use_stopwords # flag per abilitare o disabilitare 
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.reg_exp_punctuation = r'[^\w\s]'
        self.reg_exp_hashtags = r'#\w+' 
        self.reg_exp_usernames = r'@\w+'
        self.sequencePattern = r"(.)\1\1+"
        self.seqReplacePattern = r"\1\1"
        self.lemmatizer = WordNetLemmatizer()

    def process_text(self, text):
        text = self.clean_text(text)
        word_tokens = word_tokenize(text)

        if self.use_stemming:
            word_tokens = self.stem_text(word_tokens)
        if self.use_stopwords:
            word_tokens = self.remove_stopwords(word_tokens)

        word_tokens = self.lemmatize(word_tokens)

        return TreebankWordDetokenizer().detokenize(word_tokens)

    def stem_text(self, tokens):
        stemmed_words = [self.stemmer.stem(word)
                          for word in tokens]
        return stemmed_words

    def remove_stopwords(self, tokens):
        filtered_words = [word for word in tokens 
                          if word.lower() not in self.stop_words]
        return filtered_words

    
    def clean_text(self,text):
        # Trasformo le maiuscole in minuscole
        text = str(text).lower()

         # replace special characters 
        text = re.sub(self.reg_exp_hashtags, " ", text)
        text = re.sub(self.reg_exp_punctuation, " ", text)
        text = re.sub(self.reg_exp_usernames, " ", text)
        text = demoji.replace(text, " ")

        # Replace 3 or more consecutive letters by 2 letter : 'heyyyyyyyyyy' become 'heyy'
        text = re.sub(self.sequencePattern, self.seqReplacePattern, text)

        # replace multiple spaces with single space
        text = re.sub(' +', ' ', text)  

        return text.strip()
    
    def lemmatize(self, tokens):
        lemmatized = [self.lemmatizer.lemmatize(w) 
                      for w in tokens]
        
        return lemmatized


#pro = TextProcessor()
#text = "The pen      😓    is on the  😓  !? tables  👿  riding .."
#print(pro.process_text(text))
