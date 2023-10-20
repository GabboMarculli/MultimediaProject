import gzip
import io
from Dataset2 import DocumentProcessor

def parse_compressed_tsv_line_by_line(compressed_file_path):
    try:
        with open(compressed_file_path, 'rb') as f:
            with gzip.GzipFile(fileobj=f) as gz:
                buffer = io.TextIOWrapper(gz, encoding='utf-8')

                output_file = 'collection_cleaned.tsv'
                with open(output_file, 'w', encoding='utf-8') as output:
                    document_processor = DocumentProcessor(output)

                    # C'è bisogno di leggere la prima riga a parte perchè essa inizia con i seguenti metadati "# collection.tsv0000777000175000017502663675055413400073633015704 0ustar  spacemanidolspacemanidol0 "
                    # Quindi prima di entrare nel ciclo che legge tutte le righe, elimino questo prefisso
                    first_line = next(buffer)  # Leggi la prima riga
                    cleaned_first_line = ' '.join(first_line.split()[3:])  # Rimuovi la parte iniziale indesiderata
                    document_processor.process_and_write(0, cleaned_first_line)

                    for line in buffer:
                        pid, text = line.strip().split('\t')
                        document_processor.process_and_write(pid, text)

    except FileNotFoundError:
        print(f"File {compressed_file_path} non trovato.")
    except Exception as e:
        print(f"Si è verificato un errore durante l'analisi del file {compressed_file_path}: {e}")

# Esempio di utilizzo
parse_compressed_tsv_line_by_line('collection.tar.gz')