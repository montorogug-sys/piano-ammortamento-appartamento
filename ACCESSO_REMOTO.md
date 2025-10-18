# Accesso Remoto all'Applicazione

**Data creazione:** 18 Ottobre 2025

---

## URL Pubblico (Ngrok Tunnel)

**Link applicazione:** https://interzooecial-configurational-mallory.ngrok-free.dev

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

## Istruzioni per Mattia

1. **Apri il browser** (Chrome, Safari, Firefox, ecc.)
2. **Vai all'indirizzo:** https://interzooecial-configurational-mallory.ngrok-free.dev
3. **Prima visita**: Potresti vedere una pagina intermedia "You are about to visit..." → Clicca **"Visit Site"**
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
