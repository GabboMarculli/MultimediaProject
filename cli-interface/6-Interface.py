import time

# ############################################################### A RIGA DI COMANDO

class Interface:
    def __init__(self):
        pass

    def run(self):
        while True:
            query = input("Inserisci una query (o 'q' per uscire): ")

            if query.lower() == 'q':
                print("Arrivederci!")
                break

            # Esempio di esecuzione di una query e calcolo del tempo di esecuzione
            query_terms = query.strip().split()
            start_time = time.time()

            # funzione per ritornare i documenti più importanti
            ranked_documents = f(query_terms) 

            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Tempo in millisecondi

            print(f"Tempo di esecuzione: {execution_time:.2f} ms")
            print("Risultati:")
            for doc_id, score in ranked_documents:
                print(f"Documento {doc_id}: Score {score}")

# if __name__ == "__main__":
#     demo_interface = Interface()
#    demo_interface.run()


# ############################################################# USANDO TKINTER
def clear_all():
    Sentence.delete('1.0', 'end-1c')
    documents_listbox.delete(0, tk.END)

def get_sentence():
    sen = Sentence.get("1.0",'end-1c')
    return sen

import tkinter as tk
import tkinter.font as font

class InterfaceHandler:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x400")
        self.root.title("Search engine")

        # Title
        self.myFont = font.Font(size=13)
        self.title = tk.Label(root, text="Search", fg='#0052cc', font=self.myFont)
        self.title.place(x=90, y=1)

        # Defining the first row
        self.lblfrstrow = tk.Label(root, text="Document :")
        self.lblfrstrow.place(x=50, y=80)

        # Entry for adding documents
        self.document_entry = tk.Text(root, bg="light yellow")
        self.document_entry.place(x=150, y=80, width=300, height=100)

        # Listbox for displaying documents
        self.documents_listbox = tk.Listbox(root, width=60)
        self.documents_listbox.place(x=150, y=220, width=300, height=100)

        # Submit button
        self.submitbtn = tk.Button(root, text="Submit", bg='blue', command=self.add_documents)
        self.submitbtn.place(x=250, y=335, width=55)

        # Clear button
        self.clearbtn = tk.Button(root, text="Clear", bg='blue', command=self.clear_all)
        self.clearbtn.place(x=180, y=335, width=55)

    def add_documents(self):
        query = self.document_entry.get("1.0", tk.END)
        # Esempio di esecuzione di una query e calcolo del tempo di esecuzione
        query_terms = query.strip().split()
        start_time = time.time()

        # funzione per ritornare i documenti più importanti
        ranked_documents = f(query_terms) 

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Tempo in millisecondi

        self.add_document(f"Tempo di esecuzione: {execution_time:.2f} ms")
        self.add_document("Risultati:")
        for doc_id, score in ranked_documents:
            self.add_document(f"Documento {doc_id}: Score {score}")

    def add_document(self, doc_id, score):
        document_text = [doc_id, ' : ', score]
        self.documents_listbox.insert(tk.END, document_text)
        self.clear_input()

    def clear_input(self):
        self.document_entry.delete("1.0", tk.END)

    def clear_all(self):
        self.clear_input()
        self.documents_listbox.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceHandler(root)
    root.mainloop()
