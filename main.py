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
    file_path = "quotazioni.xlsx"
    if not os.path.exists(file_path):
        return []
    
    try:
        # Saltiamo la prima riga di intestazione grafica
        df = pd.read_excel(file_path, skiprows=1)
        
        # Pulizia radicale dei nomi delle colonne
        df.columns = df.columns.str.strip()

        lista_giocatori = []
        for _, row in df.iterrows():
            nome = str(row.get('Nome', '')).strip()
            
            # Saltiamo righe vuote o righe di intestazione ripetute
            if nome == '' or nome == 'nan' or nome == 'Nome':
                continue
            
            # GESTIONE COSTO (Qt.A) - Corretto senza spazio
            costo_raw = row.get('Qt.A', 0)
            
            try:
                # Convertiamo in float e poi in int per gestire eventuali decimali (es. 25.0)
                costo_finale = int(float(costo_raw))
            except:
                costo_finale = 0

            lista_giocatori.append({
                "n": nome,
                "r": str(row.get('R', 'N/D')).strip(),
                "s": str(row.get('Squadra', 'N/D')).strip(),
                "q": costo_finale
            })
                
        return lista_giocatori
    except Exception as e:
        print(f"Errore caricamento Excel: {e}")
        return []

@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    # Carichiamo tutti i calciatori
    tutti = carica_giocatori_reali()
    
    if not tutti:
        return {
            "status": "error", 
            "messaggio_ai": "Non riesco a leggere il file quotazioni.xlsx", 
            "giocatori": []
        }

    # Restituiamo la lista completa a Flutter
    return {
        "status": "success",
        "messaggio_ai": f"Database caricato con successo! Trovati {len(tutti)} giocatori.",
        "giocatori": tutti 
    }
