# 11
# Stemming & Stopword Removal. Stemming and stopword removal should be implemented. For stemming, you can use any third-party library providing the Porter
# stemming algorithm or similar. For stopword removal, you can use any english stopwords list available on the Web. Ideally, your program should have a compile 
# flag that allows you to enalbe/disble stemming & stopword removal.

import ipytest
import pytest

import re
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.stem import WordNetLemmatizer

from nltk.corpus import stopwords
from langdetect import detect

# custom_stop_words = set(stopwords.words('english'))
# custom_stop_words.update(['oh', 'like', 'yes', 'please','well', 'yeah', 'hey', 'ok', 'also', 'yet', 'maybe', 'ever', 'sure', 'hello', 'goodbye'])

from nltk.stem import SnowballStemmer, PorterStemmer
from nltk.tokenize import RegexpTokenizer
import demoji

# Mappa delle lingue
language_map = {
    'ar': 'arabic',
    'az': 'azerbaijani',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'fi': 'finnish',
    'fr': 'french',
    'de': 'german',
    'el': 'greek',
    'hu': 'hungarian',
    'id': 'indonesian',
    'it': 'italian',
    'kk': 'kazakh',
    'ne': 'nepali',
    'no': 'norwegian',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ru': 'russian',
    'sl': 'slovene',
    'es': 'spanish',
    'sv': 'swedish',
    'tg': 'tajik',
    'tr': 'turkish'
}

class TextProcessor:
    def __init__(self, use_stemming=True, use_stopwords=True):
        self.use_stemming = use_stemming # flag per abilitare o disabilitare 
        self.use_stopwords = use_stopwords # flag per abilitare o disabilitare 
        self.reg_exp_punctuation = r'[^\w\s]'
        self.reg_exp_hashtags = r'#\w+' 
        self.reg_exp_usernames = r'@\w+'
        self.control_char_pattern=r'[\x00-\x1F\x7F-\x9F]'
        self.reg_exp_web_link_pattern=r'https*://\S+|www.\S+'

    def process_text(self, text):
        # Rimuovo caratteri speciali e spazi multipli dal testo
        text = self.clean_text(text)

        # Rilevo la lingua del documento
        language = language_map.get(detect(text))

        # Trasformo il documento in una lista di tokens
        tokenizer = RegexpTokenizer(r'\w+')
        word_tokens = tokenizer.tokenize(text)

        # Se il flag delle stop words è attivo, le rimuovo
        if self.use_stopwords:
            word_tokens = self.remove_stopwords(word_tokens, language)
           
        # Se faccio prima stem e poi lemmatize, ho che "sense" diventa "sen" invece di "sens"
        # Ma se faccio prima lemmatize e poi stem ho che "ellipses" diventa "ellipsi" invece di "ellips"
        # Ho scelto di mettere prima la lemmatizzazione perchè altrimenti si può perdere informazioni, poiché lo stemming tende a ridurre le parole alla loro forma più semplice rimuovendo affissi, 
        # mentre la lemmatizzazione mira a portare le parole alla loro forma di base. In questo caso, parole come "sense" possono essere troncate in "sen" prima di arrivare alla lemmatizzazione, 
        # causando una perdita di informazioni. Così almeno si ha la forma base corretta della parola
        # word_tokens = self.lemmatize(word_tokens, language)

        # Se il flag dello stem è attivo, lo effettuo
        if self.use_stemming:
            word_tokens = self.stem_text(word_tokens, language)

        # Ritrasformo la lista di tokens in una stringa
        return TreebankWordDetokenizer().detokenize(word_tokens)

    def stem_text(self, tokens, language):
        try:
            if language == 'english':
                stemmer = PorterStemmer()
            else:
                stemmer = SnowballStemmer(language)
        except ValueError:
                # Se la lingua non è presente fra quelle della libreria nltk, esco senza effettuare modifiche agli elementi della lista
                return 
        
        stemmed_words = [stemmer.stem(word)
                          for word in tokens]
        return stemmed_words

    def remove_stopwords(self, tokens, language):
        try:
            # Seleziona il set di stopwords corrispondente alla lingua
            stop_words = set(stopwords.words(language))
        except ValueError:
            # Se la lingua non è presente fra quelle della libreria nltk, esco senza effettuare modifiche agli elementi della lista
            return

        filtered_words = [word for word in tokens 
                        if word.lower() not in stop_words]
        return filtered_words
    
    def clean_text(self,text):
        # Trasformo le maiuscole in minuscole
        text = str(text).lower()

        # replace special characters 
        combined_pattern = re.compile(self.reg_exp_hashtags + '|' + self.reg_exp_punctuation + '|' + self.reg_exp_usernames + '|' + self.control_char_pattern + '|' + self.reg_exp_web_link_pattern)
        text = re.sub(combined_pattern, " ", text)

        text = demoji.replace(text, " ")

        return text.strip()
    
    '''
    def lemmatize(self, tokens, language):
        lemmatizer = WordNetLemmatizer()
        
        lemmatized = [lemmatizer.lemmatize(w, language) 
                      for w in tokens]
        
        return lemmatized
    '''


##############################################################################################
# testing
##############################################################################################

# Array di test in inglese
TEST_SENTENCES = [
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
EXPECTED_SENTENCES = [
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

text_processor = TextProcessor() 

'''
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
check_test_results(processed_sentences, EXPECTED_SENTENCES) 
'''

@pytest.mark.parametrize("test_sentences,expected_results", list(zip(TEST_SENTENCES,EXPECTED_SENTENCES)))
def test_eval(test_sentences:str, expected_results:str):
    ris=text_processor.process_text(test_sentences)
    print (ris)
    print ("----")
    print (expected_results)
    assert ris == expected_results

