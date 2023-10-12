# 11
# Stemming & Stopword Removal. Stemming and stopword removal should be implemented. For stemming, you can use any third-party library providing the Porter
# stemming algorithm or similar. For stopword removal, you can use any english stopwords list available on the Web. Ideally, your program should have a compile 
# flag that allows you to enalbe/disble stemming & stopword removal.

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class TextProcessor:
    def __init__(self, use_stemming=True, use_stopwords=True):
        self.use_stemming = use_stemming # flag per abilitare o disabilitare 
        self.use_stopwords = use_stopwords # flag per abilitare o disabilitare 
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def process_text(self, text):
        if self.use_stemming:
            text = self.stem_text(text)
        if self.use_stopwords:
            text = self.remove_stopwords(text)
        return text

    def stem_text(self, text):
        words = text.split()
        stemmed_words = [self.stemmer.stem(word) for word in words]
        return ' '.join(stemmed_words)

    def remove_stopwords(self, text):
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return ' '.join(filtered_words)

