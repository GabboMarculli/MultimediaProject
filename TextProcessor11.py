import re
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import stopwords
from langdetect import detect

from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
import demoji

# Map that associates the abbreviation with the nationality.
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
        self.use_stemming = use_stemming # flag to disable stemming
        self.use_stopwords = use_stopwords # flag to disable remove stopwords
        self.reg_exp_punctuation = r'[^\w\s]'
        self.reg_exp_hashtags = r'#\w+' 
        self.reg_exp_usernames = r'@\w+'
        self.control_char_pattern=r'[\x00-\x1F\x7F-\x9F]'
        self.reg_exp_web_link_pattern=r'https*://\S+|www.\S+'

    def process_text(self, text):
        """ Process a text by cleaning, tokenizing, removing stopwords and stemming.

            Args:
                text: The text to be processed.
            Returns:
                The processed text after cleaning, tokenizing, removing stopwords, and stemming.
        """
        # Remove special characters
        text = self.clean_text(text)

        # Get the language
        language = language_map.get(detect(text))

        # Transform the document in a list of tokens
        tokenizer = RegexpTokenizer(r'\w+')
        word_tokens = tokenizer.tokenize(text)

        # Remove stopwords (if its flag is enable)
        if self.use_stopwords:
            word_tokens = self.remove_stopwords(word_tokens, language)

        # Do stemming (if its flag is enable)
        if self.use_stemming:
            word_tokens = self.stem_text(word_tokens, language)

        # Transform the list of tokens in a document
        print(word_tokens)
        return TreebankWordDetokenizer().detokenize(word_tokens)

    def stem_text(self, tokens, language):
        """Stem a list of tokens based on the specified language using Snowball Stemmer.

        Args:
            tokens: List of tokens to be stemmed.
            language: The language used for stemming.
        Returns:
            The list of tokens after stemming based on the provided language. 
            If the language is not supported, the function returns the original tokens.
        """
        try:
            if language != None:
                stemmer = SnowballStemmer(language)
            else:
                return tokens
        except ValueError: 
                return tokens
        
        # Do stem for each tokens in the list
        stemmed_words = [stemmer.stem(word)
                          for word in tokens]
        return stemmed_words

    def remove_stopwords(self, tokens, language):
        """Remove stopwords from a list of tokens based on the specified language.

        Args:
            tokens: List of tokens to be processed.
            language: The language used to identify the stopwords.
        Returns:
            The list of tokens after removing the stopwords based on the provided language. 
            If the language is not supported, the function returns the original tokens.
        """
        try:
            if language != None:
                stop_words = set(stopwords.words(language))
            else:
                return tokens
        except ValueError:
            return tokens

        # If the tokens is in the list of stopwords, remove it
        filtered_words = [word for word in tokens 
                        if word.lower() not in stop_words]
        return filtered_words
    
    def clean_text(self,text):
        """Clean the text by converting to lowercase, replacing special characters, and removing emojis.

        Args:
            text: The text to be cleaned.
        Returns:
            The cleaned text after converting to lowercase, replacing special characters, and removing emojis.
        """
        text = str(text).lower()

        # Replace special characters 
        combined_pattern = re.compile(self.reg_exp_hashtags + '|' + self.reg_exp_punctuation + '|' + self.reg_exp_usernames + '|' + self.control_char_pattern + '|' + self.reg_exp_web_link_pattern)
        text = re.sub(combined_pattern, " ", text)

        # Remove emoji
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
