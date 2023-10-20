from TextProcessor11 import TextProcessor

class DocumentProcessor:
    def __init__(self, output_file):
        self.output_file = output_file
        self.text_processor = TextProcessor() 

    # passo a questa funzione pid e text, questa funzione pulisce text e scrive sul documento di output questi due valori
    def process_and_write(self, pid, text):
        cleaned_text = self.text_processor.process_text(text)
        self.output_file.write(f"{pid}\t{cleaned_text}\n")    
