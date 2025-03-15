# 3D Print Cost Calculator - Istruzioni Deploy

## Prerequisiti
- Hosting Aruba con supporto Python
- Accesso SSH al server
- Database PostgreSQL (fornito da Aruba o esterno)

## Struttura File
```
/
├── app.py                 # Frontend Streamlit
├── backend/              # Backend FastAPI
├── .htaccess            # Configurazione Apache
└── .streamlit/          # Configurazione Streamlit
```

## Configurazione Ambiente

### 1. Variabili d'Ambiente
Configura le seguenti variabili nel pannello di controllo Aruba o nel file `.env`:

```bash
# URL del backend (esempio)
BACKEND_URL=https://tuodominio.it/api

# Configurazione Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Porta del server Streamlit (usa 5000)
PORT=5000
```

### 2. Configurazione Apache
Il file `.htaccess` è già configurato per:
- Reindirizzare le richieste `/api/*` al backend FastAPI
- Servire l'app Streamlit per tutte le altre richieste

### 3. Setup Database
1. Crea un database PostgreSQL dal pannello Aruba
2. Usa le credenziali fornite per aggiornare DATABASE_URL
3. Il backend creerà automaticamente le tabelle necessarie

## Avvio dell'Applicazione

### Backend (FastAPI)
```bash
# Nel terminale SSH
cd /path/to/your/app
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### Frontend (Streamlit)
```bash
# In un altro terminale SSH
cd /path/to/your/app
streamlit run app.py --server.port 5000
```

## Verifica dell'Installazione

1. Accedi a `https://tuodominio.it`
2. Dovresti vedere la pagina principale del calcolatore
3. Nella barra laterale, clicca su "⚙️ Gestione Materiali"
4. Verifica che i materiali predefiniti siano visibili
5. Prova ad aggiungere un nuovo materiale

## Troubleshooting

### Errori Comuni

1. Se il backend non è raggiungibile:
   - Verifica che BACKEND_URL sia corretto
   - Controlla i log di Apache per errori di proxy

2. Se i materiali non vengono caricati:
   - Verifica la connessione al database
   - Controlla i log del backend per errori SQL

3. Se la navigazione non funziona:
   - Assicurati che il modulo mod_rewrite sia attivo
   - Verifica la sintassi del file .htaccess

### Log e Debug
- Log del backend: `/path/to/your/app/logs/backend.log`
- Log di Apache: `/var/log/apache2/error.log`
- Log di Streamlit: `/path/to/your/app/logs/streamlit.log`

Per assistenza aggiuntiva, contatta il supporto Aruba.
