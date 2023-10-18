# Esempio di lettura e analisi del dataset MSMARCO Passages.
# il codice legge il file del dataset e divide ogni riga in <pid> e <text>, quindi memorizza ciascun documento come un dizionario Python con le chiavi "pid" e "text". 
from TextProcessor11 import TextProcessor

class DocumentProcessor:
    def __init__(self, dataset_file):
        self.dataset_file = dataset_file
        self.text_processor = TextProcessor()

    def read_and_process_documents(self, output_file):
        processed_documents = []
        with open(self.dataset_file, 'r', encoding='utf-8') as file, open(output_file, 'w', encoding='utf-8') as output:
              for line in file:
                pid, text = line.strip().split('\t')

                # if(not pid.isdigit() or text == ''):  # non casca mai in questi casi apparentemente
                #    print("Questo non va bene")
                #    continue

                cleaned_text = self.text_processor.process_text(text)
                output.write(f"{pid}\t{cleaned_text}\n")
        return processed_documents        

# Esempio di utilizzo
dataset_file = "collection.tsv"
output_file = "cleaned_collection.tsv"
doc_processor = DocumentProcessor(dataset_file)
doc_processor.read_and_process_documents(output_file)