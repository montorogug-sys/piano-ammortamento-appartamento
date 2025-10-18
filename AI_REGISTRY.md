# 🤖 AI Registry - Piano Ammortamento Appartamento

**Documento per AI Assistant**
**Ultima modifica:** 18 Ottobre 2025
**Versione app:** 2.1

---

## 📋 Indice

1. [Panoramica Applicazione](#panoramica-applicazione)
2. [Struttura File e Directory](#struttura-file-e-directory)
3. [Architettura Codice](#architettura-codice)
4. [Come Modificare l'App](#come-modificare-lapp)
5. [Deployment](#deployment)
6. [Gestione Dati](#gestione-dati)
7. [Funzionalità Principali](#funzionalità-principali)
8. [Troubleshooting Comune](#troubleshooting-comune)

---

## 📖 Panoramica Applicazione

### Scopo
Applicazione web per gestione piano ammortamento appartamento tra privati (Guglielmo = Creditore, Mattia = Debitore).

### Tecnologie
- **Framework:** Streamlit 1.50.0
- **Python:** 3.11+
- **PDF Generation:** ReportLab 4.4.4
- **Charts:** Matplotlib 3.10.7
- **Data:** Pandas 2.3.3
- **Email:** smtplib (built-in)

### Caratteristiche
- Ammortamento italiano (quota capitale costante)
- Tasso fisso 2% annuo
- Sistema bifase bonifici (eseguito → verificato)
- Email automatiche con cedolini PDF
- Doppio ruolo: Creditore e Debitore

---

## 📁 Struttura File e Directory

```
Piano_ammortamento_appartamento/
├── app.py                      # Applicazione principale (2100+ righe)
├── requirements.txt            # Dipendenze Python
├── .gitignore                  # File esclusi da git
├── .streamlit/
│   └── config.toml            # Configurazione Streamlit Cloud
├── data/
│   └── ammortamento_data.json # Database principale (JSON)
├── reports/
│   └── report_ammortamento_*.pdf  # Report completi
├── cedolini/
│   ├── ricevuta_*.pdf         # Ricevute rate
│   ├── cedolino_bonifico_eseguito_*.pdf
│   └── cedolino_bonifico_verificato_*.pdf
├── README.md                   # Documentazione utente
├── ISTRUZIONI.md              # Guida completa utilizzo
├── CONFIGURAZIONE_EMAIL.md    # Setup email SMTP
├── CHANGELOG_EMAIL_FEATURE.md # Changelog feature email
├── ACCESSO_REMOTO.md          # Istruzioni accesso remoto
└── AI_REGISTRY.md             # Questo file

DATI SENSIBILI (in .gitignore):
- data/ammortamento_data.json
- cedolini/*.pdf
- reports/*.pdf
```

---

## 🏗️ Architettura Codice

### app.py - Struttura Principale

**Righe 1-100: Import e Costanti**
- Import librerie
- Configurazione Streamlit (`st.set_page_config`)

**Righe 30-60: Inizializzazione Dati (`init_data()`)**
- Struttura JSON default
- Parametri finanziamento
- Email, IBAN, SMTP

**Righe 100-280: Funzioni Calcolo**
- `calcola_piano_ammortamento_italiano()` - Piano rate
- `calcola_capitale_effettivo()` - Capitale - spese ripristino
- `calcola_capitale_residuo()` - Capitale rimanente
- `calcola_durata_effettiva()` - Durata con rate saltate

**Righe 280-550: Generazione PDF**
- `crea_grafico_evoluzione_ammortamento()` - Grafico area
- `crea_grafico_torta_composizione()` - Grafico torta
- `genera_pdf_report_completo()` - Report completo PDF
- `genera_cedolino_rata()` - Cedolino singola rata

**Righe 875-972: Cedolini Bonifico**
- `genera_cedolino_bonifico()` - Cedolini eseguito/verificato
  - stato="eseguito" → Verde
  - stato="verificato" → Blu

**Righe 974-1016: Email**
- `invia_email_con_allegato()` - Invio email SMTP
  - Server: data['smtp_server']
  - Porta: data['smtp_port']
  - Autenticazione: smtp_email, smtp_password
  - Allegati: PDF cedolini

**Righe 1050-1100: Login e Ruoli**
- `check_password()` - Autenticazione utenti
  - Guglielmo: `guglielmo2025`
  - Mattia: `mattia2025`
- `st.session_state['role']` = "creditore" | "debitore"

**Righe 1227-1330: Dashboard (Tab 1)**
- Metriche finanziarie
- Barra progresso
- Piano ammortamento (tabelle)
- ~~Grafici~~ (RIMOSSI il 18/10/2025)

**Righe 1331-1600: Tab 2 - Registra Pagamento (Mattia)**
- Form bonifico con IBAN e causale
- Salvataggio pagamento con `confermato: false`
- Generazione cedolino "eseguito"
- Invio email automatica

**Righe 1600-1850: Tab 2 - Gestione Rate (Guglielmo)**
- Visualizzazione rate in attesa
- Dettagli bonifico (IBAN, causale)
- Pulsante "Verifica e Conferma Bonifico"
- Generazione cedolino "verificato"
- Invio email conferma

**Righe 1850-2050: Tab Configurazione (Guglielmo)**
- Parametri finanziamento
- Email e IBAN
- SMTP Gmail (server, porta, email, password)
- Spese ripristino

**Righe 2050-2150: Tab Storico**
- **SEZIONE DOWNLOAD (aggiunta 18/10/2025):**
  - Finestra 1: Lista cedole con download singolo
  - Finestra 2: Download prospetto PDF
- Generazione cedolini individuali
- Tabella pagamenti confermati
- Calcolo saldo anticipato

**Righe 2057-2100: Tab Impostazioni (Mattia)**
- Modifica email personale
- Modifica IBAN personale
- Visualizzazione dati Guglielmo (read-only)

---

## 🛠️ Come Modificare l'App

### Aggiungere un Nuovo Tab

1. **Modifica dichiarazione tabs** (righe ~1080 o ~1082):
```python
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([...])
```

2. **Aggiungi contenuto tab**:
```python
with tab6:
    st.header("Nuovo Tab")
    # ... codice ...
```

### Modificare la Dashboard

**Linee 1227-1330** - Dashboard principale

**Per aggiungere metriche:**
```python
col1, col2, col3, col4, col5 = st.columns(5)
col5.metric("Nuova Metrica", valore)
```

**Per rimuovere grafici:** (già fatto)
- Commentare/eliminare righe 1330-1398

### Modificare Cedolini/PDF

**Funzione `genera_cedolino_bonifico()`** - Linea 875

**Cambiare colori:**
- Verde eseguito: `#4caf50`
- Blu verificato: `#2196f3`

**Aggiungere campi:**
```python
p.drawString(100, y_pos, f"Nuovo campo: {valore}")
y_pos -= 20
```

### Modificare Email

**Funzione `invia_email_con_allegato()`** - Linea 974

**Cambiare oggetto/corpo:**
```python
oggetto = "Nuovo oggetto email"
corpo = """<html><body>HTML personalizzato</body></html>"""
```

**Aggiungere destinatari CC/BCC:**
```python
msg['Cc'] = "email@example.com"
```

### Cambiare Password Utenti

**Linea 137-146** - Funzione `check_password()`

```python
if utente == "Mattia (Debitore)" and password == "NUOVA_PASSWORD_MATTIA":
    st.session_state['role'] = "debitore"
    return True
elif utente == "Guglielmo (Creditore)" and password == "NUOVA_PASSWORD_GUGLIELMO":
    st.session_state['role'] = "creditore"
    return True
```

### Modificare Calcoli Finanziari

**Funzione `calcola_piano_ammortamento_italiano()`** - Linea ~100

**Formula ammortamento italiano:**
- Quota capitale = Capitale / Durata (costante)
- Quota interessi = Debito residuo * (Tasso / 12)
- Rata = Quota capitale + Quota interessi

**Per cambiare tipo ammortamento:**
- Ammortamento francese: rata costante
- Ammortamento americano: solo interessi, capitale alla fine

---

## 🚀 Deployment

### Opzione 1: Ngrok (Dati Persistenti - CONSIGLIATO)

**URL attuale:** https://interzooecial-configurational-mallory.ngrok-free.dev

**Requisiti:**
- Mac acceso
- Streamlit in esecuzione
- Ngrok attivo

**Avviare:**
```bash
# Terminale 1: Streamlit
cd "/Users/guglielmo/Documents/Archivio Guglielmo/PythonSoft/Piano_ammortamento_appartamento"
streamlit run app.py

# Terminale 2: Ngrok
ngrok http 8501
```

**Verificare tunnel:**
```bash
curl -s http://localhost:4040/api/tunnels | python3 -m json.tool
```

**Fermare:**
```bash
pkill ngrok
pkill streamlit  # (opzionale, se vuoi fermare anche streamlit)
```

**Vantaggi:**
- ✅ Dati persistenti (salvati su Mac)
- ✅ Aggiornamenti istantanei
- ✅ Backup facile

**Svantaggi:**
- ⚠️ Richiede Mac acceso
- ⚠️ URL può cambiare se ngrok viene riavviato

---

### Opzione 2: Streamlit Cloud (Demo/Test)

**URL attuale:** https://piano-ammortamento-appartamento-jxrz72g7px4kxh3dslfo4c.streamlit.app

**Repository GitHub:** https://github.com/montorogug-sys/piano-ammortamento-appartamento

**Procedura aggiornamento:**

1. **Modifica codice sul Mac**
2. **Commit e push:**
```bash
cd "/Users/guglielmo/Documents/Archivio Guglielmo/PythonSoft/Piano_ammortamento_appartamento"
git add .
git commit -m "Descrizione modifiche"
git push origin main
```

3. **Streamlit Cloud rileva automaticamente** (1-2 minuti)

**Vantaggi:**
- ✅ Sempre online
- ✅ Link permanente
- ✅ Nessuna manutenzione

**Svantaggi:**
- ❌ Dati si RESETTANO ad ogni deploy
- ❌ Solo per test/demo
- ⚠️ Usare Chrome (Safari ha problemi)

**Cache browser:**
Se l'app non si aggiorna correttamente:
```
Mac: Cmd + Shift + R
Windows: Ctrl + Shift + F5
```

---

## 💾 Gestione Dati

### File JSON Principale

**Path:** `data/ammortamento_data.json`

**Struttura:**
```json
{
  "capitale_iniziale": 80000.0,
  "durata_mesi": 267,
  "durata_originale": 267,
  "tasso_annuo": 2.0,
  "tipo_ammortamento": "italiano",
  "rata_target": 300.0,
  "configurato": true,

  "email_guglielmo": "email@gmail.com",
  "email_mattia": "email@gmail.com",
  "iban_guglielmo": "IT...",
  "iban_mattia": "IT...",

  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_email": "email@gmail.com",
  "smtp_password": "app_password_16_caratteri",

  "costi_manutenzione": [
    {"descrizione": "...", "importo": 1000.0, "categoria": "..."}
  ],

  "pagamenti": [
    {
      "data": "2025-10-15",
      "importo": 300.0,
      "numero_rata": 1,
      "note": "...",
      "causale": "Rata 1 - Piano Ammortamento Appartamento",
      "iban_mittente": "IT...",
      "iban_beneficiario": "IT...",
      "confermato": true,
      "data_verifica": "2025-10-18",
      "registrato_da": "Mattia",
      "timestamp": "2025-10-15T10:30:00"
    }
  ],

  "versamenti_straordinari": [],
  "rate_saltate": []
}
```

### Funzioni I/O

**Lettura:**
```python
data = carica_dati()  # Linea ~1020
```

**Scrittura:**
```python
salva_dati(data)  # Linea ~1030
```

### Backup Manuale

```bash
cp data/ammortamento_data.json data/backup_$(date +%Y%m%d_%H%M%S).json
```

---

## ⚙️ Funzionalità Principali

### Sistema Bifase Bonifici

**Fase 1: Eseguito (Mattia)**
1. Mattia fa bonifico bancario
2. Registra in app: data, importo, IBAN, causale
3. Sistema:
   - Salva con `confermato: false`
   - Genera cedolino "BONIFICO ESEGUITO" (verde)
   - Invia email a entrambi con allegato

**Fase 2: Verificato (Guglielmo)**
1. Guglielmo controlla arrivo su conto corrente
2. Verifica dettagli in app
3. Click "Verifica e Conferma Bonifico"
4. Sistema:
   - Aggiorna con `confermato: true`, `data_verifica`
   - Genera cedolino "BONIFICO VERIFICATO" (blu)
   - Genera report completo aggiornato
   - Invia email a entrambi

### Email Automatiche

**Configurazione SMTP Gmail:**
1. Attiva autenticazione 2FA su Google
2. Genera App Password: https://myaccount.google.com/apppasswords
3. Inserisci in app (tab Configurazione):
   - Email SMTP
   - App Password (16 caratteri senza spazi)
   - Server: smtp.gmail.com
   - Porta: 587

**Email inviate:**
- Bonifico eseguito → Guglielmo + Mattia
- Bonifico verificato → Guglielmo + Mattia

### Cedolini PDF

**Tipi:**
1. `ricevuta_[DATA]_[RATA].pdf` - Ricevuta generica
2. `cedolino_bonifico_eseguito_[DATA]_[RATA].pdf` - Mattia registra
3. `cedolino_bonifico_verificato_[DATA]_[RATA].pdf` - Guglielmo verifica

**Generazione:**
- ReportLab con canvas
- Font Helvetica
- Dimensioni A4
- Colori differenziati per stato

### Download Storico

**Finestra 1 - Cedole (18/10/2025):**
- Lista tutte le cedole ordinate
- Download singolo per ogni cedola
- Pulsante ⬇️ per ognuna

**Finestra 2 - Prospetto:**
- Genera piano ammortamento aggiornato
- Download PDF completo

---

## 🐛 Troubleshooting Comune

### PDF "Cannot open resource"

**Problema:** Temp file grafici cancellati prima della lettura

**Soluzione:** (già implementata linee 633-670)
- Salvare percorsi file temp in variabili
- Creare `Image()` objects
- Chiamare `doc.build()`
- Eliminare temp files DOPO build

### Email non partono

**Cause:**
1. App Password errata
2. 2FA non attiva su Gmail
3. Email destinatari sbagliate
4. Server/porta SMTP errati

**Verifica:**
```python
# In app.py, aggiungi debug:
st.write(f"SMTP: {data['smtp_server']}:{data['smtp_port']}")
st.write(f"Email: {data['smtp_email']}")
st.write(f"Destinatari: {destinatari}")
```

### Streamlit Cloud non carica tutti i tab

**Causa:** Cache browser

**Soluzione:**
- Chrome: Cmd+Shift+R (Mac) o Ctrl+Shift+F5 (Win)
- Oppure: DevTools → Tieni premuto ricarica → "Svuota cache e ricarica"

### Safari non funziona con Streamlit Cloud

**Problema:** Safari ha problemi WebSocket con Streamlit

**Soluzione:** Usare Chrome o Firefox

### Dati resettati su Streamlit Cloud

**Causa:** Streamlit Cloud resetta filesystem ad ogni deploy

**Soluzione:** Usare ngrok per dati persistenti

### Grafici troppo grandi

**Soluzione:** (già implementata)
```python
# Ridurre figsize
fig, ax = plt.subplots(figsize=(7, 4))  # invece di (10, 6)

# Ridurre DPI
plt.savefig(file, dpi=100)  # invece di 150
```

### Git push richiede autenticazione

**Soluzione:** Installare GitHub CLI
```bash
brew install gh
gh auth login
# Segui procedura web
```

---

## 📝 Convenzioni Codice

### Naming
- Funzioni: `snake_case` (es: `calcola_piano_ammortamento`)
- Variabili: `snake_case` (es: `capitale_effettivo`)
- Costanti: `UPPER_CASE` (se presenti)

### Commenti
```python
# Commento singola riga

# Commento multiriga
# che spiega logica complessa
```

### Docstring (dove presenti)
```python
def funzione():
    """
    Breve descrizione

    Returns:
        Tipo e descrizione return
    """
```

### Streamlit Best Practices
- Usa `st.columns()` per layout
- Usa `st.session_state` per stato persistente
- Usa `st.cache_data` per calcoli pesanti (non implementato attualmente)
- Usa `use_container_width=True` (deprecato, migrare a `width='stretch'`)

---

## 🔄 Cronologia Modifiche Principali

**18 Ottobre 2025:**
- Rimossi grafici da dashboard
- Aggiunte sezioni download in tab Storico:
  - Lista cedole con download singolo
  - Download prospetto piano ammortamento

**18 Ottobre 2025 (precedente):**
- Implementato sistema email automatiche
- Aggiunto sistema bifase bonifici (eseguito/verificato)
- Creati cedolini PDF differenziati
- Aggiunta configurazione SMTP
- Deployment su Streamlit Cloud completato
- Setup ngrok tunnel

**Versioni precedenti:**
- Sistema base ammortamento italiano
- Gestione spese ripristino
- Doppio ruolo creditore/debitore
- Generazione report PDF

---

## 🎯 TODO Future

- [ ] Migrare `use_container_width` a `width='stretch'`
- [ ] Implementare `@st.cache_data` per calcoli piano ammortamento
- [ ] Aggiungere export Excel dello storico
- [ ] Template email personalizzabili
- [ ] Backup automatico JSON su cloud
- [ ] Dashboard grafici opzionale (toggle on/off)
- [ ] Autenticazione Google OAuth invece password hardcoded
- [ ] Notifiche SMS via Twilio (opzionale)

---

## 📞 Contatti e Risorse

**Repository:** https://github.com/montorogug-sys/piano-ammortamento-appartamento

**Streamlit Docs:** https://docs.streamlit.io/

**ReportLab Docs:** https://www.reportlab.com/docs/reportlab-userguide.pdf

**Ngrok Docs:** https://ngrok.com/docs

---

**Fine AI Registry**

_Questo documento è progettato per permettere a qualsiasi AI assistant di capire rapidamente come funziona l'applicazione e come modificarla senza dover rileggere tutto il codice._
