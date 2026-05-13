# ⚡ SMOT-KNOWLEDGE

> Sistema RAG personale con cervello simulato e curiosità artificiale.
> Modelli locali su GPU (RTX 4060 Ti) — UI accessibile via tunnel SSH dal Mac.

## Architettura

```
Mac Mini M4 (client)              Linux + RTX 4060 Ti (server)
┌─────────────────┐              ┌──────────────────────────┐
│  Browser         │──SSH tunnel──▶  Backend FastAPI :8000  │
│  http://localhost│  Cat 7 cable  │  Frontend Vite   :5173  │
│  :5173           │              │  Ollama (gemma3:4b)     │
│                  │              │  MCP sequential-thinking│
│  python3 smot.py │              │  RAG engine (LanceDB)   │
└─────────────────┘              │  Sci-Hub MCP            │
                                  └──────────────────────────┘
```

## Per avviare — 1 comando dal Mac

```bash
# Scarica solo il launcher
curl -O https://raw.githubusercontent.com/BigBoss133/SMOT-KNOWLEDGE/main/smot.py

# Avvia tutto (auto-detect IP, forwarding, browser)
python3 smot.py --host <IP-DEL-LINUX>
```

Lo script:
1. Si connette via SSH al server Linux
2. Verifica che Ollama, backend e frontend siano attivi
3. Se non lo sono, li avvia automaticamente
4. Crea tunnel SSH con port forwarding (`-L 8000 -L 5173`)
5. Apre il browser sul Mac su `http://localhost:5173`
6. Resta in esecuzione — premere Ctrl+C per fermare tutto

### Tunnel SSH via cavo Cat 7

Dato che Mac e Linux sono collegati direttamente via cavo Ethernet,
la latenza è minima e la velocità massima. Lo script usa SSH con
`ServerAliveInterval=30` per mantenere il tunnel stabile.

### Comandi utili

```bash
# Solo verifica stato remoto
python3 smot.py --host 192.168.1.100 --status

# Specifica utente SSH diverso
python3 smot.py --host 192.168.1.100 --user michele-finocchiaro

# Esecuzione locale (senza SSH, per test)
python3 smot.py --local

# Aiuto completo
python3 smot.py --help
```

### Output tipico

```
  ⚡ SMOT-KNOWLEDGE — Remote Launcher
  
  ✓ SSH: 192.168.1.100  
  ✓ Ollama: 6 modelli — gemma3:4b, qwen2.5-coder:7b, ...
  ✓ Backend: gemma3:4b — 5 documenti in KB
  ✓ Frontend: attivo
  ✓ Port forwarding: localhost:8000 → server:8000
  ✓ Browser aperto su http://localhost:5173
  
  ⚡ SMOT-KNOWLEDGE attivo!
  Chat:   http://localhost:5173
  API:    http://localhost:8000/api/health
  Premere Ctrl+C per terminare tutto
```

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Backend | Python FastAPI + WebSocket |
| Frontend | Svelte 5 + Vite + Tailwind + TypeScript |
| LLM | Ollama (gemma3:4b, qwen2.5-coder:7b) |
| MCP | Sequential Thinking + Sci-Hub custom |
| Vector Store | LanceDB (embeddings qwen2.5-coder:7b) |
| GPU | NVIDIA RTX 4060 Ti 8GB |

## Pipeline COAST

Ogni richiesta attraversa:

```
Query → RAG search (LanceDB) → DOI detection (Sci-Hub) →
Sequential Thinking (MCP) → Decomposizione (Ollama) →
Generazione streaming (Ollama) → Curiosity Engine →
Auto-store nella Knowledge Base
```

## 9 Fonti di Ricerca

Sci-Hub · Semantic Scholar · arXiv · PubMed · OpenAlex · CORE · Unpaywall · CrossRef · DBLP

## API

| Endpoint | Descrizione |
|----------|-------------|
| `GET /api/health` | Stato backend + conteggio KB |
| `GET /api/stats` | Statistiche cervello |
| `GET /api/knowledge-graph` | Grafo della conoscenza |
| `GET /api/kb/search?q=...` | Ricerca semantica nella KB |
| `POST /api/kb/add` | Aggiungi documento alla KB |
| `GET /api/kb/count` | Conteggio documenti |
| `DELETE /api/kb/clear` | Pulisci KB |
| `WS /ws` | WebSocket per chat + terminale live |

## Sviluppo

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

Poi apri `http://localhost:5173` — la chat parla con Gemma3 via Ollama.
