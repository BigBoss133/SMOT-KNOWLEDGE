# ⚡ SMOT-KNOWLEDGE

> Sistema RAG personale con cervello simulato e curiosità artificiale.

SMOT-KNOWLEDGE è un sistema di **Retrieval-Augmented Generation** personale che rende intelligenti anche modelli con pochi parametri attraverso MCP dedicati, sequential thinking e un motore di curiosità simulato.

## Architettura

```
frontend/    → Svelte 5 + Vite + Tailwind (UI)
backend/     → Python FastAPI + WebSocket (API + orchestrazione)
mcp/         → Custom MCP servers
```

### COAST Algorithm

Ogni prompt attraversa l'algoritmo **Context-Optimized Augmented Sequential Thinking**:

1. **Gate** — classifica la richiesta
2. **Sequential Decompose** — scomposizione in sotto-questioni
3. **Context Budget** — allocazione token via HCE
4. **Parallel Retrieval** — ricerca su 9 fonti
5. **Curiosity Bias** — novelty scoring + rerank
6. **Reasoning** — risposta finale con citazioni

### 9 Fonti di Ricerca

Sci-Hub · Semantic Scholar · arXiv · PubMed · OpenAlex · CORE · Unpaywall · CrossRef · DBLP

## Requisiti

- Node.js 20+
- Python 3.12+
- NVIDIA GPU (consigliata: RTX 4060 Ti 8GB)
- Ollama con modelli locali

## Sviluppo

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
