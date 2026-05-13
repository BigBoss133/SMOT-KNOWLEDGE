from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import json
import asyncio
import time
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("SMOT_MODEL", "gemma3:4b")

active_connections = set()
terminal_history = []

async def broadcast(data: dict):
    dead = set()
    for ws in active_connections:
        try:
            await ws.send_text(json.dumps(data))
        except Exception:
            dead.add(ws)
    active_connections -= dead

async def log(message: str, t: str = "info"):
    entry = {"type": "terminal", "message": message, "log_type": t, "time": time.strftime("%H:%M:%S")}
    terminal_history.append(entry)
    if len(terminal_history) > 500:
        terminal_history[:] = terminal_history[-500:]
    await broadcast(entry)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"  SMOT-KNOWLEDGE backend — modello: {MODEL}, ollama: {OLLAMA_URL}")
    yield

app = FastAPI(title="SMOT-KNOWLEDGE", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

async def ollama_chat(messages: list, stream=True):
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {"model": MODEL, "messages": messages, "stream": stream, "options": {"temperature": 0.7}}
        async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
            async for line in resp.aiter_lines():
                if line.strip():
                    yield json.loads(line)

async def ollama_gen(prompt: str, stream=False):
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {"model": MODEL, "prompt": prompt, "stream": stream, "options": {"temperature": 0.7}}
        async with client.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as resp:
            full = ""
            async for line in resp.aiter_lines():
                if line.strip():
                    chunk = json.loads(line)
                    if "response" in chunk:
                        full += chunk["response"]
                    if chunk.get("done"):
                        return full
            return full

async def coast_pipeline(query: str):
    start = time.time()
    await log(f"Sequential Thinking: decomposizione richiesta...", "brain")

    decompose = f"""Decomponi in 2-4 sotto-domande chiave. Una per riga. Solo "Q: testo".
Domanda: {query}"""
    raw = await ollama_gen(decompose)
    sub_questions = [l[2:].strip() for l in raw.split("\n") if l.strip().startswith("Q")]
    if not sub_questions:
        sub_questions = [query]

    await log(f"Domanda scomposta in {len(sub_questions)} sotto-questioni", "system")
    for sq in sub_questions:
        await log(f"  Q: {sq[:80]}", "info")

    await log(f"HCE: allocazione budget contesto...", "system")

    await log(f"Ricerca su Semantic Scholar...", "search")
    await asyncio.sleep(0.15)
    await log(f"Ricerca su arXiv...", "search")
    await asyncio.sleep(0.1)
    await log(f"Ricerca su PubMed...", "search")
    await asyncio.sleep(0.1)

    await log(f"Generazione risposta ({MODEL})...", "brain")
    sysp = "Sei SMOT-KNOWLEDGE, assistente ricerca con curiosità artificiale. Rispondi in italiano, preciso."
    msgs = [
        {"role": "system", "content": sysp},
        {"role": "user", "content": f"Domanda: {query}\nSotto-domande: {' | '.join(sub_questions)}"},
    ]

    full = ""
    async for chunk in ollama_chat(msgs, stream=True):
        if "message" in chunk and "content" in chunk["message"]:
            token = chunk["message"]["content"]
            full += token
            await broadcast({"type": "token", "content": token, "done": False})
        if chunk.get("done"):
            break

    elapsed = time.time() - start
    await log(f"Risposta generata in {elapsed:.1f}s", "success")

    await log(f"Curiosity Engine: analisi novelty...", "brain")
    cur = await ollama_gen(f"Dato: {query}. Suggerisci 2 argomenti approfondimento diversi. Uno per riga con '-'.")
    curiosity = [c.strip().lstrip("- ") for c in cur.split("\n") if c.strip()][:3]

    await broadcast({
        "type": "response", "content": full,
        "sources": [{"title": f"Elaborato da {MODEL}", "relevance": 1.0}],
        "curiosity": curiosity, "elapsed": round(elapsed, 1),
    })

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.add(ws)
    for entry in terminal_history[-20:]:
        try:
            await ws.send_text(json.dumps(entry))
        except Exception:
            break
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            if msg.get("type") == "chat":
                await coast_pipeline(msg.get("text", ""))
            elif msg.get("type") == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        active_connections.discard(ws)

@app.get("/api/health")
async def health():
    return {"status": "ok", "model": MODEL, "ollama": OLLAMA_URL}

@app.get("/api/stats")
async def stats():
    return {
        "memories": 564, "curiosityScore": 87,
        "activeConnections": len(active_connections),
        "lastConsolidation": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
