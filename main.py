from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Definiamo cosa ci aspettiamo di ricevere da Flutter
class PlannerRequest(BaseModel):
    budget: int
    strategy: String

# Modello per il giocatore singolo
class Player(BaseModel):
    nome: str
    ruolo: str
    costo: int

# Rotta principale per l'ottimizzazione
@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    # QUI ANDRÀ IL TUO ALGORITMO (Knapsack o AI Agent)
    # Per ora simuliamo una risposta intelligente
    
    suggerimenti = []
    if request.strategy == "Aggressiva":
        suggerimenti = [
            {"nome": "Lautaro Martinez", "ruolo": "A", "costo": 150},
            {"nome": "Leao", "ruolo": "A", "costo": 100}
        ]
    else:
        suggerimenti = [
            {"nome": "Di Lorenzo", "ruolo": "D", "costo": 20},
            {"nome": "Calhanoglu", "ruolo": "C", "costo": 45}
        ]

    return {
        "status": "success",
        "budget_usato": sum(p["costo"] for p in suggerimenti),
        "consiglio_ai": f"Con una strategia {request.strategy}, ho dato priorità ai bonus immediati.",
        "giocatori": suggerimenti
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)