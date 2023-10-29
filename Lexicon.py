# #####################################################################
#                      LEXICON                                        #
# #####################################################################
import os
import shutil

import math
from collections import defaultdict, Counter
from typing import List
import sys

# creo una cartella
def create_folder(folder_name: str) -> None :
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# scrivo su disco, sul file "file_name" il contenuto della struttura dati "struct"
def write_to_block(file_name: str, struct: defaultdict) -> None:
    """ Write into a file_name on disk."""
    with open(file_name, "w") as f:
        for index, term in enumerate(struct.keys()):
            f.write(struct[term].to_string())

            if index != len(struct.keys()) - 1:
                f.write("\n")
        
# Passo alla funzione l'inverted index COMPLETO, scorro tutte le righe dell'inverted index che sarà nel formato
#  ciao  3:2 3:3
#  come 1:1 4:4 ....

# esempio di parametri per il lexicon: 
# block_size=2200, DIR_FOLDER = "Lexicon", file_output_path = "./lexicon", file_extension = ".txt", file_input_path = inverted_index_file
def create_lexicon(file_input_path: str, file_output_path: str, DIR_FOLDER: str, file_extension: str, block_size: int) -> None:
    '''
    Function returns a file with one row for each distinct term in the corpus. Rows are composed by:
    term, document frequency, inverse document frequency, term upper bound
    Each values is separated by a comma.

    Args:
        file_input_path: file that contains the inverted index
        file_output_path: file that will contains the result
        DIR_FOLDER: folder that will contains the output file
        file_extension: extension of the file
        block_size: dimension of rows in main memory
    '''
    try:
        lexicon = Lexicon()
        create_folder(DIR_FOLDER)
        nr_block = 0
        with open(file_input_path, 'r') as file:
            for line in file:
                # term sarà qualcosa tipo "ciao", invece la postings list sarà 3:2 3:3 ecc
                elements = line.split()
                term = elements[0]          
                postings_list = ' '.join(elements[1:])
                
                # il dft si trova facendo la split su spazi e punti e virgola di tutta la posting list
                dft = len(postings_list.split())
                
                sigmat = 0 # come si calcola il sigmat???

                if (sys.getsizeof(lexicon.get_structure()) > block_size):  #Free memory available
                    write_to_block(DIR_FOLDER + file_output_path + str(nr_block) + file_extension, lexicon.get_structure())
                    lexicon.clear_structure()
                    nr_block=nr_block + 1 

                lexicon.add_posting(term, dft, sigmat)

            #Finally, saving the last remaing block.       
            if (not lexicon.is_empty()):   
                write_to_block(DIR_FOLDER + file_output_path + str(nr_block) + file_extension, lexicon.get_structure())
                
    except IOError as e:
        print(f"Error reading from {file_input_path}: {e}")
        return None
    
# CONTENUTO DI UNA RIGA DEL LEXICON
class LexiconRow:
    def __init__(self, term, dft, sigmat):
        # Il termine vero e proprio
        self.term = term

        # Document frequency of the term
        # Come si calcola questa??
        self.dft = dft

        # Inverse of document frequency of the term. 
        # Può essere zero il dft?? nel caso non posso farne la divisione
        idft = 0
        #if dft != 0:
        #    idft = math.log(DocumentIndex.number_of_documents/self.dft)               
        self.idft = idft

        # Term's upper bound
        # Come si calcola??
        self.sigmat = sigmat

    def to_string(self):    # correggi che rimane una riga bianca finale nel file
        string = ' '.join([str(self.term) , str(self.dft) , str(self.idft), str(self.sigmat)])
        return string    

# anche qui andrebbe usato singleton così da poter richiamare facilmente la classe con l'unica istanza che possiede
# Ha senso avere questa classe? tanto leggo una riga per volta dal file dell'inverted index, ogni riga è indipendente dall'altra nel calcolo
class Lexicon:
    def __init__(self):
        self._vocabulary = defaultdict(LexiconRow) # oppure "dictionary"??

    # sigmat è intero o double??
    def add_posting(self, term: str, dft: int, sigmat: int) -> None:
        """Adds a document to the lexicon."""
        # Append new row to the lexicon
        if (self.get_postings(term)==None):
            self._vocabulary[term]=[]
        self._vocabulary[term] = LexiconRow(term, dft, sigmat)
             
    def get_postings(self, term: str) -> List[LexiconRow]:
        """Fetches a row to the lexicon"""
        if (term in self._vocabulary):
            return self._vocabulary[term]
        return None
    
    def is_empty(self)->bool:
        """Check if there is no term in the lexicon."""
        return len(self.get_terms())==0
    
    def get_terms(self) -> List[str]:
        """Returns all unique terms in the lexicon."""
        return self._vocabulary.keys() 
    
    def clear_structure(self):
        """ It clears the lexicon data structure."""
        self._vocabulary.clear()
    
    def get_structure(self):
        """Returns the lexicon data structure."""
        return self._vocabulary
    
create_lexicon("inverted_index.txt", "lexicon", "Lexicon", ".txt", 2200)

# #####################################################################
#                      DOCUMENT INDEX                                 #
# #####################################################################

# DURANTE LA MAP PHASE DELL'INDEX BUILDER (IN CUI SI CREA L'INDICE), PER OGNI ITERAZIONE PROCESSI UN DOCUMENTO DIVERSO: E' QUI CHE DEVI FARE LA ADD DI UNA RIGA AL DOCUMENT INDEX
# SEMPLICEMENTE DURANTE LA MAP PHASE AVRAI UN FOR IN CUI OGNI ITERAZIONE PRECLUDE IL DOVER APRIRE UN DOCUMENTO: LEGGINE L'ID E METTILO NEL DOCUMENT INDEX

class DocumentIndexRow:

    # riceve un documento del tipo "0    ciao questo è un documento" e restituisce 0 come docid e 5 come document length
    def __init__(self, doc_no, text) -> None:
        '''
            This constructor receives a document number and the content of the document, and save
            the first parameter and the length of the second (that represents the document length)
        '''
        self.doc_id = doc_no
        self.document_length = self.count_words(text)

    # riceve un documento e conta quanti tokens contiene
    def count_words(self, text):
        return len(text.split())
    
class Singleton: # da usare???
    _instance = None
 
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

class DocumentIndex:
    def __init__(self):
        self._index = defaultdict(list)
        self.number_of_documents = 0 # serve per calcolare l'idf

    def add_posting(self, document: str) -> None:
        """Adds a document to the document index."""
        # Append new row to the docuemnt index 
        doc_id, text = document.strip().split('\t')

        if (self.get_postings(doc_id)==None):
            self._index[doc_id]=[]
        self._index[doc_id].append(DocumentIndexRow(doc_id,text).get_row())

        # Aggiorno il numero di documenti incrementando di uno questo valore per ogni nuovo documento inserito
        self.numberOfDocuments = self.numberOfDocuments + 1 
             
    def get_postings(self, doc_id: int) -> List[DocumentIndexRow]:
        """Fetches a row to the document index"""
        if (doc_id in self._index):
            return self._index[doc_id]
        return None
    
    def is_empty(self)->bool:
        """Check if there is no term in the document index."""
        return len(self.get_terms())==0
    
    def get_terms(self) -> List[str]:
        """Returns all unique terms in the index."""
        return self._index.keys() 
    
    def clear_structure(self):
        """ It clears the document index data structure."""
        self._index.clear()
    
    def get_structure(self):
        """Returns the document index data structure."""
        return self._index
    