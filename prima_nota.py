import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
import pandas as pd
from datetime import datetime
import os

class PrimaNotaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prima Nota - Gestione Movimenti")
        
        # Dati
        self.movimenti = []
        self.saldo_corrente = 0.0
        
        # Frame principale
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Campi di input
        ttk.Label(main_frame, text="Data:").grid(row=0, column=0, sticky=tk.W)
        self.data_entry = DateEntry(main_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  locale='it_IT')  # Formato data italiano
        self.data_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Dettagli Fattura:").grid(row=1, column=0, sticky=tk.W)
        self.fattura_entry = ttk.Entry(main_frame, width=40)
        self.fattura_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Entrate POS:").grid(row=2, column=0, sticky=tk.W)
        self.entrate_pos_entry = ttk.Entry(main_frame, width=15)
        self.entrate_pos_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Entrate Contanti:").grid(row=3, column=0, sticky=tk.W)
        self.entrate_cash_entry = ttk.Entry(main_frame, width=15)
        self.entrate_cash_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Uscite Contanti:").grid(row=4, column=0, sticky=tk.W)
        self.uscite_cash_entry = ttk.Entry(main_frame, width=15)
        self.uscite_cash_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Saldo
        ttk.Label(main_frame, text="Saldo Corrente:", font=('Helvetica', 10, 'bold')).grid(row=5, column=0, sticky=tk.W)
        self.saldo_label = ttk.Label(main_frame, text="€ 0.00", font=('Helvetica', 10, 'bold'))
        self.saldo_label.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Pulsanti
        ttk.Button(main_frame, text="Registra Movimento", command=self.registra_movimento).grid(row=6, column=0, pady=10)
        ttk.Button(main_frame, text="Salva su Excel", command=self.salva_excel).grid(row=6, column=1, pady=10)
        
        # Tabella movimenti
        columns = ('Data', 'Fattura', 'Entrate POS', 'Entrate Cash', 'Uscite Cash', 'Saldo')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        
        # Configurazione colonne
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column('Fattura', width=200)  # Colonna fattura più larga
        
        self.tree.grid(row=7, column=0, columnspan=3, pady=10)
        
        # Scrollbar per la tabella
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=7, column=3, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)

    def registra_movimento(self):
        try:
            # Recupera i valori dai campi
            data = self.data_entry.get_date().strftime('%d/%m/%Y')
            fattura = self.fattura_entry.get()
            entrate_pos = float(self.entrate_pos_entry.get() or 0)
            entrate_cash = float(self.entrate_cash_entry.get() or 0)
            uscite_cash = float(self.uscite_cash_entry.get() or 0)
            
            # Calcola il nuovo saldo
            self.saldo_corrente += (entrate_pos + entrate_cash - uscite_cash)
            
            # Crea il movimento
            movimento = {
                'Data': data,
                'Fattura': fattura,
                'Entrate POS': entrate_pos,
                'Entrate Cash': entrate_cash,
                'Uscite Cash': uscite_cash,
                'Saldo': self.saldo_corrente
            }
            self.movimenti.append(movimento)
            
            # Aggiorna la tabella
            self.tree.insert('', 'end', values=(
                data, fattura, 
                f"€ {entrate_pos:.2f}", 
                f"€ {entrate_cash:.2f}", 
                f"€ {uscite_cash:.2f}",
                f"€ {self.saldo_corrente:.2f}"
            ))
            
            # Aggiorna il saldo visualizzato
            self.saldo_label.config(text=f"€ {self.saldo_corrente:.2f}")
            
            # Pulisce i campi di input
            self.pulisci_campi()
            
        except ValueError:
            messagebox.showerror("Errore", "Inserire valori numerici validi per gli importi")

    def pulisci_campi(self):
        """Pulisce tutti i campi di input"""
        self.fattura_entry.delete(0, tk.END)
        self.entrate_pos_entry.delete(0, tk.END)
        self.entrate_cash_entry.delete(0, tk.END)
        self.uscite_cash_entry.delete(0, tk.END)

    def salva_excel(self):
        """Salva i movimenti in un file Excel"""
        if not self.movimenti:
            messagebox.showwarning("Attenzione", "Nessun movimento da salvare")
            return
            
        try:
            df = pd.DataFrame(self.movimenti)
            nome_file = f"prima_nota_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(nome_file, index=False)
            messagebox.showinfo("Successo", f"Dati salvati in {nome_file}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel salvare il file: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = PrimaNotaApp(root)
    root.mainloop() 