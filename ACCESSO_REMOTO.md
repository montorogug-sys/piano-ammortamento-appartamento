# Accesso Remoto all'Applicazione

**Data creazione:** 18 Ottobre 2025
**Metodi di deployment:** Streamlit Cloud + Ngrok Tunnel

---

## ⭐ Opzione 1: Streamlit Cloud (CONSIGLIATO PER DEMO)

**Link applicazione:** https://piano-ammortamento-appartamento-jxrz72g7px4kxh3dslfo4c.streamlit.app

**Status:** ✅ Online e funzionante (tutti i tab caricati correttamente)

**Vantaggi:**
- ✅ Sempre online (anche con Mac spento)
- ✅ Link permanente e pubblico
- ✅ Nessuna configurazione richiesta

**⚠️ IMPORTANTE:**
- ✅ **USARE CHROME** - funziona perfettamente
- ❌ **Safari NON funziona** - problemi di caricamento e autenticazione

**Svantaggi:**
- ⚠️ **I DATI SI RESETTANO** ad ogni riavvio/aggiornamento dell'app
- ⚠️ Solo per TEST e DEMO, non per dati reali

---

## 💾 Opzione 2: Ngrok Tunnel (CONSIGLIATO PER DATI REALI)

**Link applicazione:** https://interzooecial-configurational-mallory.ngrok-free.dev

**Status:** ✅ Funzionante e testato

**Vantaggi:**
- ✅ **Dati persistenti** salvati sul Mac
- ✅ Aggiornamenti istantanei del codice
- ✅ Controllo completo
- ✅ Backup facile (file JSON sul Mac)

**Svantaggi:**
- ⚠️ Richiede Mac acceso e connesso
- ⚠️ Richiede streamlit e ngrok in esecuzione
- ⚠️ Link può cambiare se ngrok viene riavviato

---

## 🎯 Quale Usare?

| Scenario | Usa |
|----------|-----|
| Test iniziale con Mattia | **Streamlit Cloud** |
| Demo veloce | **Streamlit Cloud** |
| Dati REALI di pagamenti | **Ngrok** |
| Produzione quotidiana | **Ngrok** |
| Backup e sicurezza dati | **Ngrok** |

---

## Credenziali di Accesso

### Per Mattia (Debitore)
- **Username:** `Mattia (Debitore)`
- **Password:** `mattia2025`

### Per Guglielmo (Creditore)
- **Username:** `Guglielmo (Creditore)`
- **Password:** `guglielmo2025`

> ⚠️ **IMPORTANTE**: Queste sono password TEMPORANEE per il test iniziale. Verranno cambiate dopo la configurazione completa.

---

## 🔄 Procedura Aggiornamento Software

### Con Streamlit Cloud:
1. Modifica i file sul Mac (`app.py`, ecc.)
2. Fai commit e push su GitHub:
   ```bash
   git add .
   git commit -m "Descrizione modifiche"
   git push origin main
   ```
3. Streamlit Cloud rileva il push automaticamente
4. L'app si riavvia (1-2 minuti)
5. ⚠️ **I DATI vengono RESETTATI** al riavvio

### Con Ngrok:
1. Modifica i file sul Mac
2. Streamlit rileva automaticamente le modifiche
3. Clicca "Rerun" nella UI
4. Aggiornamento **istantaneo**
5. ✅ **I DATI restano intatti**

---

## Istruzioni per Mattia

### Scegli quale URL usare:

**Per TEST/DEMO (senza dati reali):**
- URL: https://piano-ammortamento-appartamento-6munvtkctp5ynbdtr7rbor.streamlit.app
- Usa **Chrome** (Safari può avere problemi)

**Per DATI REALI (pagamenti effettivi):**
- URL: https://interzooecial-configurational-mallory.ngrok-free.dev
- Qualsiasi browser

### Accesso:

1. **Apri il browser** (Chrome consigliato per Streamlit Cloud)
2. **Vai all'indirizzo** scelto sopra
3. **Prima visita Ngrok**: Potresti vedere "You are about to visit..." → Clicca **"Visit Site"**
4. **Login**:
   - Seleziona "Mattia (Debitore)" dal menu
   - Inserisci password: `mattia2025`
   - Clicca "Login"

---

## Funzionalità Disponibili

### Per Mattia
- **Dashboard**: Visualizza progresso pagamenti e piano ammortamento
- **Registra Pagamento**: Dopo aver fatto il bonifico, registra i dati:
  - Data pagamento
  - Importo
  - Causale (precompilata)
  - IBAN mittente e beneficiario
- **Spese Ripristino**: Visualizza le spese di manutenzione
- **Impostazioni**: Configura la tua email e IBAN personale
- **Storico**: Vedi tutte le rate pagate

### Per Guglielmo
- Tutte le funzionalità di Mattia
- **Gestione Rate**: Verifica e conferma i bonifici di Mattia
- **Configurazione**: Imposta parametri finanziamento, email SMTP, IBAN

---

## Note Importanti

### Disponibilità
- ✅ L'applicazione è accessibile finché il Mac di Guglielmo è acceso
- ✅ Funziona da qualsiasi dispositivo connesso a internet
- ✅ Nessuna installazione richiesta per Mattia

### Sicurezza
- 🔒 Connessione HTTPS criptata
- 🔒 Dati salvati localmente sul Mac di Guglielmo
- 🔒 Le password verranno cambiate dopo il test

### Backup Dati
I dati sono salvati in:
`/Users/guglielmo/Documents/Archivio Guglielmo/PythonSoft/Piano_ammortamento_appartamento/data/ammortamento_data.json`

---

## Flusso Operativo Bonifico

### 1. Mattia esegue il bonifico
- Vai in banca/app bancaria
- Fai bonifico a Guglielmo con causale e importo corretti
- Annotati data e importo

### 2. Mattia registra nel sistema
- Accedi all'app
- Tab "Registra Pagamento"
- Compila form con dati bonifico
- Clicca "Registra Pagamento Rata"
- **Sistema invia email automatica** a entrambi con cedolino "ESEGUITO"

### 3. Guglielmo verifica
- Ricevi email di notifica
- Controlla arrivo bonifico sul conto corrente
- Accedi all'app
- Tab "Gestione Rate"
- Clicca "Verifica e Conferma Bonifico"
- **Sistema invia email** a entrambi con cedolino "VERIFICATO" + report completo

---

## Configurazione Email (Prima del Primo Bonifico)

Prima di registrare il primo pagamento, Guglielmo deve configurare:

1. **Email e IBAN** (entrambi)
2. **Server SMTP Gmail**:
   - Generare App Password Gmail (vedi CONFIGURAZIONE_EMAIL.md)
   - Inserire email SMTP e App Password nell'app

**Questo permette l'invio automatico delle email con i cedolini PDF.**

---

## Troubleshooting

### L'app non si apre
- Verifica che il link sia completo e corretto
- Prova a copiare/incollare invece di cliccare
- Prova con un browser diverso

### "Sito non raggiungibile"
- Il Mac di Guglielmo potrebbe essere spento
- Il tunnel ngrok potrebbe essere stato fermato
- Contatta Guglielmo

### Login non funziona
- Verifica username esatto: `Mattia (Debitore)` (con maiuscola e parentesi)
- Password: `mattia2025` (tutto minuscolo)
- Non dimenticare di selezionare l'utente dal menu a tendina

---

## Fermare il Tunnel (Solo Guglielmo)

Quando non serve più condividere l'app:

```bash
pkill ngrok
```

Questo ferma la condivisione ma l'app continua a girare localmente.

---

## Alternative di Accesso

### Rete Locale (Stesso WiFi)
Se Mattia è sulla stessa rete WiFi di Guglielmo:
**http://192.168.3.2:8501**

### Locale (Solo Guglielmo)
**http://localhost:8501**

---

**Versione:** 1.0
**Tunnel ID:** command_line
**Creato il:** 18/10/2025 alle 05:53 UTC
