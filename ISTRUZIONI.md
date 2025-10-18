# ISTRUZIONI D'USO - Piano Ammortamento Appartamento

## Guida Completa per l'Utilizzo dell'Applicazione

---

## 📋 INDICE

1. [Introduzione](#introduzione)
2. [Accesso all'Applicazione](#accesso-allapplicazione)
3. [Guida per Guglielmo (Creditore)](#guida-per-guglielmo-creditore)
4. [Guida per Mattia (Debitore)](#guida-per-mattia-debitore)
5. [Funzionalità Avanzate](#funzionalità-avanzate)
6. [Generazione Report PDF](#generazione-report-pdf)
7. [Backup e Sicurezza](#backup-e-sicurezza)
8. [Domande Frequenti (FAQ)](#domande-frequenti-faq)

---

## INTRODUZIONE

Questa applicazione gestisce il piano di ammortamento per il pagamento rateale dell'appartamento tra Guglielmo (venditore/creditore) e Mattia (acquirente/debitore).

### Caratteristiche Principali

- **Ammortamento Italiano**: Quota capitale costante, interessi decrescenti nel tempo
- **Tasso Fisso**: 2% annuo
- **Rata Fissa**: €300 mensili (durata variabile in base al capitale)
- **Doppio Controllo**: Mattia registra i pagamenti, Guglielmo conferma
- **Spese di Ripristino**: Tracciamento completo delle spese di manutenzione
- **Generazione PDF**: Ricevute automatiche e report completi
- **Versamenti Straordinari**: Possibilità di pagamenti extra per ridurre la durata
- **Salta Rata**: Possibilità di posticipare pagamenti

---

## ACCESSO ALL'APPLICAZIONE

### URL di Accesso

- **Locale**: `http://localhost:8501`
- **Rete Locale**: `http://[IP_COMPUTER]:8501`
- **Online** (se deployato): URL fornito da Streamlit Cloud

### Credenziali di Accesso

#### Mattia (Debitore)
- **Username**: `Mattia (Debitore)`
- **Password**: `mattia2025`

#### Guglielmo (Creditore)
- **Username**: `Guglielmo (Creditore)`
- **Password**: `guglielmo2025`

> ⚠️ **IMPORTANTE**: Si consiglia di cambiare le password nel codice prima del deployment in produzione!

---

## GUIDA PER GUGLIELMO (CREDITORE)

Guglielmo ha accesso a tutte le funzionalità dell'applicazione attraverso 5 tab.

### 1️⃣ TAB: DASHBOARD

**Cosa mostra:**
- Riepilogo generale del finanziamento
- Progresso pagamenti con barra di avanzamento
- Prossima rata da pagare con data di scadenza
- Prime 6 e ultime 6 rate del piano ammortamento
- Avvisi su rate in attesa di conferma

**Come usarlo:**
- Consulta questa sezione per avere una visione d'insieme dello stato del finanziamento
- Verifica il progresso dei pagamenti
- Controlla le prossime scadenze

### 2️⃣ TAB: GESTIONE RATE

**Funzioni disponibili:**

#### Confermare i Pagamenti
1. Visualizza la lista delle rate registrate da Mattia in attesa di conferma
2. Ogni rata mostra:
   - Numero rata
   - Data pagamento
   - Importo
   - Note (se presenti)
3. Clicca su **"Conferma Ricevuta"** per confermare il pagamento
4. Il sistema genera automaticamente un PDF ricevuta

#### Confermare Versamenti Straordinari
1. Visualizza versamenti extra registrati da Mattia
2. Controlla importo e note
3. Clicca su **"Conferma Versamento Straordinario"**
4. Il sistema aggiorna automaticamente la durata del finanziamento

#### Gestire Rate Saltate
- Visualizza l'elenco delle rate saltate da Mattia
- Controlla il motivo del salto
- Monitora l'impatto sulla durata totale

### 3️⃣ TAB: SPESE RIPRISTINO

**Come gestire le spese:**

#### Aggiungere una Nuova Spesa
1. Compila il modulo:
   - **Categoria**: Seleziona (Elettrico, Idraulico, Muratura, Infissi, Altro)
   - **Descrizione**: Descrivi brevemente il lavoro
   - **Importo**: Inserisci il costo (es: 1500.50)
   - **Data**: Seleziona la data della spesa
   - **Fornitore/Note**: Aggiungi dettagli (opzionale)
2. Clicca su **"Aggiungi Spesa"**
3. La spesa viene automaticamente sottratta dal capitale iniziale

#### Visualizzare il Riepilogo
- Totale spese per categoria
- Grafico a torta della distribuzione
- Tabella dettagliata di tutte le spese

**⚠️ Importante**: Le spese di ripristino riducono il capitale effettivo da rimborsare!

### 4️⃣ TAB: CONFIGURAZIONE

**Gestione Configurazione Iniziale:**

1. **Solo alla prima configurazione**:
   - Inserisci il capitale iniziale (es: €80,000)
   - Imposta la rata mensile target (es: €300)
   - Verifica il tasso di interesse (default 2%)
   - Controlla la durata calcolata automaticamente
   - Clicca su **"Conferma Configurazione"**

2. **Modifica Configurazione Esistente**:
   - Puoi modificare i parametri anche dopo l'inizio
   - ⚠️ Attenzione: modificare i parametri ricalcola tutto il piano
   - Clicca su **"Aggiorna Configurazione"** per salvare

### 5️⃣ TAB: STORICO

**Funzioni disponibili:**

#### Generare Report PDF Completo
1. Clicca su **"📄 Genera Report PDF Completo"**
2. Il sistema genera un PDF con:
   - Riepilogo generale
   - Piano ammortamento completo con tutte le date
   - Storico pagamenti effettuati
   - Versamenti straordinari (se presenti)
3. Il file viene salvato nella cartella dell'applicazione

#### Visualizzare lo Storico
- **Pagamenti confermati**: Data, importo, capitale residuo, note
- **Versamenti straordinari**: Importi extra pagati
- **Rate saltate**: Numero rata, data, motivo
- **Calcolo saldo anticipato**: Quanto serve per saldare tutto

---

## GUIDA PER MATTIA (DEBITORE)

Mattia ha accesso a 4 tab con funzionalità di consultazione e registrazione pagamenti.

### 1️⃣ TAB: DASHBOARD

**Cosa mostra:**
- Stesso contenuto della dashboard di Guglielmo
- Visualizzazione del progresso pagamenti
- Prossima rata da pagare
- Piano ammortamento (prime e ultime 6 rate)

**Come usarlo:**
- Consulta regolarmente per verificare lo stato del debito
- Controlla le scadenze prossime
- Monitora il capitale residuo

### 2️⃣ TAB: REGISTRA PAGAMENTO

**Come registrare un pagamento:**

#### Pagamento Rata Mensile
1. Verifica le informazioni della rata del mese:
   - Numero rata
   - **Data di scadenza**
   - Importo totale
   - Quota capitale
   - Quota interessi
2. Inserisci i dati del pagamento:
   - **Data Pagamento**: (default oggi, modificabile)
   - **Importo**: (precompilato, modificabile)
   - **Note**: Aggiungi informazioni se necessario
3. Clicca su **"📤 Registra Pagamento Rata"**
4. Attendi la conferma da Guglielmo

#### Versamento Straordinario (Una Tantum)
1. Espandi la sezione **"💰 Versamento Straordinario"**
2. Visualizza il capitale residuo attuale
3. Inserisci l'importo extra da versare
4. Il sistema mostra immediatamente:
   - Nuova durata in mesi
   - Mesi risparmiati
   - Nuova data fine prevista
5. Aggiungi note (opzionale)
6. Clicca su **"💸 Registra Versamento Straordinario"**
7. Attendi la conferma da Guglielmo

**💡 Esempio**: Se il capitale residuo è €50,000 e versi €5,000 straordinari, la durata si riduce proporzionalmente.

#### Saltare una Rata
1. Clicca su **"⏭️ Salta Rata del Mese"**
2. Inserisci il motivo (es: "Spese impreviste", "Difficoltà economiche temporanee")
3. Conferma
4. La scadenza viene automaticamente posticipata di 1 mese

**⚠️ Attenzione**: Ogni rata saltata posticipa la fine del finanziamento di 1 mese!

### 3️⃣ TAB: SPESE RIPRISTINO

**Visualizzazione:**
- Riepilogo spese per categoria
- Grafico distribuzione
- Tabella dettagliata

**Nota**: Mattia può solo visualizzare, non può aggiungere spese.

### 4️⃣ TAB: STORICO

Stesso contenuto della sezione Storico di Guglielmo:
- Può generare il **Report PDF Completo**
- Visualizza tutti i pagamenti confermati
- Vede i versamenti straordinari effettuati
- Controlla le rate saltate

---

## FUNZIONALITÀ AVANZATE

### 📊 Piano di Ammortamento Italiano

**Come funziona:**
- La **quota capitale** è costante ogni mese (€ capitale/durata)
- Gli **interessi** sono calcolati sul debito residuo e diminuiscono nel tempo
- La **rata totale** = quota capitale + interessi (decresce leggermente ogni mese)

**Esempio con €80,000, rata €300, 2% annuo:**
- Mese 1: Quota Capitale €266,67 + Interessi €133,33 = Rata €300,00
- Mese 150: Quota Capitale €266,67 + Interessi €20,00 = Rata €286,67
- Mese 267 (ultimo): Quota Capitale €266,67 + Interessi €0,44 = Rata €267,11

### 💰 Versamenti Straordinari

**Vantaggi:**
- Riducono il capitale residuo immediatamente
- Diminuiscono la durata del finanziamento
- Riducono gli interessi totali da pagare

**Come vengono gestiti:**
1. Mattia registra il versamento
2. Guglielmo conferma
3. Il sistema ricalcola automaticamente:
   - Nuovo capitale residuo
   - Nuova durata (mantenendo rata €300)
   - Nuovo piano ammortamento

### ⏭️ Saltare Rate

**Effetti:**
- La rata saltata viene spostata in fondo al piano
- La durata totale aumenta di 1 mese per ogni rata saltata
- Il capitale residuo rimane invariato
- Gli interessi totali aumentano leggermente

**Quando usare:**
- Difficoltà economiche temporanee
- Spese impreviste urgenti
- Accordo tra le parti

### 🏗️ Spese di Ripristino

**Categorie disponibili:**
- **Elettrico**: Impianti elettrici, illuminazione
- **Idraulico**: Tubature, sanitari, caldaia
- **Muratura**: Muri, intonaci, pavimenti
- **Infissi**: Finestre, porte, serramenti
- **Altro**: Altre spese

**Impatto:**
- Le spese riducono il capitale iniziale
- Il piano ammortamento viene ricalcolato sul capitale effettivo
- Capitale Effettivo = Capitale Iniziale - Totale Spese Ripristino

**Esempio:**
- Capitale Iniziale: €80,000
- Spese Ripristino: €5,000
- **Capitale Effettivo: €75,000** ← Base per calcolo rate

---

## GENERAZIONE REPORT PDF

### 📄 Report Completo

**Contenuto del PDF:**

1. **Riepilogo Generale**
   - Capitale iniziale e effettivo
   - Rate pagate e progresso
   - Capitale residuo
   - Parametri finanziamento

2. **Piano Ammortamento Completo**
   - Tutte le rate con:
     - Numero mese
     - **Data di scadenza**
     - Quota capitale
     - Quota interessi
     - Rata totale
     - Debito residuo

3. **Storico Pagamenti Effettuati**
   - Data pagamento
   - Importo
   - Note
   - Totale pagato

4. **Versamenti Straordinari** (se presenti)
   - Data
   - Importo
   - Note
   - Totale straordinari

**Come generarlo:**
1. Vai nel tab **"Storico"**
2. Clicca su **"📄 Genera Report PDF Completo"**
3. Il file viene creato nella cartella **`reports/`** con nome: `report_ammortamento_YYYYMMDD_HHMMSS.pdf`
4. Salvalo in un posto sicuro per i tuoi archivi

**Quando generarlo:**
- Alla fine di ogni anno
- Prima di riunioni tra le parti
- Per controlli periodici
- Per backup documentale

### 📋 Ricevute Singole Rate

**Quando vengono generate:**
- Automaticamente quando Guglielmo conferma un pagamento

**Contenuto:**
- Data pagamento
- Numero rata
- Importo
- Capitale residuo
- Spazio per firme

**Nome file e posizione:** `cedolini/ricevuta_YYYY-MM-DD_RATA_X.pdf`

---

## BACKUP E SICUREZZA

### 💾 Backup dei Dati

**File dati:** `data/ammortamento_data.json`

**Come fare backup manuale:**

```bash
# Mac/Linux
cp data/ammortamento_data.json backup/backup_$(date +%Y%m%d).json

# Windows
copy data\ammortamento_data.json backup\backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json
```

**Frequenza consigliata:**
- Backup settimanale
- Backup dopo ogni conferma pagamento importante
- Backup prima di modificare la configurazione

**Dove salvare i backup:**
- Google Drive / Dropbox
- Chiavetta USB esterna
- Cloud storage personale

### 🔒 Sicurezza

**Cambio Password:**

1. Apri il file `app.py`
2. Cerca la sezione login (righe ~437-446)
3. Modifica le password:

```python
if utente == "Mattia (Debitore)" and password == "TUA_PASSWORD_SICURA_MATTIA":
    ...
elif utente == "Guglielmo (Creditore)" and password == "TUA_PASSWORD_SICURA_GUGLIELMO":
    ...
```

**Raccomandazioni:**
- Password minimo 12 caratteri
- Mix lettere maiuscole, minuscole, numeri, simboli
- Non condividere via email/SMS
- Cambiare periodicamente (es: ogni 6 mesi)

### 🌐 Privacy Dati

**Deployment Locale:**
- Dati accessibili solo da rete locale
- Nessun dato viene caricato online

**Deployment Streamlit Cloud:**
- Impostare repository privato su GitHub
- Aggiungere solo email autorizzate nelle impostazioni app
- Considerare backup locali periodici

---

## DOMANDE FREQUENTI (FAQ)

### ❓ Generali

**D: Posso modificare l'importo della rata mensile?**
R: Sì, dalla sezione Configurazione. Modifica la "Rata mensile target" e clicca "Aggiorna Configurazione". Attenzione: questo ricalcola tutto il piano ammortamento.

**D: Cosa succede se inserisco una spesa di ripristino?**
R: La spesa viene sottratta dal capitale iniziale, riducendo il totale da rimborsare. Il piano ammortamento viene automaticamente ricalcolato.

**D: Posso cancellare un pagamento già confermato?**
R: No, per sicurezza i pagamenti confermati non possono essere cancellati dall'applicazione. Per correzioni, contattare direttamente Guglielmo.

### ❓ Pagamenti

**D: Quanto posso versare come rata straordinaria?**
R: Fino al totale del capitale residuo. Puoi anche saldare completamente il debito.

**D: Posso saltare più rate consecutive?**
R: Tecnicamente sì, ma ogni rata saltata posticipa la fine del finanziamento. Meglio limitare i salti.

**D: Come vengono calcolati gli interessi?**
R: Interessi = (Capitale Residuo × 2%) / 12 mesi. Gli interessi diminuiscono ogni mese perché il capitale residuo diminuisce.

**D: La data di scadenza della rata è fissa?**
R: Sì, le date partono dalla data di configurazione iniziale e procedono mensilmente (es: se inizi il 15 gennaio, le rate scadono il 15 di ogni mese).

### ❓ Tecnici

**D: Dove vengono salvati i dati?**
R: Nel file `data/ammortamento_data.json` nella cartella dell'applicazione.

**D: Posso accedere da smartphone?**
R: Sì, l'interfaccia è responsive e funziona su qualsiasi dispositivo con browser.

**D: L'app funziona offline?**
R: Se installata localmente, sì. Se deployata su Streamlit Cloud, serve connessione internet.

**D: I PDF dove vengono salvati?**
R: I report completi nella cartella `reports/`, le ricevute singole nella cartella `cedolini/`.

**D: Posso stampare i report?**
R: Sì, apri il PDF generato e stampalo normalmente.

### ❓ Problemi Comuni

**D: L'app non si avvia, cosa faccio?**
R:
1. Verifica che Python sia installato: `python --version`
2. Verifica dipendenze: `pip install -r requirements.txt`
3. Riavvia: `streamlit run app.py`

**D: Non vedo il pulsante di conferma pagamenti.**
R: Sei loggato come Mattia? Solo Guglielmo può confermare pagamenti.

**D: Il PDF non viene generato.**
R: Verifica che reportlab sia installato: `pip install reportlab --upgrade`

**D: Ho perso la password, cosa faccio?**
R: Le password sono nel codice sorgente (`app.py`). Se hai accesso al file, puoi leggerle o cambiarle.

---

## 📞 SUPPORTO

Per problemi tecnici:
1. Verifica questa guida
2. Controlla il file README.md
3. Verifica i log dell'applicazione
4. Se deployato su Streamlit Cloud: "Manage app" > "Logs"

---

## 📝 NOTE LEGALI

Questa applicazione è per uso privato tra Guglielmo e Mattia.
Non sostituisce consulenza legale o finanziaria professionale.
Per accordi ufficiali, consultare un notaio o consulente legale.

---

**Versione:** 2.0
**Ultimo Aggiornamento:** Ottobre 2025
**Autore:** Sviluppato per Guglielmo e Mattia

---

## 🎯 GUIDA RAPIDA

### Per Mattia (Ogni Mese):
1. Accedi all'app
2. Tab "Registra Pagamento"
3. Verifica importo e data scadenza
4. Conferma pagamento
5. (Opzionale) Aggiungi versamento straordinario
6. Attendi conferma da Guglielmo

### Per Guglielmo (Ogni Mese):
1. Accedi all'app
2. Tab "Gestione Rate"
3. Verifica il pagamento di Mattia
4. Clicca "Conferma Ricevuta"
5. Scarica PDF ricevuta generato
6. (Periodicamente) Genera report completo dal tab Storico

---

**Fine Documento - Buon Utilizzo! 🏠💰**
