# 11
# Stemming & Stopword Removal. Stemming and stopword removal should be implemented. For stemming, you can use any third-party library providing the Porter
# stemming algorithm or similar. For stopword removal, you can use any english stopwords list available on the Web. Ideally, your program should have a compile 
# flag that allows you to enalbe/disble stemming & stopword removal.

import re
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.stem import WordNetLemmatizer

from nltk.corpus import stopwords
custom_stop_words = set(stopwords.words('english'))
custom_stop_words.update(['oh', 'like', 'yes', 'please','well', 'yeah', 'hey', 'ok', 'also', 'yet', 'maybe', 'ever', 'sure', 'hello', 'goodbye'])

from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import demoji

class TextProcessor:
    def __init__(self, use_stemming=True, use_stopwords=True):
        self.use_stemming = use_stemming # flag per abilitare o disabilitare 
        self.use_stopwords = use_stopwords # flag per abilitare o disabilitare 
        self.stemmer = PorterStemmer()
        self.stop_words = custom_stop_words
        self.reg_exp_punctuation = r'[^\w\s]'
        self.reg_exp_hashtags = r'#\w+' 
        self.reg_exp_usernames = r'@\w+'
        self.sequencePattern = r"(.)\1\1+"
        self.seqReplacePattern = r"\1\1"
        self.lemmatizer = WordNetLemmatizer()

    def process_text(self, text):
        text = self.clean_text(text)

        tokenizer = RegexpTokenizer(r'\w+')
        word_tokens = tokenizer.tokenize(text)

        if self.use_stopwords:
            word_tokens = self.remove_stopwords(word_tokens)

        # Se faccio prima stem e poi lemmatize, ho che "sense" diventa "sen" invece di "sens"
        # Ma se faccio prima lemmatize e poi stem ho che "ellipses" diventa "ellipsi" invece di "ellips"
        # Ho scelto di mettere prima la lemmatizzazione perchè altrimenti si può perdere informazioni, poiché lo stemming tende a ridurre le parole alla loro forma più semplice rimuovendo affissi, 
        # mentre la lemmatizzazione mira a portare le parole alla loro forma di base. In questo caso, parole come "sense" possono essere troncate in "sen" prima di arrivare alla lemmatizzazione, 
        # causando una perdita di informazioni. Così almeno si ha la forma base corretta della parola
        word_tokens = self.lemmatize(word_tokens)

        if self.use_stemming:
            word_tokens = self.stem_text(word_tokens)

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


##############################################################################################
# testing
##############################################################################################

# Array di test in inglese
test_sentences = [
    "This is a sentence with multiple spaces  and punctuation!",
    "Oh no, there are special characters like @, #, $, %, and ^ in this sentence.",
    "What's the meaning of a 'wrong' apostrophe in the middle of a word?",
    "\"Multiple quotes\" and special characters?! Yes, please.",
    "I just can't understand why there are so many spaces          between words.",
    "Stop!!!! Using too many exclamation points!!! It doesn't make sense!!!!",
    "What's the difference between \"English quotes\" and 'single quotes'?",
    "Sometimes, sentences end with lots of commas,,,,,, which are annoying.",
    "Oh no, this sentence has no punctuation or spaces between words",
    "The excessive use of a period! Overdone!!!",
    "There's a tabulator\tbetween these words, making it weird.",
    "What's the use of a semicolon; when a comma or a period could be used?",
    "Who cares about correcting spelling or grammar errors: no one, apparently.",
    "Cats are running and jumping all over the place!",
    "The quick brown fox jumps over the lazy dog.",
    "She likes to read books, especially mystery novels.",
    "The conference starts at 9 AM sharp. Don't be late!",
    "The weather is beautiful today, with clear skies and a gentle breeze.",
    "Eating fruits and vegetables is essential for a healthy diet.",
    "Learning new skills is beneficial for personal and professional growth.",
    "Traveling to different countries exposes you to diverse cultures and traditions.",
    "The pen      😓    is on the  😓  !? tables  👿  riding .."
]

# Array dei risultati attesi in inglese
expected_results = [
    "sentenc multipl space punctuat",
    "special charact sentenc",
    "mean wrong apostroph middl word",
    "multipl quot special charact",
    "understand mani space word",
    "stop use mani exclam point make sens",
    "differ english quot singl quot",
    "sometim sentenc end lot comma annoy",
    "sentenc punctuat space word",
    "excess use period overdon",
    "tabul word make weird",
    "use semicolon comma period could use",
    "care correct spell grammar error one appar",
    "cat run jump place",
    "quick brown fox jump lazi dog",
    "like read book especi mysteri novel",
    "confer start 9 sharp late",
    "weather beauti today clear sky gentl breez",
    "eat fruit veget essenti healthi diet",
    "learn new skill benefici person profession growth",
    "travel differ countri expos divers cultur tradit",
    "pen tabl ride"
]

'''
text_processor = TextProcessor() 
processed_sentences = []
for sentence in test_sentences:
    processed_sentence = text_processor.process_text(sentence)
    processed_sentences.append(processed_sentence)


def check_test_results(test_array, expected_array):
    for i in range(len(test_array)):
        if test_array[i] != expected_array[i]:
            print(f"Test {i + 1}: Failed")
            print(test_array[i])

# Utilizzo della funzione
check_test_results(processed_sentences, expected_results)
'''
