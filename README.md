# ⚡ SMOT-KNOWLEDGE

Sistema RAG personale con cervello simulato e curiosità artificiale.
Modello locale su GPU — accesso via tunnel SSH dal Mac.

## Tunnel SSH — Dal Mac al server Linux

```bash
# Collega le porte (sostituisci 10.0.0.2 con l'IP del server)
ssh -L 5173:localhost:5173 -L 8001:localhost:8001 michele-finocchiaro@10.0.0.2
```

Poi apri `http://localhost:5173` nel browser del Mac.

## Launcher automatico

Scarica ed esegui — fa tutto da solo (SSH tunnel + avvio servizi + browser):

```bash
curl -L -H "Accept: application/vnd.github.raw" \
  "https://api.github.com/repos/BigBoss133/SMOT-KNOWLEDGE/contents/smot.py" \
  -o smot.py

python3 smot.py --host 10.0.0.2
```

Il launcher verifica la connessione, avvia backend/frontend se necessario,
crea il tunnel SSH e apre il browser. Output tipico:

```
  ✓ SSH: 10.0.0.2
  ✓ Backend: gemma3:4b
  ✓ Frontend: attivo
  ✓ Tunnel: localhost:8001 ↔ server:8001
  ✓ Browser aperto su http://localhost:5173
```

La porta del backend è dinamica — se 8000 è occupata usa 8001, 8002, ecc.

### Comandi utili

```bash
# Solo verifica stato remoto
python3 smot.py --host 10.0.0.2 --status

# Sviluppo locale (senza SSH)
python3 smot.py --local

# Utente SSH diverso
python3 smot.py --host 10.0.0.2 --user michele-finocchiaro
```

### Se la UI mostra "Backend non connesso"

```bash
# 1. Verifica che il backend sia raggiungibile via tunnel
curl -sf http://localhost:8001/api/health
# Se risponde → il tunnel funziona

# 2. Se non risponde, riavvia i servizi sul server:
ssh michele-finocchiaro@10.0.0.2 "
  cd /home/michele-finocchiaro/SMOT-KNOWLEDGE/backend
  nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/smot-be.log 2>&1 &
  cd /home/michele-finocchiaro/SMOT-KNOWLEDGE/frontend
  SMOT_BACKEND_PORT=8001 nohup npm run dev > /tmp/smot-fe.log 2>&1 &
"

# 3. Tunnel SSH e ricarica http://localhost:5173
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
