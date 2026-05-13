# ⚡ SMOT-KNOWLEDGE

Sistema RAG personale con cervello simulato e curiosità artificiale.
Modello locale su GPU — accesso via tunnel SSH dal Mac.

## 1 Comando — Dal Mac

```bash
# Scarica il launcher (solo questo file)
curl -O https://raw.githubusercontent.com/BigBoss133/SMOT-KNOWLEDGE/main/smot.py

# Avvia — sostituisci con l'IP del server Linux
python3 smot.py --host 192.168.1.100
```

Lo script verifica subito la connettività SSH, poi:

```
  Verifica tunnel SSH verso 192.168.1.100... ✓

  ⚡ SMOT-KNOWLEDGE
  ────────────────────────────────────────

  ✓ SSH: 192.168.1.100 — tunnel via cavo Cat 7
  ✓ Backend: gemma3:4b — 5 documenti in KB
  ✓ Ollama: attivo
  ✓ Frontend: attivo
  ✓ Tunnel: localhost:8000 ↔ server:8000
  ✓ Browser aperto su http://localhost:5173

  ⚡ SMOT-KNOWLEDGE attivo
  Modello: gemma3:4b
  Chat:   http://localhost:5173
  API:    http://localhost:8000/api/health
  Premi Ctrl+C per fermare tutto
```

### Altri comandi

```bash
# Solo verifica se il server è attivo
python3 smot.py --host 192.168.1.100 --status

# Esecuzione locale (senza SSH, per sviluppo)
python3 smot.py --local

# Specifica utente SSH
python3 smot.py --host 192.168.1.100 --user michele-finocchiaro
```

## Architettura

```
Mac Mini M4 (client)              Linux + RTX 4060 Ti (server)
┌─────────────────┐              ┌──────────────────────────────┐
│  Browser         │──SSH tunnel──▶  Backend FastAPI  :8000     │
│  localhost:5173  │  Cat 7 cable  │  Frontend Vite   :5173     │
│                  │              │  Ollama (gemma3:4b)         │
│  python3 smot.py │              │  RAG (LanceDB)              │
│  (senza dip.)    │              │  MCP sequential-thinking    │
└─────────────────┘              │  Sci-Hub via DOI            │
                                  └──────────────────────────────┘
```

## Cosa fa

| Richiesta | Pipeline |
|-----------|----------|
| "Spiegami l'attention" | RAG → ST → Ollama → Curiosità |
| "Paper su DOI 10.xxx" | DOI detection → Sci-Hub → Ollama |
| "Cerca nella KB" | RAG search su LanceDB |

## 9 Fonti di Ricerca

Sci-Hub · Semantic Scholar · arXiv · PubMed · OpenAlex · CORE · Unpaywall · CrossRef · DBLP

## API

| Endpoint | Cosa restituisce |
|----------|-----------------|
| `GET /api/health` | Stato, modello attivo, conteggio KB |
| `GET /api/stats` | Statistiche cervello (memorie, curiosità) |
| `GET /api/kb/search?q=` | Ricerca semantica nella knowledge base |
| `GET /api/kb/count` | Numero documenti indicizzati |
| `POST /api/kb/add` | Aggiunge documento alla KB |
| `WS /ws` | Chat in tempo reale + log terminale |

## Modello

**gemma3:4b** — 4.3B parametri, Q4_K_M, ~50 token/s su RTX 4060 Ti.
Un modello solo. Sostituibile via `SMOT_MODEL` env var.

## Sviluppo in locale

```bash
git clone https://github.com/BigBoss133/SMOT-KNOWLEDGE.git
cd SMOT-KNOWLEDGE

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```
