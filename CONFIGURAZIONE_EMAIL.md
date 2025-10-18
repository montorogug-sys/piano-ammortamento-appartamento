# Configurazione Email e Bonifici

## 📧 Nuova Funzionalità: Notifiche Email Automatiche

Ora il sistema invia automaticamente email con cedolini PDF quando:
1. **Mattia registra un bonifico** → Email a entrambi con cedolino "ESEGUITO"
2. **Guglielmo verifica il bonifico** → Email a entrambi con cedolino "VERIFICATO" + link al report completo

---

## 🔧 Configurazione Iniziale SMTP (Gmail)

### Passo 1: Genera App Password Gmail

Per usare Gmail per inviare email automatiche:

1. Vai su https://myaccount.google.com/apppasswords
2. Accedi con il tuo account Gmail
3. Seleziona:
   - **App**: Posta
   - **Dispositivo**: Altro (personalizzato) → scrivi "Piano Ammortamento"
4. Clicca "Genera"
5. **Copia la password di 16 caratteri** (es: `abcd efgh ijkl mnop`)

### Passo 2: Configura nell'Applicazione

1. Accedi come **Guglielmo** (Creditore)
2. Vai nel tab **"⚙️ Configurazione"**
3. Scorri fino a **"📧 Configurazione Email e IBAN"**
4. Compila i campi:

   **Email:**
   - Email Guglielmo: `tua-email@gmail.com`
   - Email Mattia: `email-mattia@gmail.com`

   **IBAN:**
   - IBAN Guglielmo: `IT60X0542811101000000123456` (esempio)
   - IBAN Mattia: `IT28W8000000292100645211151` (esempio)

5. Scorri fino a **"📮 Configurazione Server SMTP"**
6. Compila:
   - **Email SMTP**: la tua email Gmail (es: `tua-email@gmail.com`)
   - **Password SMTP**: la App Password di 16 caratteri copiata prima
   - **Server SMTP**: `smtp.gmail.com` (già precompilato)
   - **Porta SMTP**: `587` (già precompilato)

7. Clicca **"Aggiorna Configurazione"**

✅ **Fatto!** Il sistema ora può inviare email automaticamente.

---

## 💳 Come Funziona: Flusso Pagamento con Bonifico

### Per Mattia (Debitore)

1. Esegui il bonifico bancario dal tuo conto
2. Accedi all'applicazione come Mattia
3. Vai nel tab **"💳 Registra Pagamento"**
4. Compila il form:
   - **Data Pagamento**: data in cui hai fatto il bonifico
   - **Importo**: importo trasferito
   - **Causale Bonifico**: viene precompilata automaticamente
   - **Note aggiuntive**: eventuali note (opzionale)
   - **IBAN Mittente**: il tuo IBAN (precompilato se configurato)
   - **IBAN Beneficiario**: IBAN di Guglielmo (precompilato se configurato)

5. Clicca **"📤 Registra Pagamento Rata"**

**Cosa succede:**
- ✅ Pagamento salvato nel sistema con stato "In attesa di verifica"
- 📄 Generato cedolino PDF **"BONIFICO ESEGUITO"** in `cedolini/`
- 📧 Inviate email a entrambi con:
  - Dettagli bonifico
  - Cedolino "ESEGUITO" allegato
  - Stato: ⏳ In attesa di verifica

### Per Guglielmo (Creditore)

1. Ricevi email con notifica bonifico eseguito
2. Controlla sul tuo conto corrente che il bonifico sia arrivato
3. Accedi all'applicazione come Guglielmo
4. Vai nel tab **"💰 Gestione Rate"**
5. Vedi le **"Rate in Attesa di Conferma"**
6. Espandi la rata da verificare e controlla:
   - Data e importo
   - Causale
   - IBAN mittente e beneficiario
   - Note

7. Clicca **"✅ Verifica e Conferma Bonifico"**

**Cosa succede:**
- ✅ Bonifico confermato nel sistema
- 📄 Generato nuovo cedolino **"BONIFICO VERIFICATO"** in `cedolini/`
- 📄 Generato report PDF completo aggiornato in `reports/`
- 📧 Inviate email a entrambi con:
  - Conferma verifica
  - Cedolino "VERIFICATO" allegato
  - Link/nome file del report completo
  - Stato: ✅ Pagamento Confermato

---

## 📂 Struttura File PDF

Dopo l'implementazione, i PDF vengono salvati così:

```
cedolini/
├── cedolino_bonifico_eseguito_20251018_1.pdf
├── cedolino_bonifico_verificato_20251018_1.pdf
├── cedolino_bonifico_eseguito_20251118_2.pdf
└── cedolino_bonifico_verificato_20251118_2.pdf

reports/
├── report_ammortamento_20251018_110530.pdf
└── report_ammortamento_20251118_143022.pdf
```

**Convenzione nomi:**
- `cedolino_bonifico_eseguito_[DATA]_[RATA].pdf` → Cedolino quando Mattia registra
- `cedolino_bonifico_verificato_[DATA]_[RATA].pdf` → Cedolino dopo verifica Guglielmo
- `report_ammortamento_[TIMESTAMP].pdf` → Report completo generato

---

## ✉️ Contenuto Email

### Email 1: Bonifico Eseguito (da Mattia)

**Oggetto:** 🏦 Bonifico Eseguito - Rata X

**Corpo:**
- Notifica che Mattia ha registrato il pagamento
- Dettagli: data, importo, causale, IBAN
- Stato: ⏳ In attesa di verifica
- Cedolino "ESEGUITO" allegato

**Destinatari:** Guglielmo + Mattia

---

### Email 2: Bonifico Verificato (da Guglielmo)

**Oggetto:** ✅ Bonifico Verificato - Rata X

**Corpo:**
- Conferma che Guglielmo ha verificato il bonifico
- Dettagli: rata, data pagamento, importo, causale, data verifica
- Stato: ✅ Pagamento Confermato
- Cedolino "VERIFICATO" allegato
- Link al report completo PDF

**Destinatari:** Guglielmo + Mattia

---

## 🔒 Sicurezza

### Password Gmail

⚠️ **IMPORTANTE:**
- **NON usare la password normale di Gmail**
- Usa solo la **App Password** generata appositamente
- La App Password può essere revocata in qualsiasi momento da Google

### Protezione Dati

- Le password SMTP sono salvate in `data/ammortamento_data.json`
- Per deployment cloud, considera di usare variabili d'ambiente o secrets
- Mai committare file contenenti password su repository pubblici

---

## 🛠️ Troubleshooting

### Email non vengono inviate

**Problema:** Vedi messaggio "Email non inviate: [errore]"

**Soluzioni:**
1. Verifica di aver inserito la **App Password** (non password normale Gmail)
2. Controlla che l'email SMTP sia corretta
3. Verifica che le email destinatari siano valide
4. Controlla la connessione internet
5. Verifica che il server SMTP sia `smtp.gmail.com` e porta `587`

### App Password Gmail non funziona

**Possibili cause:**
1. Account Gmail non ha autenticazione a 2 fattori attiva (obbligatoria per App Password)
2. App Password copiata con spazi (rimuovili: `abcd efgh ijkl mnop` → `abcdefghijklmnop`)
3. Account Gmail con policy aziendali restrittive

### Email si inviano ma non arrivano

1. Controlla la cartella **Spam** del destinatario
2. Verifica che le email destinatari siano scritte correttamente
3. Controlla che il provider email del destinatario non blocchi email automatiche

---

## 📝 Modificare Email/IBAN dopo Configurazione

Le email e IBAN possono essere modificati in qualsiasi momento:

1. Accedi come **Guglielmo**
2. Tab **"⚙️ Configurazione"**
3. Modifica i campi necessari
4. Clicca **"Aggiorna Configurazione"**

I nuovi valori saranno usati per tutti i pagamenti successivi.

---

## 🌐 Alternative a Gmail

Se non vuoi usare Gmail, puoi configurare altri provider:

### Outlook/Hotmail
- Server: `smtp-mail.outlook.com`
- Porta: `587`
- Email: tua email Outlook
- Password: password Outlook (o App Password se 2FA attiva)

### Yahoo
- Server: `smtp.mail.yahoo.com`
- Porta: `587`
- Email: tua email Yahoo
- Password: App Password Yahoo

### Provider personalizzato
Chiedi al tuo provider email:
- Indirizzo server SMTP
- Porta (solitamente 587 o 465)
- Se richiede autenticazione TLS/SSL

---

## 📞 Supporto

Per problemi con la configurazione email:
1. Controlla questa guida
2. Verifica i log dell'applicazione Streamlit
3. Testa l'invio email manualmente con i tuoi dati SMTP

---

**Versione:** 1.0
**Data:** Ottobre 2025
**Feature:** Sistema Notifiche Email Bonifici
