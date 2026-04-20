from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import random

app = FastAPI()

# Configurazione CORS: permette a Flutter di comunicare con il backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schema dei dati in arrivo da Flutter
class PlannerRequest(BaseModel):
    budget: int
    strategy: str

# Funzione per caricare i dati reali dal file Excel caricato su GitHub
def carica_giocatori_reali():
    file_path = "quotazioni.xlsx"
    
    # Verifica se il file esiste nel repository
    if not os.path.exists(file_path):
        print("ERRORE: File quotazioni.xlsx non trovato nel server.")
        return []
    
    try:
        # Legge l'Excel. 
        # NOTA: skiprows=1 serve perché l'export di Fantacalcio ha solitamente 
        # una riga di intestazione grafica prima dei nomi delle colonne.
        df = pd.read_excel(file_path, skiprows=1)
        
        # Pulisce i nomi delle colonne eliminando eventuali spazi bianchi
        df.columns = df.columns.str.strip()

        lista_giocatori = []
        for _, row in df.iterrows():
            # Mappiamo le colonne dell'Excel (R, Nome, Squadra, Qt. A)
            # alle chiavi contratte che Flutter si aspetta (r, n, s, q)
            try:
                # Usiamo .get per evitare crash se mancano dati in una riga
                nome = str(row.get('Nome', 'Sconosciuto'))
                ruolo = str(row.get('R', 'N/D'))
                squadra = str(row.get('Squadra', 'N/D'))
                # Converte la quotazione in intero, default 0 se non valida
                quotazione = int(row.get('Qt. A', 0))
                
                if nome != 'nan' and nome != 'Sconosciuto':
                    lista_giocatori.append({
                        "n": nome,
                        "r": ruolo,
                        "s": squadra,
                        "q": quotazione
                    })
            except Exception:
                continue # Salta righe malformate
                
        return lista_giocatori
    except Exception as e:
        print(f"Errore critico nella lettura dell'Excel: {e}")
        return []

@app.get("/")
def read_root():
    """Rotta di test per verificare lo stato del server"""
    file_presente = os.path.exists("quotazioni.xlsx")
    return {
        "status": "Online",
        "database_presente": file_presente,
        "info": "Fanta AI Backend con dati reali caricati."
    }

@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    """Logica di ottimizzazione (per ora restituisce una lista filtrata)"""
    tutti_i_giocatori = carica_giocatori_reali()
    
    if not tutti_i_giocatori:
        return {
            "status": "error",
            "messaggio_ai": "Non sono riuscito a caricare i dati reali dal database.",
            "giocatori": []
        }

    # --- LOGICA TEMPORANEA DI SELEZIONE ---
    # Qui l'AI filtrerà i giocatori in base al budget e alla strategia.
    # Per ora, prendiamo una selezione casuale che rispetta il budget totale.
    random.shuffle(tutti_i_giocatori)
    squadra_selezionata = []
    budget_usato = 0
    
    for p in tutti_i_giocatori:
        # Se il giocatore costa meno di quanto rimasto e non abbiamo ancora 15 giocatori
        if p['q'] > 0 and (budget_usato + p['q']) <= request.budget and len(squadra_selezionata) < 15:
            squadra_selezionata.append(p)
            budget_usato += p['q']

    return {
        "status": "success",
        "messaggio_ai": f"Ho analizzato {len(tutti_i_giocatori)} giocatori reali. Ecco una bozza basata sulla strategia {request.strategy}.",
        "giocatori": squadra_selezionata,
        "budget_rimanente": request.budget - budget_usato
    }
