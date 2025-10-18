# Piano Ammortamento Appartamento

Applicazione web per la gestione del piano di ammortamento per il pagamento rateale di un appartamento tra privati.

## Caratteristiche

- **Ammortamento Italiano**: Quota capitale costante, interessi decrescenti
- **Tasso fisso al 2% annuo**
- **Doppio controllo**: Mattia registra i pagamenti, Guglielmo conferma
- **Gestione bonifici bancari**: Tracciamento completo con IBAN e causali
- **Notifiche email automatiche**: Email con cedolini PDF per ogni fase del pagamento
- **Gestione spese ripristino**: Tracciamento completo delle spese di manutenzione
- **Generazione PDF**: Ricevute automatiche per ogni rata confermata
- **Dashboard interattiva**: Visualizzazione progresso e piano ammortamento
- **Cedolini bonifico**: PDF separati per "Eseguito" e "Verificato"

## Configurazione Iniziale

### Parametri Default
- Capitale iniziale: €80.000
- Rata mensile target: €300
- Tasso interesse: 2% annuo
- Tipo ammortamento: Italiano (quota capitale costante)
- Durata: Calcolata automaticamente in base alla rata

### Utenti e Password

**Mattia (Debitore)**
- Username: `Mattia (Debitore)`
- Password: `mattia2025`
- Permessi: Registrare pagamenti, visualizzare dashboard e spese

**Guglielmo (Creditore)**
- Username: `Guglielmo (Creditore)`
- Password: `guglielmo2025`
- Permessi: Confermare pagamenti, gestire configurazione, gestire spese ripristino

> ⚠️ **IMPORTANTE**: Cambia le password prima del deployment in produzione! Modifica le righe 137-146 in `app.py`.

## Installazione Locale

### Requisiti
- Python 3.8+
- pip

### Setup

1. **Crea ambiente virtuale (consigliato)**
```bash
cd "/Users/guglielmo/Documents/Archivio Guglielmo/PythonSoft/Piano_ammortamento_appartamento"
python3 -m venv venv
source venv/bin/activate  # Su Mac/Linux
# oppure su Windows: venv\Scripts\activate
```

2. **Installa dipendenze**
```bash
pip install -r requirements.txt
```

3. **Avvia l'applicazione**
```bash
streamlit run app.py
```

L'app sarà disponibile su: `http://localhost:8501`

### Accesso da Rete Locale

Se vuoi che Mattia acceda dal suo PC sulla stessa rete:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Mattia potrà accedere usando: `http://TUO_IP:8501`

Per trovare il tuo IP:
- Mac: `ifconfig | grep "inet "`
- Windows: `ipconfig`

## Deployment su Streamlit Cloud (CONSIGLIATO)

### Vantaggi
- ✅ Gratuito
- ✅ Accessibile da qualsiasi dispositivo
- ✅ Sempre online
- ✅ HTTPS automatico
- ✅ Nessuna configurazione server

### Procedura

1. **Crea repository GitHub**
   - Vai su https://github.com
   - Crea nuovo repository (es. `piano-ammortamento`)
   - Inizializza senza README (ne hai già uno)

2. **Carica il codice su GitHub**
```bash
cd "/Users/guglielmo/Documents/Archivio Guglielmo/PythonSoft/Piano_ammortamento_appartamento"
git init
git add .
git commit -m "Initial commit - Piano Ammortamento App"
git branch -M main
git remote add origin https://github.com/TUO_USERNAME/piano-ammortamento.git
git push -u origin main
```

3. **Deploy su Streamlit Cloud**
   - Vai su https://share.streamlit.io
   - Fai login con GitHub
   - Click su "New app"
   - Seleziona:
     - Repository: `TUO_USERNAME/piano-ammortamento`
     - Branch: `main`
     - Main file path: `app.py`
   - Click "Deploy!"

4. **Configurazione Privacy (Opzionale)**
   - Nelle impostazioni dell'app, puoi renderla privata
   - Aggiungi email autorizzate (tua e di Mattia)

### URL Finale
L'app sarà disponibile su:
`https://TUO_USERNAME-piano-ammortamento-app-xxx.streamlit.app`

## Struttura File

```
Piano_ammortamento_appartamento/
├── app.py                  # Applicazione principale
├── requirements.txt        # Dipendenze Python
├── README.md              # Questo file
├── ISTRUZIONI.md          # Guida completa all'utilizzo
├── CONFIGURAZIONE_EMAIL.md # Guida configurazione email e bonifici
├── data/                  # Cartella dati (creata automaticamente)
│   └── ammortamento_data.json  # Database pagamenti e configurazione
├── reports/               # PDF report completi
│   └── report_ammortamento_*.pdf
└── cedolini/              # PDF ricevute e cedolini bonifici
    ├── ricevuta_*.pdf
    ├── cedolino_bonifico_eseguito_*.pdf
    └── cedolino_bonifico_verificato_*.pdf
```

## Utilizzo

### 1. Configurazione Iniziale (Guglielmo)
- Login come Guglielmo
- Tab "Configurazione"
- **Parametri Finanziamento:**
  - Capitale iniziale (€80.000)
  - Rata mensile target (€300)
  - Tasso interesse (2%)
- **Email e IBAN:**
  - Email Guglielmo e Mattia
  - IBAN conti correnti
- **Server SMTP (per email automatiche):**
  - Email SMTP e App Password Gmail
  - Vedi `CONFIGURAZIONE_EMAIL.md` per dettagli
- Aggiungi eventuali spese di ripristino
- Conferma configurazione

### 2. Registrazione Bonifico (Mattia)
- Esegui bonifico bancario
- Login come Mattia
- Tab "Registra Pagamento"
- Compila form bonifico:
  - Data pagamento
  - Importo
  - Causale (precompilata)
  - IBAN mittente e beneficiario
- Click "Registra Pagamento Rata"
- Sistema invia email automatica a entrambi con cedolino "ESEGUITO"
- Aspetta verifica da Guglielmo

### 3. Verifica Bonifico (Guglielmo)
- Ricevi email con notifica bonifico
- Controlla arrivo bonifico sul conto corrente
- Login come Guglielmo
- Tab "Gestione Rate"
- Verifica dettagli bonifico (IBAN, causale, importo)
- Click "Verifica e Conferma Bonifico"
- Sistema genera:
  - Cedolino PDF "VERIFICATO"
  - Report completo aggiornato
  - Email automatiche a entrambi

### 4. Gestione Spese Ripristino (Guglielmo)
- Tab "Spese Ripristino"
- Aggiungi nuove spese per categoria
- Visualizza riepilogo e grafici
- Le spese vengono automaticamente sottratte dal capitale

### 5. Monitoraggio (Entrambi)
- Dashboard: Progresso pagamenti
- Storico: Tutte le rate confermate
- Calcolo saldo anticipato

## Backup Dati

I dati sono salvati in `data/ammortamento_data.json`.

**Per fare backup:**
```bash
cp data/ammortamento_data.json data/backup_$(date +%Y%m%d).json
```

**Su Streamlit Cloud:**
I dati persistono finché l'app è attiva. Per backup sicuri, considera di usare:
- GitHub per versioning del codice
- Google Drive/Dropbox per backup manuali del JSON

## Sicurezza

### Password
Cambia le password hardcoded prima del deployment:

In `app.py`, linee 137-146, modifica:
```python
if utente == "Mattia (Debitore)" and password == "TUA_PASSWORD_SICURA_MATTIA":
    ...
elif utente == "Guglielmo (Creditore)" and password == "TUA_PASSWORD_SICURA_GUGLIELMO":
    ...
```

### Raccomandazioni
- Usa password forti (minimo 12 caratteri, mix lettere/numeri/simboli)
- Non condividere le password via email/SMS non criptati
- Cambia le password periodicamente
- Se usi Streamlit Cloud privato, limita accesso alle email autorizzate

## Troubleshooting

### L'app non si avvia
```bash
# Verifica installazione dipendenze
pip install -r requirements.txt --upgrade

# Verifica versione Python
python --version  # Deve essere 3.8+
```

### Errore "Module not found"
```bash
pip install streamlit pandas reportlab
```

### I dati non si salvano
- Verifica permessi scrittura cartella `data/`
- Su Streamlit Cloud: i dati si resettano al restart (normale)

### PDF non generato
```bash
pip install reportlab --upgrade
```

## Supporto

Per problemi o domande:
1. Verifica questo README
2. Per configurazione email: vedi `CONFIGURAZIONE_EMAIL.md`
3. Per istruzioni complete: vedi `ISTRUZIONI.md`
4. Controlla i log dell'applicazione
5. Su Streamlit Cloud: vedi "Manage app" > "Logs"

## Licenza

Uso privato - Guglielmo & Mattia
