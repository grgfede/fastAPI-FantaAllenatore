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
        # PROVA 1: Carica senza saltare righe (spesso l'export diretto è così)
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()

        # Se non trova la colonna 'Nome', prova saltando la prima riga
        if 'Nome' not in df.columns:
            df = pd.read_excel(file_path, skiprows=1)
            df.columns = df.columns.str.strip()

        lista_giocatori = []
        for _, row in df.iterrows():
            nome = str(row.get('Nome', ''))
            # Filtriamo righe vuote o intestazioni ripetute
            if nome == '' or nome == 'nan' or nome == 'Nome':
                continue
                
            lista_giocatori.append({
                "n": nome,
                "r": str(row.get('R', 'N/D')),
                "s": str(row.get('Squadra', 'N/D')),
                "q": int(row.get('Qt. A', 0))
            })
        
        print(f"DEBUG: Caricati {len(lista_giocatori)} giocatori")
        return lista_giocatori
    except Exception as e:
        print(f"Errore: {e}")
        return []

@app.get("/")
def read_root():
    return {"status": "Online", "database": os.path.exists("quotazioni.xlsx")}

@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    tutti = carica_giocatori_reali()
    
    if not tutti:
        return {"status": "error", "messaggio_ai": "Database vuoto o leggibile male.", "giocatori": []}

    # Mescoliamo e prendiamo i primi 15 che rientrano nel budget
    random.shuffle(tutti)
    squadra = []
    spesa = 0
    
    for p in tutti:
        if p['q'] > 0 and (spesa + p['q']) <= request.budget and len(squadra) < 15:
            squadra.append(p)
            spesa += p['q']

    return {
        "status": "success",
        "messaggio_ai": f"Ho analizzato {len(tutti)} giocatori reali. Ecco la tua squadra!",
        "giocatori": squadra
    }
