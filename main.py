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
        # Saltiamo la prima riga di titolo
        df = pd.read_excel(file_path, skiprows=1)
        df.columns = df.columns.str.strip()

        lista_giocatori = []
        for _, row in df.iterrows():
            nome = str(row.get('Nome', '')).strip()
            if nome == '' or nome == 'nan' or nome == 'Nome':
                continue
            
            # GESTIONE COSTO (Qt. A)
            # Proviamo a prendere il valore dalla colonna 'Qt. A'
            costo_raw = row.get('Qt. A', 0)
            try:
                # Trasformiamo in intero (gestisce sia 25.0 che "25")
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
        print(f"Errore: {e}")
        return []

@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    # Recuperiamo TUTTI i giocatori dal database
    tutti = carica_giocatori_reali()
    
    if not tutti:
        return {"status": "error", "messaggio_ai": "Errore lettura dati", "giocatori": []}

    # Restituiamo la lista intera a Flutter (senza tagli!)
    return {
        "status": "success",
        "messaggio_ai": f"Ho trovato {len(tutti)} giocatori reali per il tuo budget di {request.budget}.",
        "giocatori": tutti # Inviamo l'intera lista
    }
