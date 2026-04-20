from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os

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
    file_path = "quotazioni.csv"
    if not os.path.exists(file_path):
        return [{"n": "CSV non trovato", "r": "P", "s": "Errore", "q": 0}]
    
    try:
        # Carichiamo il CSV. 
        # Nota: l'export di Fantacalcio spesso usa il punto e virgola ';'
        df = pd.read_csv(file_path, sep=";", encoding="utf-8")
        
        # Puliamo i nomi delle colonne per sicurezza (rimuove spazi bianchi)
        df.columns = df.columns.str.strip()

        giocatori = []
        for _, row in df.iterrows():
            # Usiamo i nomi esatti delle tue colonne
            giocatori.append({
                "n": str(row['Nome']),
                "r": str(row['R']),
                "s": str(row['Squadra']),
                "q": int(row['Qt. A']) # 'Qt. A' è la quotazione attuale
            })
        return giocatori
    except Exception as e:
        print(f"Errore: {e}")
        return []

@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    lista_completa = carica_giocatori_reali()
    
    # Esempio: prendiamo i primi 20 per vedere se arrivano su Flutter
    mini_lista = lista_completa[:20] 

    return {
        "status": "success",
        "messaggio_ai": f"Database caricato. Trovati {len(lista_completa)} giocatori.",
        "giocatori": mini_lista
    }
