# Prima Nota Multi-Struttura

Applicazione Streamlit per la gestione della prima nota di due strutture: Hotel Terranobile e Masseria Pietrasole.

## 🚀 Deploy su Streamlit Cloud

### 1. Preparazione Repository
- Crea un repository GitHub con questo codice
- Assicurati che tutti i file siano presenti:
  - `prima_nota_web.py` (file principale)
  - `requirements.txt` (dipendenze)
  - `README.md` (questo file)

### 2. Configurazione Streamlit Cloud
1. Vai su [share.streamlit.io](https://share.streamlit.io)
2. Connetti il tuo repository GitHub
3. Configura le variabili d'ambiente:
   - **Main file path**: `prima_nota_web.py`
   - **Python version**: 3.9+

### 3. Configurazione Secrets
Nel dashboard di Streamlit Cloud, vai su "Secrets" e aggiungi:

```toml
[passwords]
admin = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJ/8qHqKi"
utente = "$2b$12$8K1p/a0dL1LXMIgoEDFrwOe6J7K8K1p/a0dL1LXMIgoEDFrwOe6J7"
SACHIN = "$2b$12$meta2026_hash_here"
MICHELE = "$2b$12$meta2026_hash_here"
SANDRA = "$2b$12$meta2026_hash_here"
SEDE = "$2b$12$meta2026_hash_here"
```

### 4. Credenziali di Accesso
- **Username**: admin, utente, SACHIN, MICHELE, SANDRA, SEDE
- **Password**: password123, demo, meta2026 (rispettivamente)

## 🔧 Funzionalità

### ✅ Gestione Movimenti
- Inserimento movimenti con categorie automatiche
- Modifica e eliminazione movimenti
- Allegati PDF e immagini
- Flag "In attesa di fattura"

### ✅ Filtri e Ricerca
- Filtro per mese
- Ricerca testuale
- Filtro per movimenti in attesa

### ✅ Export Dati
- Excel con fogli multipli
- PDF in formato orizzontale
- CSV per compatibilità

### ✅ Sicurezza
- Autenticazione con password hashate
- Backup automatici
- Gestione errori robusta

## 📊 Struttura Dati

### Colonne Principali
- **Data**: Formato DD/MM/YYYY
- **Categoria**: Automatica per uscite cash
- **Dettagli**: Descrizione movimento
- **Entrate POS/Bonifico**: Importi POS
- **Incassi Assegni**: Assegni ricevuti
- **Versamento Assegno**: Assegni versati
- **Entrate Cash**: Contanti ricevuti
- **Uscite Cash**: Contanti spesi
- **In Attesa**: Flag fattura

### Saldi Calcolati
- **Saldo Contabile**: Movimenti confermati
- **Saldo Sospeso**: Movimenti in attesa
- **Disponibilità**: Totale disponibile

## 🔒 Sicurezza

### Autenticazione
- Password hashate con bcrypt
- Gestione sessioni Streamlit
- Timeout automatico

### Backup
- Backup automatico ogni salvataggio
- Mantenimento ultimi 5 backup
- Naming con timestamp

## 📱 Compatibilità

### Browser Supportati
- Chrome/Edge (raccomandato)
- Firefox
- Safari

### Dispositivi
- Desktop (ottimizzato)
- Tablet (compatibile)
- Mobile (limitato)

## 🛠️ Sviluppo Locale

```bash
# Installazione dipendenze
pip install -r requirements.txt

# Avvio applicazione
streamlit run prima_nota_web.py

# Avvio con accesso di rete
streamlit run prima_nota_web.py --server.address 0.0.0.0
```

## 📞 Supporto

Per problemi o richieste:
1. Controlla i log di Streamlit Cloud
2. Verifica la configurazione secrets
3. Controlla la connessione al repository

## 🔄 Aggiornamenti

L'applicazione si aggiorna automaticamente quando:
- Modifichi il codice nel repository
- Cambi la configurazione secrets
- Aggiorni requirements.txt

## ⚠️ Limitazioni Streamlit Cloud

- **Storage**: 1GB per app (gratuito)
- **RAM**: 512MB per app (gratuito)
- **Tempo**: Timeout dopo inattività
- **Concorrenza**: Un utente per volta
- **Backup**: Solo locali (non persistenti)

## 💡 Suggerimenti

1. **Backup Regolari**: Esporta i dati in Excel periodicamente
2. **Pulizia**: Rimuovi allegati vecchi se necessario
3. **Monitoraggio**: Controlla l'uso dello storage
4. **Aggiornamenti**: Mantieni le dipendenze aggiornate 