"""Chroma-backed chunk store with incremental, hash-based ingestion."""
from __future__ import annotations

import re
from dataclasses import dataclass

import chromadb

from .chunker import Chunk, chunk_document
from .embedder import Embedder
from .parser import OKFDocument, slug


def _coll_name(embedder_name: str) -> str:
    return "okf_" + re.sub(r"[^a-zA-Z0-9._-]+", "_", embedder_name)[:100]


@dataclass
class IngestReport:
    docs: int
    chunks_total: int
    added: int
    unchanged: int
    deleted: int


class OKFStore:
    def __init__(self, persist_dir: str, embedder: Embedder):
        self.embedder = embedder
        self.client = chromadb.PersistentClient(path=persist_dir)
        # one collection per embedder: vector dimensions must never be mixed
        self.col = self.client.get_or_create_collection(
            _coll_name(embedder.name), metadata={"hnsw:space": "cosine"}
        )

    # ---------- ingest ----------
    @staticmethod
    def _meta(doc: OKFDocument, ch: Chunk) -> dict:
        m = {
            "doc_id": ch.doc_id, "title": ch.title, "heading_path": ch.heading_path,
            "type": doc.type, "ordinal": ch.ordinal, "hash": ch.content_hash,
            "slug": slug(ch.doc_id.split("/")[-1]),
            "links": "|".join(doc.links),
        }
        for t in doc.tags:           # chroma has no list metadata -> one bool key per tag
            m[f"tag_{slug(t)}"] = True
        return m

    def ingest(self, docs: list[OKFDocument], max_chars: int = 1200) -> IngestReport:
        existing = self.col.get(include=["metadatas"])
        old = {i: m["hash"] for i, m in zip(existing["ids"], existing["metadatas"])}

        want: dict[str, tuple[OKFDocument, Chunk]] = {}
        for d in docs:
            for ch in chunk_document(d, max_chars=max_chars):
                want[ch.chunk_id] = (d, ch)

        to_add = [cid for cid, (_, ch) in want.items() if old.get(cid) != ch.content_hash]
        stale = [cid for cid in old if cid not in want]
        if stale:
            self.col.delete(ids=stale)
        if to_add:
            embs = self.embedder.embed([want[c][1].embed_text for c in to_add])
            self.col.upsert(
                ids=to_add, embeddings=embs,
                documents=[want[c][1].text for c in to_add],
                metadatas=[self._meta(*want[c]) for c in to_add],
            )
        return IngestReport(len(docs), len(want), len(to_add),
                            len(want) - len(to_add), len(stale))

    # ---------- query ----------
    def search(self, query: str, n: int, where: dict | None = None):
        emb = self.embedder.embed([query])[0]
        n = max(1, min(n, self.col.count() or 1))
        r = self.col.query(query_embeddings=[emb], n_results=n, where=where,
                           include=["documents", "metadatas", "distances"])
        out = []
        for cid, doc, meta, dist in zip(r["ids"][0], r["documents"][0],
                                        r["metadatas"][0], r["distances"][0]):
            out.append({"id": cid, "text": doc, "meta": meta, "score": 1.0 - dist})
        return out

    def first_chunks_by_slug(self, slugs: list[str]):
        if not slugs:
            return []
        r = self.col.get(
            where={"$and": [{"ordinal": 0}, {"slug": {"$in": slugs}}]},
            include=["documents", "metadatas"],
        )
        return [{"id": i, "text": d, "meta": m}
                for i, d, m in zip(r["ids"], r["documents"], r["metadatas"])]

    def all_docs_text(self) -> dict[str, str]:
        r = self.col.get(include=["documents", "metadatas"])
        by: dict[str, list[tuple[int, str]]] = {}
        for d, m in zip(r["documents"], r["metadatas"]):
            by.setdefault(m["doc_id"], []).append((m["ordinal"], d))
        return {k: "\n\n".join(t for _, t in sorted(v)) for k, v in by.items()}
