
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import yaml, os, sqlite3, time, pathlib

app = FastAPI(title="VoiceAI Orchestrator", version="0.1.0")

DB_PATH = os.environ.get("DB_PATH", "/app/data/voiceai.db")
FLOWS_DIR = pathlib.Path("/app/flows")

class Outcome(BaseModel):
    call_id: str
    customer: str
    intent: str
    data: dict

def init_db():
    os.makedirs("/app/data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER,
                call_id TEXT,
                customer TEXT,
                intent TEXT,
                data TEXT
            )
        """)
init_db()

@app.get("/healthz")
def health():
    return {"ok": True}

@app.get("/docs-note")
def docs_note():
    return JSONResponse({"note": "FastAPI auto-docs at /docs"})

@app.get("/flows")
def list_flows():
    items = []
    for p in FLOWS_DIR.glob("*.yaml"):
        items.append(p.name)
    return {"flows": items}

@app.get("/flows/{name}")
def get_flow(name: str):
    p = FLOWS_DIR / name
    if not p.exists():
        raise HTTPException(404, "Flow not found")
    return yaml.safe_load(p.read_text())

class OutcomeIn(BaseModel):
    call_id: str
    customer: str
    intent: str
    data: dict

@app.post("/outcome")
def save_outcome(outcome: OutcomeIn):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO outcomes (ts, call_id, customer, intent, data) VALUES (?,?,?,?,?)",
            (int(time.time()), outcome.call_id, outcome.customer, outcome.intent, yaml.safe_dump(outcome.data)),
        )
    return {"status": "saved"}

# TODO:
# - Implement Asterisk ARI control and media bridging to Azure Speech.
# - STT/TTS clients (httpx websockets) with streaming.
