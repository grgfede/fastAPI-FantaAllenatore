from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Configurazione CORS per permettere a Flutter di chiamare il server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definiamo lo schema dei dati che arrivano da Flutter
class PlannerRequest(BaseModel):
    budget: int
    strategy: str

# Rotta Home (per testare se il server è vivo dal browser)
@app.get("/")
def read_root():
    return {"status": "Online", "message": "Fanta AI Backend pronto!"}

# Rotta di Ottimizzazione
@app.post("/optimize")
async def optimize_squad(request: PlannerRequest):
    # Logica temporanea di risposta
    return {
        "status": "success",
        "messaggio_ai": f"Analisi completata per budget {request.budget} con strategia {request.strategy}.",
        "giocatori": [
            {"nome": "Maignan", "ruolo": "P", "costo": 25},
            {"nome": "Lautaro", "ruolo": "A", "costo": 120}
        ]
    }
