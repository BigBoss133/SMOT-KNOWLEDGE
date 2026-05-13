import os
import time
import lancedb
import httpx
import numpy as np
from typing import Optional

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("SMOT_EMBED_MODEL", "qwen2.5-coder:7b")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lancedb")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class RAGEngine:
    def __init__(self):
        self.db = lancedb.connect(DB_PATH)
        self._table = None

    @property
    def table(self):
        if self._table is None:
            try:
                self._table = self.db.open_table("knowledge")
            except Exception:
                self._table = None
        return self._table

    async def embed(self, text: str) -> list:
        async with httpx.AsyncClient(timeout=30.0) as c:
            r = await c.post(f"{OLLAMA_URL}/api/embeddings", json={
                "model": EMBED_MODEL, "prompt": text,
            })
            return r.json().get("embedding", [])

    async def add_document(self, text: str, metadata: Optional[dict] = None):
        if not text.strip():
            return
        emb = await self.embed(text[:2000])
        if not emb or len(emb) == 0:
            return
        vec = np.array([emb], dtype=np.float32)
        tbl = self.table
        record = {
            "vector": vec[0].tolist(),
            "text": text[:5000],
            "metadata": metadata or {},
            "created_at": time.time(),
        }
        if tbl is None:
            self._table = self.db.create_table("knowledge", data=[record])
        else:
            tbl.add([record])

    async def add_documents(self, docs: list):
        for doc in docs:
            text = doc if isinstance(doc, str) else doc.get("text", "")
            meta = None if isinstance(doc, str) else doc.get("metadata")
            await self.add_document(text, meta)

    async def search(self, query: str, top_k: int = 5) -> list:
        tbl = self.table
        if tbl is None:
            return []
        emb = await self.embed(query)
        if not emb or len(emb) == 0:
            return []
        try:
            results = tbl.search(emb).limit(top_k).to_list()
            return [
                {
                    "text": r["text"],
                    "metadata": r.get("metadata", {}),
                    "_distance": float(r.get("_distance", 0)),
                }
                for r in results
            ]
        except Exception as e:
            print(f"  RAG search error: {e}")
            return []

    async def count(self) -> int:
        tbl = self.table
        if tbl is None:
            return 0
        return tbl.count_rows()

    async def clear(self):
        try:
            self.db.drop_table("knowledge")
        except Exception as e:
            print(f"  RAG clear: {e}")
        self._table = None


rag = RAGEngine()
