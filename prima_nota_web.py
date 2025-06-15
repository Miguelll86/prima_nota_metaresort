import streamlit as st
st.set_page_config(page_title="Prima Nota Multi-Struttura", layout="wide")
import pandas as pd
from datetime import datetime
import os
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
import uuid
import bcrypt

# --- Logo in alto ---
# (RIMOSSO: il logo viene mostrato solo nella schermata di login)

# --- Configurazione pagina ---

# --- CSS per forzare maiuscolo e migliorare la tabella ---
st.markdown("""
<style>
/* Forza maiuscolo in tutti i campi di input tranne password */
.stTextInput input, .stTextArea textarea {
    text-transform: uppercase !important;
}

/* Escludi specificamente i campi password dal maiuscolo */
.stTextInput input[type="password"],
.stTextInput input[autocomplete="current-password"],
.stTextInput input[autocomplete="new-password"] {
    text-transform: none !important;
}

/* Migliora dimensioni e autosize della tabella */
.ag-theme-streamlit {
    font-size: 16px !important;
}

.ag-theme-streamlit .ag-cell {
    font-size: 16px !important;
    line-height: 1.2 !important;
    padding: 6px 8px !important;
    white-space: nowrap !important;
}

.ag-theme-streamlit .ag-header-cell {
    font-size: 16px !important;
    font-weight: bold !important;
    padding: 6px 8px !important;
}

/* Autosize colonne */
.ag-theme-streamlit .ag-cell-wrapper {
    width: 100% !important;
}

/* Migliora leggibilità */
.ag-theme-streamlit .ag-row {
    min-height: 40px !important;
}

/* Stile per placeholder maiuscolo (escludendo password) */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    text-transform: uppercase !important;
}

/* Stile per campi numerici - rimuove pulsanti +/- e migliora leggibilità */
.stNumberInput input {
    cursor: text !important;
    transition: all 0.2s ease !important;
    color: #000000 !important;
    font-weight: normal !important;
    background-color: #ffffff !important;
    border: 1px solid #cccccc !important;
}

.stNumberInput input:focus {
    background-color: #fff3cd !important;
    border-color: #ffc107 !important;
    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25) !important;
    color: #000000 !important;
    font-weight: normal !important;
}

.stNumberInput input:hover {
    border-color: #ffc107 !important;
    color: #000000 !important;
}

/* Nascondi i pulsanti +/- dei campi numerici */
.stNumberInput button {
    display: none !important;
}

/* Assicura che il testo rimanga sempre leggibile */
.stNumberInput input::placeholder {
    color: #666666 !important;
}

/* Stile per il valore inserito - sempre leggibile */
.stNumberInput input[value]:not([value=""]) {
    color: #000000 !important;
    font-weight: normal !important;
}

/* JavaScript per rimuovere maiuscolo dai campi password */
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Trova tutti i campi input
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    
    inputs.forEach(input => {
        // Se il campo ha placeholder che contiene "password" o è di tipo password
        if (input.type === 'password' || 
            (input.placeholder && input.placeholder.toLowerCase().includes('password'))) {
            input.style.textTransform = 'none';
        }
    });
});
</script>
</style>
""", unsafe_allow_html=True)

# --- Strutture ---
STRUTTURE = ["HOTEL TERRANOBILE", "MASSERIA PIETRASOLE"]

# --- Funzione per verificare password con bcrypt ---
def verify_password(password, hashed):
    """Verifica password usando bcrypt"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

# --- Funzione per hashare password ---
def hash_password(password):
    """Hasha password con bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# --- Utenti sicuri con Streamlit Secrets ---
def get_users():
    """Ottiene gli utenti da Streamlit Secrets"""
    try:
        return st.secrets.passwords
    except:
        # Fallback per sviluppo locale
        return {
            "admin": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJ/8qHqKi",  # password123
            "utente": "$2b$12$8K1p/a0dL1LXMIgoEDFrwOe6J7K8K1p/a0dL1LXMIgoEDFrwOe6J7",  # demo
            "SACHIN": "$2b$12$meta2026_hash_here",
            "MICHELE": "$2b$12$meta2026_hash_here", 
            "SANDRA": "$2b$12$meta2026_hash_here",
            "SEDE": "$2b$12$meta2026_hash_here"
        }

# --- Inizializzazione session state ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'struttura' not in st.session_state:
    st.session_state.struttura = STRUTTURE[0]
if 'dati' not in st.session_state:
    st.session_state.dati = {s: [] for s in STRUTTURE}
if 'saldo' not in st.session_state:
    st.session_state.saldo = {s: 0.0 for s in STRUTTURE}
if 'modifica_idx' not in st.session_state:
    st.session_state.modifica_idx = None
if 'storico_modifiche' not in st.session_state:
    st.session_state.storico_modifiche = {s: {} for s in STRUTTURE}

# --- Login ---
def login():
    st.markdown("""
        <style>
        .login-center {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            min-height: unset;
            margin-top: 40px;
        }
        .login-box {
            width: 220px;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 20px;
        }
        .login-input input {
            width: 160px !important;
            text-align: center;
        }
        /* Escludi i campi password dal maiuscolo forzato */
        .login-box input[type="password"] {
            text-transform: none !important;
        }
        </style>
        <div class='login-center'>
    """, unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=160)
    st.markdown("""
        <div class='login-box'>
    """, unsafe_allow_html=True)
    username = st.text_input("Username", key="login_username", max_chars=20, help="Inserisci il tuo username", placeholder="Username", label_visibility="collapsed")
    password = st.text_input("Password", type="password", key="login_password", max_chars=20, help="Inserisci la password", placeholder="Password", label_visibility="collapsed")
    if st.button("Accedi"):
        if username in get_users() and verify_password(password, get_users()[username]):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Benvenuto, {username}!")
            st.rerun()
        else:
            st.error("Credenziali non valide")
    st.markdown("""
        </div>
        </div>
    """, unsafe_allow_html=True)

if not st.session_state.logged_in:
    login()
    st.stop()

# Dopo il login, subito dopo la sidebar e prima di qualsiasi contenuto della pagina
# (RIMOSSO: visualizzazione doppia del logo struttura)

# --- Sidebar: selezione struttura ---
st.sidebar.title("Struttura")
st.session_state.struttura = st.sidebar.radio("Seleziona struttura", STRUTTURE)

# --- Logo struttura DOPO la selezione ---
if st.session_state.logged_in:
    logo_map = {
        "HOTEL TERRANOBILE": "logo_terranobile.png",
        "MASSERIA PIETRASOLE": "logo_pietrasole.png"
    }
    logo_path = logo_map.get(st.session_state.struttura)
    if logo_path and os.path.exists(logo_path):
        st.image(logo_path, width=180)

# --- Funzione per calcolare saldi ---
def calcola_saldi(movimenti):
    saldo_effettivo = 0.0
    saldo_sospeso = 0.0
    for m in movimenti:
        # Il saldo è dato solo da Entrate Cash + Incassi Assegni + Versamento Assegno - Uscite Cash
        delta = (
            m.get('Entrate Cash', 0.0) +
            m.get('Incassi Assegni', 0.0) +
            m.get('Versamento Assegno', 0.0) -
            m.get('Uscite Cash', 0.0)
        )
        if m.get('In Attesa', False):
            saldo_sospeso += delta
        else:
            saldo_effettivo += delta
    return saldo_effettivo, saldo_sospeso

# --- Funzione per salvataggio automatico su CSV con backup ---
def salva_dati_csv(struttura):
    """Salva dati su CSV con backup automatico"""
    try:
        # Crea una copia dei dati senza gli allegati per il CSV
        dati_per_csv = []
        for movimento in st.session_state.dati[struttura]:
            movimento_copy = movimento.copy()
            # Rimuovi i campi che non possono essere salvati in CSV
            movimento_copy.pop('Allegato', None)
            movimento_copy.pop('Modifiche', None)
            dati_per_csv.append(movimento_copy)
        
        df = pd.DataFrame(dati_per_csv)
        
        # Salva il file principale
        filename = f"dati_{struttura.replace(' ', '_')}.csv"
        df.to_csv(filename, index=False)
        
        # Crea backup con timestamp
        backup_filename = f"backup_{struttura.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(backup_filename, index=False)
        
        # Mantieni solo gli ultimi 5 backup
        import glob
        backup_files = glob.glob(f"backup_{struttura.replace(' ', '_')}_*.csv")
        backup_files.sort(reverse=True)
        for old_backup in backup_files[5:]:
            try:
                os.remove(old_backup)
            except:
                pass
        
        # Salva gli allegati come file separati
        salva_allegati_separati(struttura)
        
        return True
    except Exception as e:
        st.error(f"Errore nel salvataggio: {str(e)}")
        return False

# --- Funzione per export Excel ---
def export_excel(dati, struttura):
    """Esporta i dati in formato Excel"""
    try:
        # Crea DataFrame per l'export (senza allegati)
        df_export = pd.DataFrame([{k: v for k, v in m.items() if k not in ['Allegato', 'Modifiche']} for m in dati])
        
        # Crea un buffer per il file Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Foglio principale con i movimenti
            df_export.to_excel(writer, sheet_name='Movimenti', index=False)
            
            # Foglio con i saldi
            saldo_effettivo, saldo_sospeso = calcola_saldi(dati)
            saldi_df = pd.DataFrame({
                'Tipo': ['Saldo Contabile', 'Saldo Sospeso', 'Disponibilità'],
                'Importo': [saldo_effettivo, saldo_sospeso, saldo_effettivo + saldo_sospeso]
            })
            saldi_df.to_excel(writer, sheet_name='Saldi', index=False)
        
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.error(f"Errore nell'export Excel: {str(e)}")
        return None

# --- Funzione per export PDF ---
def export_pdf(dati, struttura):
    """Esporta i dati in formato PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from io import BytesIO
        
        # Crea buffer per il PDF con orientamento orizzontale
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        
        # Stili
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centrato
        )
        
        # Titolo
        elements.append(Paragraph(f"Prima Nota - {struttura}", title_style))
        elements.append(Spacer(1, 20))
        
        # Saldi
        saldo_effettivo, saldo_sospeso = calcola_saldi(dati)
        disponibilita = saldo_effettivo + saldo_sospeso
        
        saldi_data = [
            ['Tipo', 'Importo'],
            ['Saldo Contabile', f'€ {saldo_effettivo:.2f}'],
            ['Saldo Sospeso', f'€ {saldo_sospeso:.2f}'],
            ['Disponibilità', f'€ {disponibilita:.2f}']
        ]
        
        saldi_table = Table(saldi_data, colWidths=[2.5*inch, 2*inch])
        saldi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(Paragraph("Saldi", styles['Heading2']))
        elements.append(saldi_table)
        elements.append(Spacer(1, 20))
        
        # Tabella movimenti
        if dati:
            # Prepara i dati per la tabella con tutte le colonne
            movimenti_data = [['Data', 'Categoria', 'Dettagli', 'Entrate POS', 'Incassi Assegni', 'Versamento Assegno', 'Entrate Cash', 'Uscite Cash', 'In Attesa']]
            
            for movimento in dati:
                movimenti_data.append([
                    movimento.get('Data', ''),
                    movimento.get('Categoria', '')[:12] + '...' if len(movimento.get('Categoria', '')) > 12 else movimento.get('Categoria', ''),
                    movimento.get('Dettagli', '')[:25] + '...' if len(movimento.get('Dettagli', '')) > 25 else movimento.get('Dettagli', ''),
                    f"€ {movimento.get('Entrate POS/Bonifico', 0):.0f}",
                    f"€ {movimento.get('Incassi Assegni', 0):.0f}",
                    f"€ {movimento.get('Versamento Assegno', 0):.0f}",
                    f"€ {movimento.get('Entrate Cash', 0):.0f}",
                    f"€ {movimento.get('Uscite Cash', 0):.0f}",
                    'Sì' if movimento.get('In Attesa', False) else 'No'
                ])
            
            # Calcola larghezze colonne più compatte per formato orizzontale
            page_width = landscape(A4)[0] - 2*inch  # Larghezza pagina meno margini
            col_widths = [
                0.6*inch,   # Data (ridotta)
                0.8*inch,   # Categoria (ridotta)
                1.8*inch,   # Dettagli (ridotta)
                0.7*inch,   # Entrate POS (ridotta)
                0.7*inch,   # Incassi Assegni (ridotta)
                0.7*inch,   # Versamento Assegno (ridotta)
                0.7*inch,   # Entrate Cash (ridotta)
                0.7*inch,   # Uscite Cash (ridotta)
                0.4*inch    # In Attesa (ridotta)
            ]
            
            # Crea tabella movimenti
            movimenti_table = Table(movimenti_data, colWidths=col_widths)
            movimenti_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            elements.append(Paragraph("Movimenti", styles['Heading2']))
            elements.append(movimenti_table)
        else:
            elements.append(Paragraph("Nessun movimento registrato", styles['Normal']))
        
        # Genera PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        st.error("Per l'export PDF è necessario installare reportlab: pip install reportlab")
        return None
    except Exception as e:
        st.error(f"Errore nell'export PDF: {str(e)}")
        return None

# --- Funzione per salvare allegati come file separati ---
def salva_allegati_separati(struttura):
    allegati_dir = f"allegati_{struttura.replace(' ', '_')}"
    if not os.path.exists(allegati_dir):
        os.makedirs(allegati_dir)
    
    for movimento in st.session_state.dati[struttura]:
        if movimento.get('Allegato') and movimento.get('Allegato Nome'):
            try:
                allegato_path = os.path.join(allegati_dir, f"{movimento['ID']}_{movimento['Allegato Nome']}")
                with open(allegato_path, 'wb') as f:
                    if isinstance(movimento['Allegato'], bytes):
                        f.write(movimento['Allegato'])
                    else:
                        # Se è una stringa (dal CSV), prova a convertirla
                        f.write(movimento['Allegato'].encode('latin-1'))
            except Exception as e:
                st.error(f"Errore nel salvataggio dell'allegato {movimento['Allegato Nome']}: {str(e)}")

# --- Funzione per caricare allegati da file separati ---
def carica_allegati_separati(struttura):
    allegati_dir = f"allegati_{struttura.replace(' ', '_')}"
    if not os.path.exists(allegati_dir):
        return
    
    for movimento in st.session_state.dati[struttura]:
        if movimento.get('Allegato Nome') and not movimento.get('Allegato'):
            # Cerca il file allegato corrispondente
            for filename in os.listdir(allegati_dir):
                if filename.startswith(movimento['ID']) and filename.endswith(movimento['Allegato Nome']):
                    try:
                        allegato_path = os.path.join(allegati_dir, filename)
                        with open(allegato_path, 'rb') as f:
                            movimento['Allegato'] = f.read()
                        break
                    except Exception as e:
                        st.error(f"Errore nel caricamento dell'allegato {filename}: {str(e)}")

# --- Funzione per aggiungere/modificare movimento ---
def aggiungi_movimento(data, categoria, dettagli, entrate_pos, incassi_assegni, versamento_assegno, entrate_cash, uscite_cash, allegato, allegato_nome, in_attesa, modifica_idx=None):
    struttura = st.session_state.struttura
    username = st.session_state.username
    saldo_prec = st.session_state.saldo[struttura]
    nuovo_saldo = saldo_prec + (entrate_pos + entrate_cash - uscite_cash)
    if modifica_idx is not None:
        movimento = st.session_state.dati[struttura][modifica_idx]
        movimento.update({
            'Data': data.strftime('%d/%m/%Y'),
            'Categoria': categoria,
            'Dettagli': dettagli,
            'Entrate POS/Bonifico': entrate_pos,
            'Incassi Assegni': incassi_assegni,
            'Versamento Assegno': versamento_assegno,
            'Entrate Cash': entrate_cash,
            'Uscite Cash': uscite_cash,
            'Allegato Nome': allegato_nome,
            'Saldo': nuovo_saldo,
            'In Attesa': in_attesa,
            'Utente': username,
            'Allegato': allegato,
        })
    else:
        nuovo_mov = {
            'ID': str(uuid.uuid4()),
            'Data': data.strftime('%d/%m/%Y'),
            'Categoria': categoria,
            'Dettagli': dettagli,
            'Entrate POS/Bonifico': entrate_pos,
            'Incassi Assegni': incassi_assegni,
            'Versamento Assegno': versamento_assegno,
            'Entrate Cash': entrate_cash,
            'Uscite Cash': uscite_cash,
            'Allegato Nome': allegato_nome,
            'Saldo': nuovo_saldo,
            'In Attesa': in_attesa,
            'Utente': username,
            'Allegato': allegato,
            'Modifiche': []
        }
        st.session_state.dati[struttura].append(nuovo_mov)
    st.session_state.saldo[struttura] = nuovo_saldo
    salva_dati_csv(struttura)

# --- Funzione per migrare allegati esistenti dal CSV ---
def migra_allegati_esistenti(struttura):
    """Migra allegati che potrebbero essere salvati come stringhe nel CSV"""
    allegati_dir = f"allegati_{struttura.replace(' ', '_')}"
    if not os.path.exists(allegati_dir):
        os.makedirs(allegati_dir)
    
    for movimento in st.session_state.dati[struttura]:
        if movimento.get('Allegato Nome') and movimento.get('Allegato'):
            allegato_data = movimento['Allegato']
            # Se l'allegato è una stringa (dal CSV), prova a salvarlo come file
            if isinstance(allegato_data, str) and len(allegato_data) > 0:
                try:
                    allegato_path = os.path.join(allegati_dir, f"{movimento['ID']}_{movimento['Allegato Nome']}")
                    if not os.path.exists(allegato_path):
                        with open(allegato_path, 'wb') as f:
                            f.write(allegato_data.encode('latin-1'))
                        # Rimuovi l'allegato dal movimento per risparmiare memoria
                        movimento['Allegato'] = None
                except Exception as e:
                    st.warning(f"Impossibile migrare l'allegato {movimento['Allegato Nome']}: {str(e)}")

# --- Categorie dinamiche ---
def get_categorie(struttura, uscite_cash=0.0):
    # Se ci sono uscite cash, mostra solo "PAGAMENTO"
    if uscite_cash and uscite_cash > 0:
        return ["PAGAMENTO"]
    
    # Altrimenti, restituisci lista vuota per lasciare il campo vuoto
    return []

# --- Funzione per ottenere tutte le categorie disponibili (per compatibilità) ---
def get_tutte_categorie(struttura):
    base = [
        "PAGAMENTO",
        "VERSAMENTO SEDE",
        "CHIUSURA GIORNALIERA",
        "SALDO TOTALE",
        "SALDO PARZIALE"
    ]
    if struttura == "HOTEL TERRANOBILE":
        base.append("VERSAMENTO BANCA INTESA")
    if struttura == "MASSERIA PIETRASOLE":
        base.append("VERSAMENTO BANCA SELLA")
    return base

# --- Funzione per pulire categorie obsolete ---
def pulisci_categorie_obsolete(struttura):
    """Converte categorie obsolete in categorie valide"""
    categorie_valide = get_tutte_categorie(struttura)
    modifiche_fatte = False
    
    for movimento in st.session_state.dati[struttura]:
        categoria_attuale = movimento.get('Categoria', '')
        uscite_cash = float(movimento.get('Uscite Cash', 0.0))
        
        # Se ci sono uscite cash, la categoria deve essere "PAGAMENTO"
        if uscite_cash > 0:
            if categoria_attuale != 'PAGAMENTO':
                movimento['Categoria'] = 'PAGAMENTO'
                modifiche_fatte = True
        # Se non ci sono uscite cash, mantieni la categoria esistente (non forzare vuoto)
        # L'utente può scegliere la categoria appropriata
    
    if modifiche_fatte:
        # Salva i dati puliti
        salva_dati_csv(struttura)
        return True
    
    return False

# --- Caricamento automatico dati da CSV all'avvio ---
for struttura in STRUTTURE:
    filename = f"dati_{struttura.replace(' ', '_')}.csv"
    if os.path.exists(filename):
        try:
            if os.path.getsize(filename) > 0:
                df = pd.read_csv(filename)
                st.session_state.dati[struttura] = df.fillna('').to_dict(orient='records')
                # Migra allegati esistenti se necessario
                migra_allegati_esistenti(struttura)
                # Carica gli allegati separati
                carica_allegati_separati(struttura)
                # Pulisci categorie obsolete
                if pulisci_categorie_obsolete(struttura):
                    st.info(f"✅ Categorie obsolete pulite per {struttura}")
            else:
                st.session_state.dati[struttura] = []
        except pd.errors.EmptyDataError:
            st.session_state.dati[struttura] = []
    else:
        st.session_state.dati[struttura] = []

# --- Pagina PRINCIPALE: Prima Nota ---
struttura = st.session_state.struttura
movimenti = st.session_state.dati[struttura]
saldo_effettivo, saldo_sospeso = calcola_saldi(movimenti)

# --- Saldi in evidenza ---
st.markdown("""
    <style>
    .big-metric .stMetricValue {
        font-size: 4.4rem !important;
        font-weight: bold;
    }
    .medium-metric .stMetricValue {
        font-size: 2.5rem !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("## Saldi")
col1, col2, col3, col4 = st.columns([2,2,2,1])
with col1:
    st.markdown('<div class="big-metric">', unsafe_allow_html=True)
    st.metric("Saldo Contabile", f"€ {saldo_effettivo:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="medium-metric">', unsafe_allow_html=True)
    st.metric("Saldo Sospeso (in attesa di fattura)", f"€ {saldo_sospeso:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    disponibilita = saldo_effettivo + saldo_sospeso
    st.markdown('<div class="big-metric">', unsafe_allow_html=True)
    st.metric("Disponibilità", f"€ {disponibilita:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
aggiorna = col4.button("🔄 Aggiorna", key="aggiorna_saldi")
if aggiorna:
    saldo_effettivo, saldo_sospeso = calcola_saldi(st.session_state.dati[struttura])
    st.session_state.saldo[struttura] = saldo_effettivo
    st.success("Saldi aggiornati!")
    st.rerun()

# --- Form inserimento/modifica movimento ---
st.subheader(f"Nuovo movimento - {struttura}")
# Precarica dati se in modifica
idx_mod = st.session_state.modifica_idx
movimento_mod = None
if idx_mod is not None and 0 <= idx_mod < len(st.session_state.dati[struttura]):
    movimento_mod = st.session_state.dati[struttura][idx_mod]
else:
    # Reset dell'indice se non è valido
    st.session_state.modifica_idx = None

with st.form(key="form_movimento", clear_on_submit=True):
    col1, col2, col3 = st.columns([1.2,1,1])
    with col1:
        # Gestione sicura della data
        data_default = datetime.now()
        if movimento_mod and movimento_mod.get('Data'):
            try:
                data_default = datetime.strptime(movimento_mod['Data'], '%d/%m/%Y')
            except ValueError:
                # Se la data è malformata, usa la data corrente
                data_default = datetime.now()
        
        data = st.date_input(
            "Data",
            value=data_default,
            format="DD/MM/YYYY"
        )
        
        # Gestione sicura della categoria
        categoria_default = get_tutte_categorie(struttura)[0] if get_tutte_categorie(struttura) else "PAGAMENTO"
        if movimento_mod and movimento_mod.get('Categoria'):
            try:
                categoria_default = movimento_mod['Categoria']
                # Se la categoria non esiste nella lista, usa la prima disponibile
                if categoria_default not in get_tutte_categorie(struttura):
                    categoria_default = get_tutte_categorie(struttura)[0] if get_tutte_categorie(struttura) else "PAGAMENTO"
            except (ValueError, IndexError):
                categoria_default = get_tutte_categorie(struttura)[0] if get_tutte_categorie(struttura) else "PAGAMENTO"
        
        categoria = st.selectbox(
            "Categoria",
            get_tutte_categorie(struttura),
            index=get_tutte_categorie(struttura).index(categoria_default) if categoria_default in get_tutte_categorie(struttura) else 0
        )
        dettagli = st.text_input("Dettagli", value=movimento_mod.get('Dettagli', '') if movimento_mod else "")
    with col2:
        entrate_pos = st.number_input("Entrate POS/Bonifico", value=float(movimento_mod.get('Entrate POS/Bonifico', 0.0)) if movimento_mod else None, step=0.01, format="%0.2f", key="pos", help="Importo POS/Bonifico", label_visibility="visible")
        incassi_assegni = st.number_input("Incassi Assegni", value=float(movimento_mod.get('Incassi Assegni', 0.0)) if movimento_mod else None, step=0.01, format="%0.2f", key="assegni", help="Importo assegni", label_visibility="visible")
        versamento_assegno = st.number_input("Versamento Assegno", value=float(movimento_mod.get('Versamento Assegno', 0.0)) if movimento_mod else None, step=0.01, format="%0.2f", key="versamento_assegno", help="Importo versamento assegno", label_visibility="visible")
    with col3:
        entrate_cash = st.number_input("Entrate Cash", value=float(movimento_mod.get('Entrate Cash', 0.0)) if movimento_mod else None, step=0.01, format="%0.2f", key="cash", help="Importo contanti", label_visibility="visible")
        uscite_cash = st.number_input("Uscite Cash", value=float(movimento_mod.get('Uscite Cash', 0.0)) if movimento_mod else None, step=0.01, format="%0.2f", key="uscite_cash", help="Uscite contanti", label_visibility="visible")
        allegato = st.file_uploader("Allega fattura (PDF o immagine)", type=["pdf", "jpg", "jpeg", "png"])
        st.markdown('<div style="margin-top: 8px; margin-bottom: 8px;"><label style="color: red; font-weight: bold;">In attesa di fattura</label></div>', unsafe_allow_html=True)
        in_attesa = st.checkbox("Spunta se in attesa di fattura", value=movimento_mod.get('In Attesa', False) if movimento_mod else False, key="in_attesa_checkbox", label_visibility="collapsed")
    
    # Gestione automatica della categoria in base alle uscite cash
    uscite_cash_val = 0.0 if uscite_cash is None else float(uscite_cash)
    categorie_disponibili = get_categorie(struttura, uscite_cash_val)
    
    # Se ci sono uscite cash, forza la categoria a "PAGAMENTO"
    if uscite_cash_val > 0:
        categoria_finale = "PAGAMENTO"
        st.info("💡 Categoria automaticamente impostata a 'PAGAMENTO' per le uscite cash")
    else:
        # Se non ci sono uscite cash, permetti all'utente di scegliere la categoria
        categoria_finale = categoria  # Usa la categoria scelta dall'utente
    
    submitted = st.form_submit_button("Registra Movimento" if idx_mod is None else "Salva Modifica")
    if submitted:
        allegato_bytes = allegato.read() if allegato else (movimento_mod.get('Allegato') if movimento_mod else None)
        allegato_nome = allegato.name if allegato else (movimento_mod.get('Allegato Nome') if movimento_mod else None)
        
        # Gestisci i valori None dai campi numerici
        entrate_pos = 0.0 if entrate_pos is None else float(entrate_pos)
        incassi_assegni = 0.0 if incassi_assegni is None else float(incassi_assegni)
        versamento_assegno = 0.0 if versamento_assegno is None else float(versamento_assegno)
        entrate_cash = 0.0 if entrate_cash is None else float(entrate_cash)
        uscite_cash = 0.0 if uscite_cash is None else float(uscite_cash)
        
        # Usa la categoria finale determinata automaticamente
        aggiungi_movimento(data, categoria_finale, dettagli, entrate_pos, incassi_assegni, versamento_assegno, entrate_cash, uscite_cash, allegato_bytes, allegato_nome, in_attesa, idx_mod)
        st.session_state.modifica_idx = None
        st.success("Movimento registrato!" if idx_mod is None else "Movimento modificato!")
        st.rerun()

# --- Funzione per importare dati da Excel ---
def import_excel(file, struttura):
    """Importa dati da file Excel che segue la struttura della tabella"""
    try:
        # Leggi il file Excel
        df = pd.read_excel(file, sheet_name='Movimenti')
        
        # Verifica che le colonne necessarie siano presenti
        colonne_richieste = ['Data', 'Categoria', 'Dettagli', 'Entrate POS/Bonifico', 'Incassi Assegni', 
                           'Versamento Assegno', 'Entrate Cash', 'Uscite Cash', 'In Attesa']
        
        colonne_mancanti = [col for col in colonne_richieste if col not in df.columns]
        if colonne_mancanti:
            return False, f"Colonne mancanti nel file Excel: {', '.join(colonne_mancanti)}"
        
        # Converti DataFrame in lista di dizionari
        movimenti_importati = []
        for _, row in df.iterrows():
            # Gestione data - converte da Excel format a DD/MM/YYYY
            data_excel = row['Data']
            data_formattata = ''
            
            if pd.notna(data_excel):
                try:
                    # Se è già una stringa nel formato DD/MM/YYYY
                    if isinstance(data_excel, str) and '/' in data_excel:
                        # Se contiene anche l'ora, prendi solo la parte della data
                        if ' ' in data_excel:
                            data_excel = data_excel.split(' ')[0]
                        data_formattata = data_excel
                    else:
                        # Se è un datetime di pandas/Excel, converti in DD/MM/YYYY
                        if hasattr(data_excel, 'strftime'):
                            data_formattata = data_excel.strftime('%d/%m/%Y')
                        else:
                            # Prova a parsare come stringa e rimuovi l'ora se presente
                            data_str = str(data_excel)
                            if ' ' in data_str:
                                data_str = data_str.split(' ')[0]
                            # Se è in formato YYYY-MM-DD, converti in DD/MM/YYYY
                            if '-' in data_str and len(data_str.split('-')[0]) == 4:
                                try:
                                    dt = datetime.strptime(data_str, '%Y-%m-%d')
                                    data_formattata = dt.strftime('%d/%m/%Y')
                                except:
                                    data_formattata = data_str
                            else:
                                data_formattata = data_str
                except Exception:
                    data_formattata = str(data_excel)
            
            # Genera ID univoco per ogni movimento
            movimento = {
                'ID': str(uuid.uuid4()),
                'Data': data_formattata,
                'Categoria': str(row['Categoria']) if pd.notna(row['Categoria']) else '',
                'Dettagli': str(row['Dettagli']) if pd.notna(row['Dettagli']) else '',
                'Entrate POS/Bonifico': float(row['Entrate POS/Bonifico']) if pd.notna(row['Entrate POS/Bonifico']) else 0.0,
                'Incassi Assegni': float(row['Incassi Assegni']) if pd.notna(row['Incassi Assegni']) else 0.0,
                'Versamento Assegno': float(row['Versamento Assegno']) if pd.notna(row['Versamento Assegno']) else 0.0,
                'Entrate Cash': float(row['Entrate Cash']) if pd.notna(row['Entrate Cash']) else 0.0,
                'Uscite Cash': float(row['Uscite Cash']) if pd.notna(row['Uscite Cash']) else 0.0,
                'In Attesa': bool(row['In Attesa']) if pd.notna(row['In Attesa']) else False,
                'Allegato Nome': str(row.get('Allegato Nome', '')) if pd.notna(row.get('Allegato Nome', '')) else '',
                'Utente': str(row.get('Utente', 'IMPORT')) if pd.notna(row.get('Utente', 'IMPORT')) else 'IMPORT',
                'Saldo': 0.0,  # Verrà ricalcolato
                'Allegato': None,  # Gli allegati non possono essere importati da Excel
                'Modifiche': []
            }
            movimenti_importati.append(movimento)
        
        # Sostituisci i dati esistenti con quelli importati
        st.session_state.dati[struttura] = movimenti_importati
        
        # Ricalcola i saldi
        saldo_effettivo, saldo_sospeso = calcola_saldi(movimenti_importati)
        st.session_state.saldo[struttura] = saldo_effettivo
        
        # Salva i dati
        salva_dati_csv(struttura)
        
        return True, f"Importati {len(movimenti_importati)} movimenti con successo!"
        
    except Exception as e:
        return False, f"Errore nell'importazione: {str(e)}"

# --- Funzione per parsare date in vari formati ---
def parse_date_safe(date_str):
    """Parsa una data in vari formati possibili"""
    if not date_str or pd.isna(date_str):
        return datetime(1900, 1, 1)
    
    # Rimuovi spazi extra
    date_str = str(date_str).strip()
    
    # Se contiene l'ora, prendi solo la parte della data
    if ' ' in date_str:
        date_str = date_str.split(' ')[0]
    
    # Prova diversi formati
    formats = [
        '%d/%m/%Y',      # DD/MM/YYYY
        '%Y-%m-%d',      # YYYY-MM-DD
        '%d-%m-%Y',      # DD-MM-YYYY
        '%Y/%m/%d',      # YYYY/MM/DD
        '%d/%m/%y',      # DD/MM/YY
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Se nessun formato funziona, ritorna una data di default
    return datetime(1900, 1, 1)

# --- Filtro ricerca e filtro mese ---
st.subheader(f"Registro Movimenti - {struttura}")

# Layout per i filtri
col_filtri1, col_filtri2, col_filtri3, col_pulisci = st.columns([1, 1, 1, 0.5])

with col_filtri1:
    filtro_attesa = st.checkbox("🔍 Solo in attesa", help="Mostra solo movimenti in attesa di fattura")

with col_filtri2:
    search_text = st.text_input("🔎 Cerca", placeholder="Testo libero...", help="Cerca in data, categoria, dettagli, utente")

with col_filtri3:
    filtro_mese = st.selectbox(
        "📅 Filtra mese",
        options=["Tutti"] + [f"{m:02d}/2025" for m in range(1, 13)] + [f"{m:02d}/2026" for m in range(1, 13)],
        help="Filtra per mese specifico"
    )

with col_pulisci:
    if st.button("🗑️ Pulisci", help="Rimuovi tutti i filtri"):
        st.rerun()

dati = st.session_state.dati[struttura].copy()  # Copia per non modificare l'originale

# Filtro "In Attesa"
if filtro_attesa:
    dati = [m for m in dati if m.get('In Attesa') is True]

# Filtro mese - CORRETTO
if filtro_mese != "Tutti":
    mese, anno = filtro_mese.split("/")
    dati_filtrati = []
    for m in dati:
        data_movimento = m.get('Data', '')
        if data_movimento:
            try:
                # Estrai mese e anno dalla data (formato DD/MM/YYYY)
                parti_data = data_movimento.split('/')
                if len(parti_data) == 3:
                    giorno, mese_mov, anno_mov = parti_data
                    if mese_mov == mese and anno_mov == anno:
                        dati_filtrati.append(m)
            except Exception:
                continue  # Salta movimenti con date malformate
    dati = dati_filtrati

# Filtro ricerca testo - MIGLIORATO
if search_text and search_text.strip():
    search_lower = search_text.lower().strip()
    dati_filtrati = []
    for m in dati:
        # Cerca solo nei campi rilevanti per la ricerca
        campi_ricerca = [
            str(m.get('Data', '')),
            str(m.get('Categoria', '')),
            str(m.get('Dettagli', '')),
            str(m.get('Utente', ''))
        ]
        # Verifica se il testo di ricerca è presente in almeno uno dei campi
        if any(search_lower in campo.lower() for campo in campi_ricerca):
            dati_filtrati.append(m)
    dati = dati_filtrati

# Ordinamento per data - SEMPRE DEFINITO (DECRESCENTE)
try:
    dati_sorted = sorted(dati, key=lambda x: parse_date_safe(x.get('Data', '01/01/1900')), reverse=True)
except Exception as e:
    st.warning(f"⚠️ Errore nell'ordinamento per data: {str(e)}")
    dati_sorted = dati

# Sezione Import Excel
st.markdown("---")
st.subheader("📥 Importa dati da Excel")
st.info("Carica un file Excel che segue la struttura della tabella. Le colonne devono essere: Data, Categoria, Dettagli, Entrate POS/Bonifico, Incassi Assegni, Versamento Assegno, Entrate Cash, Uscite Cash, In Attesa")

uploaded_file = st.file_uploader("Seleziona file Excel", type=['xlsx', 'xls'], help="File Excel con struttura compatibile")

if uploaded_file is not None:
    col_import, col_preview = st.columns([1, 2])
    
    with col_import:
        if st.button("📥 Importa dati", type="primary"):
            success, message = import_excel(uploaded_file, struttura)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with col_preview:
        try:
            df_preview = pd.read_excel(uploaded_file, sheet_name='Movimenti', nrows=5)
            st.write("**Anteprima dei dati:**")
            st.dataframe(df_preview, use_container_width=True)
        except Exception as e:
            st.error(f"Errore nella lettura del file: {str(e)}")

if not dati:
    st.info("Nessun movimento trovato con i filtri applicati.")
else:
    # Mostra statistiche dei filtri applicati e pulsanti export
    if filtro_attesa or filtro_mese != "Tutti" or search_text:
        col_stats, col_export_excel, col_export_pdf, col_export_csv = st.columns([2, 1, 1, 1])
        with col_stats:
            st.info(f"📊 Mostrando {len(dati)} movimenti su {len(st.session_state.dati[struttura])} totali")
        with col_export_excel:
            if st.button("📊 Excel", help="Esporta in Excel"):
                excel_data = export_excel(dati_sorted, struttura)
                if excel_data:
                    st.download_button(
                        label="💾 Scarica Excel",
                        data=excel_data,
                        file_name=f"prima_nota_{struttura.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        with col_export_pdf:
            if st.button("📄 PDF", help="Esporta in PDF"):
                pdf_data = export_pdf(dati_sorted, struttura)
                if pdf_data:
                    st.download_button(
                        label="💾 Scarica PDF",
                        data=pdf_data,
                        file_name=f"prima_nota_{struttura.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
        with col_export_csv:
            if st.button("📥 CSV", help="Esporta in CSV"):
                # Crea DataFrame per l'export (senza allegati)
                df_export = pd.DataFrame([{k: v for k, v in m.items() if k not in ['Allegato', 'Modifiche']} for m in dati_sorted])
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica CSV",
                    data=csv,
                    file_name=f"movimenti_{struttura.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        # Se non ci sono filtri, mostra solo i pulsanti export
        col_export_excel, col_export_pdf, col_export_csv = st.columns(3)
        with col_export_excel:
            if st.button("📊 Excel", help="Esporta in Excel"):
                excel_data = export_excel(dati_sorted, struttura)
                if excel_data:
                    st.download_button(
                        label="💾 Scarica Excel",
                        data=excel_data,
                        file_name=f"prima_nota_{struttura.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        with col_export_pdf:
            if st.button("📄 PDF", help="Esporta in PDF"):
                pdf_data = export_pdf(dati_sorted, struttura)
                if pdf_data:
                    st.download_button(
                        label="💾 Scarica PDF",
                        data=pdf_data,
                        file_name=f"prima_nota_{struttura.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
        with col_export_csv:
            if st.button("📥 CSV", help="Esporta in CSV"):
                # Crea DataFrame per l'export (senza allegati)
                df_export = pd.DataFrame([{k: v for k, v in m.items() if k not in ['Allegato', 'Modifiche']} for m in dati_sorted])
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="💾 Scarica CSV",
                    data=csv,
                    file_name=f"movimenti_{struttura.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# Crea DataFrame per la tabella
df = pd.DataFrame([{k: v for k, v in m.items() if k not in ['Allegato', 'Modifiche']} for m in dati_sorted])
df.reset_index(drop=True, inplace=True)

# Configurazione tabella AgGrid - APPLICATA A TUTTE LE STRUTTURE
gb = GridOptionsBuilder.from_dataframe(df)

# Configurazione colonne con autosize
gb.configure_column('ID', hide=True)  # Nascondo completamente la colonna ID
gb.configure_column('Data', autoHeight=False, wrapText=False, headerCheckboxSelection=True, checkboxSelection=True, sortable=True, pinned='left', suppressSizeToFit=False, flex=1)
gb.configure_column('Categoria', autoHeight=False, wrapText=False, sortable=False, pinned='left', suppressSizeToFit=False, flex=1.5)
gb.configure_column('Dettagli', autoHeight=False, wrapText=False, sortable=False, pinned='left', suppressSizeToFit=False, flex=2)
gb.configure_column('Entrate POS/Bonifico', width=120, type=['numericColumn'], format='€ #,##0.00', sortable=False)
gb.configure_column('Incassi Assegni', width=120, type=['numericColumn'], format='€ #,##0.00', sortable=False)
gb.configure_column('Versamento Assegno', width=120, type=['numericColumn'], format='€ #,##0.00', sortable=False)
gb.configure_column('Entrate Cash', width=120, type=['numericColumn'], format='€ #,##0.00', sortable=False)
gb.configure_column('Uscite Cash', width=120, type=['numericColumn'], format='€ #,##0.00', sortable=False)
gb.configure_column('In Attesa', editable=True, cellEditor='agCheckboxCellEditor', cellRenderer='agCheckboxCellRenderer', width=80, sortable=False)
gb.configure_column('Allegato Nome', editable=False, width=150, autoHeight=False, wrapText=False, sortable=False)
gb.configure_column('Note', hide=True)
gb.configure_column('Utente', width=100, autoHeight=False, wrapText=False, sortable=False)
gb.configure_column('Saldo', hide=True)

# Configurazione generale della tabella
gb.configure_selection('single', use_checkbox=True, pre_selected_rows=[])
gb.configure_grid_options(
    domLayout='normal',
    rowHeight=40,  # Ripristinato a 40
    headerHeight=40,  # Ripristinato a 40
    suppressRowClickSelection=True,
    enableCellTextSelection=True,
    ensureDomOrder=True,
    # Abilita autosize automatico
    suppressColumnVirtualisation=True,
    suppressRowVirtualisation=True,
    # Abilita menu di ordinamento
    suppressMenuHide=False,
    # Configurazione per colonne flessibili
    suppressColumnMoveAnimation=True,
    suppressRowHoverHighlight=False,
    # Forza ordinamento iniziale per data (DECRESCENTE)
    defaultSortModel=[{'colId': 'Data', 'sort': 'desc'}]
)

grid_options = gb.build()

# Visualizzazione tabella
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=500,
    theme='streamlit',
    reload_data=True,
    enable_enterprise_modules=False,
    data_return_mode='AS_INPUT',
    custom_css={
        ".ag-theme-streamlit": {
            "font-size": "16px",
            "font-family": "Arial, sans-serif"
        },
        ".ag-theme-streamlit .ag-cell": {
            "padding": "6px 8px",  # Padding normale
            "line-height": "1.2",  # Line-height normale
            "white-space": "nowrap",  # No word-wrap
            "font-size": "16px"  # Font aumentato
        },
        ".ag-theme-streamlit .ag-header-cell": {
            "font-weight": "bold",
            "background-color": "#f0f2f6",
            "font-size": "16px"
        }
    }
)

# Aggiorno il flag 'In Attesa' usando l'ID univoco e mostro messaggio di conferma
flag_changed = False
if grid_response['data'] is not None:
    for _, row in grid_response['data'].iterrows():
        for m in st.session_state.dati[struttura]:
            if m['ID'] == row['ID']:
                if m['In Attesa'] != row['In Attesa']:
                    m['In Attesa'] = row['In Attesa']
                    flag_changed = True
                break
if flag_changed:
    st.success("Stato 'In attesa di fattura' aggiornato con successo!")
    saldo_effettivo, saldo_sospeso = calcola_saldi(st.session_state.dati[struttura])
    salva_dati_csv(struttura)

# Azioni su riga selezionata - PULSANTI SOPRA LA TABELLA
selected = grid_response['selected_rows']
if selected is not None and len(selected) > 0:
    if isinstance(selected, list):
        sel_row = selected[0]
    elif hasattr(selected, 'iloc'):
        sel_row = selected.iloc[0]
    else:
        sel_row = {}

    if isinstance(sel_row, dict):
        selected_id = sel_row.get('ID', None)
        data_val = sel_row.get('Data', '')
        cat_val = sel_row.get('Categoria', '')
        det_val = sel_row.get('Dettagli', '')
    else:
        selected_id = sel_row['ID'] if 'ID' in sel_row else None
        data_val = sel_row['Data'] if 'Data' in sel_row else ''
        cat_val = sel_row['Categoria'] if 'Categoria' in sel_row else ''
        det_val = sel_row['Dettagli'] if 'Dettagli' in sel_row else ''

    st.markdown('---')
    st.info(f"Riga selezionata: {data_val} - {cat_val} - {det_val}")
    
    # Trova il movimento corrispondente per verificare se ha allegati
    movimento_selezionato = None
    for m in st.session_state.dati[struttura]:
        if m['ID'] == selected_id:
            movimento_selezionato = m
            break
    
    # Determina il numero di colonne in base alla presenza di allegati
    if movimento_selezionato and movimento_selezionato.get('Allegato Nome'):
        col_mod, col_del, col_attach = st.columns(3)
        has_attachment = True
    else:
        col_mod, col_del = st.columns(2)
        has_attachment = False
    
    with col_mod:
        if st.button('✏️ Modifica riga selezionata', key='modifica_riga'):
            for idx, m in enumerate(st.session_state.dati[struttura]):
                if m['ID'] == selected_id:
                    st.session_state.modifica_idx = idx
                    st.session_state.show_modale_modifica = True
                    st.rerun()
    
    with col_del:
        if st.button('🗑️ Elimina riga selezionata', key='elimina_riga'):
            for idx, m in enumerate(st.session_state.dati[struttura]):
                if m['ID'] == selected_id:
                    st.session_state.dati[struttura].pop(idx)
                    salva_dati_csv(struttura)
                    st.rerun()
    
    # Pulsante per scaricare allegato (solo se presente)
    if has_attachment:
        with col_attach:
            if movimento_selezionato.get('Allegato'):
                try:
                    # Verifica che l'allegato sia effettivamente bytes
                    allegato_data = movimento_selezionato['Allegato']
                    if not isinstance(allegato_data, bytes):
                        # Se non è bytes, prova a caricarlo dal file separato
                        allegati_dir = f"allegati_{struttura.replace(' ', '_')}"
                        allegato_path = os.path.join(allegati_dir, f"{movimento_selezionato['ID']}_{movimento_selezionato['Allegato Nome']}")
                        if os.path.exists(allegato_path):
                            with open(allegato_path, 'rb') as f:
                                allegato_data = f.read()
                                movimento_selezionato['Allegato'] = allegato_data  # Aggiorna in memoria
                        else:
                            st.error(f"⚠️ Allegato '{movimento_selezionato['Allegato Nome']}' non trovato")
                            allegato_data = None
                    
                    # Procedi solo se abbiamo i dati dell'allegato
                    if allegato_data:
                        # Determina il MIME type corretto basato sull'estensione
                        allegato_nome = movimento_selezionato['Allegato Nome']
                        if allegato_nome.lower().endswith('.pdf'):
                            mime_type = "application/pdf"
                        elif allegato_nome.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif allegato_nome.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        else:
                            mime_type = "application/octet-stream"
                        
                        st.download_button(
                            label=f"📎 Scarica {allegato_nome}",
                            data=BytesIO(allegato_data),
                            file_name=allegato_nome,
                            mime=mime_type,
                            key=f"allegato_selezionato_{selected_id}"
                        )
                except Exception as e:
                    st.error(f"❌ Errore nel caricamento dell'allegato {movimento_selezionato.get('Allegato Nome', 'sconosciuto')}: {str(e)}")
            else:
                st.warning(f"⚠️ Allegato '{movimento_selezionato['Allegato Nome']}' non disponibile")
        
        # Visualizzazione tabella
        st.markdown('---')
        # Rimuovo la sezione di visualizzazione allegati e note sotto la tabella
        # Ora vengono mostrati solo quando una riga è selezionata 