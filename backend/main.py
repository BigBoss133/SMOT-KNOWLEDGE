from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import json
import asyncio
import time
import os
import re

from mcp_manager import mcp_manager
from rag_engine import rag

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("SMOT_MODEL", "gemma3:4b")

active_connections = set()
terminal_history = []

knowledge_graph = {
    "nodes": [
        {"id": "attention", "label": "Attention Mechanism", "category": "core", "connections": ["transformer", "rag"]},
        {"id": "transformer", "label": "Transformer", "category": "architecture", "connections": ["attention", "llm"]},
        {"id": "llm", "label": "Large Language Models", "category": "architecture", "connections": ["transformer", "rlhf", "rag"]},
        {"id": "rlhf", "label": "RLHF", "category": "training", "connections": ["llm", "alignment"]},
        {"id": "rag", "label": "RAG", "category": "system", "connections": ["llm", "attention", "embeddings"]},
        {"id": "embeddings", "label": "Embeddings", "category": "core", "connections": ["rag", "lancedb"]},
        {"id": "lancedb", "label": "Vector Store", "category": "system", "connections": ["embeddings", "rag"]},
        {"id": "alignment", "label": "Alignment", "category": "training", "connections": ["rlhf", "llm"]},
        {"id": "moe", "label": "Mixture of Experts", "category": "architecture", "connections": ["llm"]},
    ],
    "curiosities": [],
}

DOI_RE = re.compile(r'\b(10\.\d{4,}/[^\s,;)\]]+)')

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
    await mcp_manager.init()
    c = await rag.count()
    print(f"  SMOT-KNOWLEDGE — modello: {MODEL}, RAG: {c} documenti, MCP: st + scihub")
    yield
    await mcp_manager.close_all()

app = FastAPI(title="SMOT-KNOWLEDGE", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

async def ollama_chat(messages: list, stream=True):
    async with httpx.AsyncClient(timeout=120.0) as c:
        payload = {"model": MODEL, "messages": messages, "stream": stream, "options": {"temperature": 0.7}}
        async with c.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
            async for line in resp.aiter_lines():
                if line.strip():
                    yield json.loads(line)

async def ollama_gen(prompt: str):
    async with httpx.AsyncClient(timeout=60.0) as c:
        payload = {"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.7}}
        async with c.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as resp:
            full = ""
            async for line in resp.aiter_lines():
                if line.strip():
                    chunk = json.loads(line)
                    if "response" in chunk:
                        full += chunk["response"]
                    if chunk.get("done"):
                        return full
            return full if full else ""

async def coast_pipeline(query: str):
    start = time.time()
    await log(f"Sequential Thinking: analisi richiesta...", "brain")

    # FASE 0: RAG — cerca nella knowledge base locale
    rag_results = await rag.search(query, top_k=3)
    if rag_results:
        await log(f"RAG: trovati {len(rag_results)} documenti correlati", "success")
    else:
        await log(f"RAG: nessun documento correlato trovato", "info")

    # FASE 0b: DOI detection → Sci-Hub
    dois = DOI_RE.findall(query)
    paper_texts = []
    for doi in dois:
        doi = doi.rstrip(".,;:)!?")
        await log(f"DOI rilevato: {doi} — fetch da Sci-Hub...", "search")
        paper = await mcp_manager.fetch_paper(doi)
        if paper:
            paper_texts.append(f"[Paper {doi}]: {paper[:1500]}")
            await log(f"Paper {doi} recuperato", "success")
        else:
            await log(f"Paper {doi} non disponibile", "error")

    # FASE 1: Sequential Thinking
    thoughts = [
        f"Decomponi in sotto-problemi: {query}",
        f"Quali connessioni tra questi concetti?",
    ]
    try:
        st_result = await mcp_manager.sequential_think(thoughts)
        await log(f"Sequential Thinking completato", "success")
    except Exception as e:
        st_result = ""
        await log(f"ST: {e}", "error")

    # FASE 1b: decomposizione
    raw = await ollama_gen(
        f'Decomponi in 2-4 sotto-domande chiave. Una per riga. Solo "Q: testo".\nDomanda: {query}'
    )
    sub_questions = [l[2:].strip() for l in raw.split("\n") if l.strip().startswith("Q")]
    if not sub_questions:
        sub_questions = [query]
    await log(f"Scomposta in {len(sub_questions)} sotto-questioni", "system")

    await log(f"Generazione risposta ({MODEL})...", "brain")

    # Assembla contesto
    ctx = [f"Sotto-domande: {' | '.join(sub_questions)}"]
    if st_result:
        ctx.append(f"Analisi: {st_result[:300]}")
    if rag_results:
        ctx.append("Documenti correlati:")
        for r in rag_results:
            ctx.append(f"- {r['text'][:200]}")
    if paper_texts:
        ctx.extend(paper_texts)

    msgs = [
        {"role": "system", "content": "Sei SMOT-KNOWLEDGE, assistente ricerca con RAG e cervello simulato. Rispondi in italiano, preciso."},
        {"role": "user", "content": f"Domanda: {query}\n\n{' '.join(ctx)}"},
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

    # FASE 5: Curiosity + aggiorna KB
    await log(f"Curiosity Engine + aggiornamento Knowledge Base...", "brain")
    cur = await ollama_gen(
        f"Dato: {query}. Suggerisci 2 argomenti approfondimento diversi. Uno per riga con '-'."
    )
    curiosity = [c.strip().lstrip("- ") for c in cur.split("\n") if c.strip()][:3]

    auto_store = await ollama_gen(
        f"Riassumi in 2-3 righe il concetto principale di: {query}"
    )
    if auto_store and len(auto_store) > 20:
        await rag.add_document(
            f"{query}\n{auto_store}",
            {"type": "auto", "source": MODEL, "timestamp": time.time()},
        )
        await log(f"Knowledge Base aggiornata", "system")

    kg = knowledge_graph
    for c in curiosity:
        safe_id = re.sub(r'\W+', '_', c.lower().strip())[:20]
        if not any(n["id"] == safe_id for n in kg["nodes"]):
            kg["nodes"].append(
                {"id": safe_id, "label": c[:25], "category": "curiosity", "connections": []}
            )
    kg["curiosities"] = curiosity

    sources = [{"title": f"Elaborato da {MODEL}", "relevance": 1.0}]
    if rag_results:
        sources.append({"title": f"KB: {len(rag_results)} documenti", "relevance": 0.9})
    if paper_texts:
        sources.append({"title": f"Sci-Hub: {len(paper_texts)} paper", "relevance": 0.85})

    await broadcast({
        "type": "response", "content": full,
        "sources": sources,
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
    return {"status": "ok", "model": MODEL, "ollama": OLLAMA_URL, "rag_docs": await rag.count()}

@app.get("/api/stats")
async def stats():
    return {
        "memories": await rag.count() + len(knowledge_graph["nodes"]),
        "curiosityScore": min(99, 70 + len(knowledge_graph["curiosities"]) * 5),
        "activeConnections": len(active_connections),
        "lastConsolidation": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

@app.get("/api/knowledge-graph")
async def get_kg():
    return knowledge_graph

@app.post("/api/kb/add")
async def kb_add(doc: dict):
    text = doc.get("text", "")
    if not text:
        raise HTTPException(400, "text required")
    meta = doc.get("metadata", {})
    await rag.add_document(text, meta)
    return {"status": "ok", "docs": await rag.count()}

@app.get("/api/kb/search")
async def kb_search(q: str = "", top_k: int = 5):
    if not q:
        return []
    results = await rag.search(q, top_k)
    return results

@app.get("/api/kb/count")
async def kb_count():
    return {"count": await rag.count()}

@app.delete("/api/kb/clear")
async def kb_clear():
    await rag.clear()
    return {"status": "ok", "count": 0}
