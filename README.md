# ⚡ SMOT-KNOWLEDGE

Sistema RAG personale con cervello simulato e curiosità artificiale.
Modello locale su GPU — accesso via tunnel SSH dal Mac.

## 1 Comando — Dal Mac

```bash
# Scarica il launcher
curl -L -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/repos/BigBoss133/SMOT-KNOWLEDGE/contents/smot.py" \
  -o smot.py

# Avvia — sostituisci con l'IP del server Linux
python3 smot.py --host 10.0.0.2
```

Il launcher fa tutto automaticamente:

```
  ✓ SSH: 10.0.0.2 — tunnel via cavo Cat 7
  ✓ Backend: gemma3:4b — 5 documenti in KB
  ✓ Frontend: attivo
  ✓ Tunnel: localhost:8001 ↔ server:8001
  ✓ Browser aperto su http://localhost:5173

  ⚡ SMOT-KNOWLEDGE attivo
  Chat:   http://localhost:5173
  Backend: porta 8001
```

Se la porta 8000 è già occupata, usa automaticamente la prima libera (8001, 8002, ...).

### Altri comandi

```bash
# Solo verifica stato
python3 smot.py --host 10.0.0.2 --status

# Sviluppo locale (senza SSH)
python3 smot.py --local

# Utente SSH personalizzato
python3 smot.py --host 10.0.0.2 --user michele-finocchiaro
```

## Architettura

```
Mac Mini M4 (client)              Linux + RTX 4060 Ti (server)
┌─────────────────┐              ┌──────────────────────────────┐
│  Browser         │──SSH tunnel──▶  Backend FastAPI  :8001     │
│  localhost:5173  │  Cat 7 cable  │  Frontend Vite   :5173     │
│                  │              │  Ollama (gemma3:4b)         │
│  python3 smot.py │              │  RAG (LanceDB)              │
│  (no dip.)       │              │  MCP sequential-thinking    │
└─────────────────┘              │  Sci-Hub via DOI            │
                                  └──────────────────────────────┘
```

## Cosa fa

| Dici | Pipeline |
|------|----------|
| "Spiegami l'attention" | RAG → Sequential Thinking → Ollama → Curiosità |
| "Cerca paper su DOI 10.xxx" | DOI detection → Sci-Hub MCP → Ollama |
| "Cosa c'è nella knowledge base?" | RAG search su LanceDB |

## 9 Fonti di Ricerca

Sci-Hub · Semantic Scholar · arXiv · PubMed · OpenAlex · CORE · Unpaywall · CrossRef · DBLP

## API

| Endpoint | Descrizione |
|----------|-------------|
| `GET /api/health` | Stato backend + modello attivo |
| `GET /api/stats` | Statistiche cervello |
| `GET /api/kb/search?q=` | Ricerca semantica nella KB |
| `POST /api/kb/add` | Aggiunge documento |
| `GET /api/kb/count` | Conteggio documenti |
| `GET /api/knowledge-graph` | Grafo della conoscenza |
| `WS /ws` | Chat streaming + terminale live |

## Modello

**gemma3:4b** su Ollama. ~50 token/s su RTX 4060 Ti.
Sostituibile via `SMOT_MODEL=gemma4:e2b` nel backend.

## Sviluppo in locale

```bash
git clone https://github.com/BigBoss133/SMOT-KNOWLEDGE.git
cd SMOT-KNOWLEDGE

# Backend
cd backend
pip3 install --break-system-packages -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (altro terminale)
cd frontend
npm install
npm run dev
```
