from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlannerRequest(BaseModel):
    budget: int
    strategy: str

def carica_giocatori_reali():
    file_path = "quotazioni.xlsx"
    if not os.path.exists(file_path):
        return []
    
    try:
        # SALTIAMO LA PRIMA RIGA (quella con "Quotazioni Fantacalcio...")
        # In questo modo la riga con "Nome", "R", "Squadra" diventa l'intestazione (header)
        df = pd.read_excel(file_path, skiprows=1)
        
        # Puliamo i nomi delle colonne da spazi bianchi extra
        df.columns = df.columns.str.strip()

        lista_giocatori = []
        for _, row in df.iterrows():
            nome = str(row.get('Nome', '')).strip()
            
            # Filtro per evitare righe vuote o l'intestazione stessa
            if nome == '' or nome == 'nan' or nome == 'Nome':
                continue
            
            # Recuperiamo i dati usando i nomi esatti delle tue colonne
            try:
                lista_giocatori.append({
                    "n": nome,
                    "r": str(row.get('R', 'N/D')).strip(),
                    "s": str(row.get('Squadra', 'N/D')).strip(),
                    "q": int(row.get('Qt. A', 0))
                })
            except:
                continue # Salta se la quotazione non è un numero
                
        return lista_giocatori
    except Exception as e:
        print(f"Errore durante la lettura dell'Excel: {e}")
        return []

@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    tutti = carica_giocatori_reali()
    
    if not tutti:
        return {
            "status": "error", 
            "messaggio_ai": "Errore: Non riesco a leggere i calciatori dall'Excel.", 
            "giocatori": []
        }

    # Semplice logica di test: mischia e prendi i primi 20
    random.shuffle(tutti)
    squadra = tutti[:20] 

    return {
        "status": "success",
        "messaggio_ai": f"Database pronto! Analizzati {len(tutti)} calciatori per la stagione 2025/26.",
        "giocatori": squadra
    }
