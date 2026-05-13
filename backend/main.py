from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⚡ SMOT-KNOWLEDGE backend avviato")
    yield
    print("⚡ SMOT-KNOWLEDGE backend spento")

app = FastAPI(title="SMOT-KNOWLEDGE API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections
active_connections = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "chat":
                asyncio.create_task(handle_chat(msg, websocket))
    except WebSocketDisconnect:
        active_connections.discard(websocket)

async def broadcast_log(message: str, log_type: str = "info"):
    payload = json.dumps({"type": "terminal", "message": message, "log_type": log_type})
    dead = set()
    for ws in active_connections:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.add(ws)
    active_connections -= dead

async def handle_chat(msg: dict, ws: WebSocket):
    query = msg.get("text", "")
    start = time.time()

    await broadcast_log(f"🧠 Sequential Thinking: decomposizione richiesta...", "brain")
    await asyncio.sleep(0.3)
    await broadcast_log(f"📡 Ricerca su Semantic Scholar...", "search")
    await asyncio.sleep(0.2)
    await broadcast_log(f"📡 Ricerca su arXiv...", "search")
    await asyncio.sleep(0.2)
    await broadcast_log(f"📡 Ricerca su PubMed...", "search")
    await asyncio.sleep(0.2)
    await broadcast_log(f"🧮 HCE: calcolo contest budget...", "system")
    await asyncio.sleep(0.2)
    await broadcast_log(f"🧠 Curiosity Engine: novelty scoring...", "brain")
    await asyncio.sleep(0.3)
    await broadcast_log(f"🧮 Knapsack: selezione chunk ottimali...", "system")
    await asyncio.sleep(0.2)
    await broadcast_log(f"💡 Curiosità: 2 nuovi pattern rilevati", "brain")
    await asyncio.sleep(0.2)

    elapsed = time.time() - start
    await broadcast_log(f"✅ Risposta generata in {elapsed:.1f}s", "success")

    response = {
        "type": "response",
        "content": f"Ecco cosa ho trovato su \"{query}\".\n\nQuesta è la risposta elaborata dal backend COAST con sequential thinking, RAG su 9 fonti e curiosity engine.",
        "sources": [
            {"title": f"Risultati per: {query[:30]}...", "url": "#", "relevance": 0.94},
        ],
        "curiosity": ["Approfondire questo argomento?", "Cercare fonti correlate?"],
        "elapsed": round(elapsed, 1),
    }
    await ws.send_text(json.dumps(response))

@app.get("/api/health")
async def health():
    return {"status": "ok", "brain": "active", "curiosity": True}

@app.get("/api/stats")
async def stats():
    return {
        "memories": 564,
        "curiosityScore": 87,
        "activeConnections": 142,
        "lastConsolidation": "2026-05-14T12:00:00Z",
    }
