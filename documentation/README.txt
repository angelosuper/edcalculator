# 3D Print Cost Calculator - Documentazione Completa

## Struttura dei File

### Frontend (Streamlit)
1. app.py
   - Funzione: Entry point dell'applicazione Streamlit
   - Plugin: streamlit, plotly, three.js
   - Caratteristiche: Visualizzatore 3D, calcolo costi, interfaccia multilingua

2. materials_manager.py 
   - Funzione: Gestione materiali
   - Plugin: streamlit, requests
   - Caratteristiche: CRUD operazioni materiali, validazione dati

3. stl_processor.py
   - Funzione: Processamento file STL
   - Plugin: numpy-stl, numpy
   - Caratteristiche: Calcolo volume, stima tempi

### Backend (FastAPI)
1. backend/api.py
   - Funzione: API REST
   - Plugin: fastapi, sqlalchemy
   - Caratteristiche: Endpoints materiali e costi

2. backend/models.py
   - Funzione: Modelli database
   - Plugin: sqlalchemy
   - Caratteristiche: Schema dati

3. backend/schemas.py
   - Funzione: Validazione
   - Plugin: pydantic
   - Caratteristiche: Schema API

## Configurazione Database
```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Avvio Applicazione
1. Backend:
```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

2. Frontend:
```bash
streamlit run app.py --server.port 5000
```

## Dipendenze
```
fastapi
numpy
numpy-stl
pandas
plotly
psycopg2-binary
pydantic
requests
sqlalchemy
streamlit
trimesh
uvicorn
```
