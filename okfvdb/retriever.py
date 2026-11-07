"""Budget-based retrieval.

No fixed top-k and no re-ranker. Instead:
  1. metadata pre-filter (type / tags from OKF frontmatter)
  2. vector search over a generous candidate pool
  3. adaptive cut: absolute min_score AND relative cutoff vs the best hit
  4. greedy pack into a token budget
  5. optional link expansion: pull the lead chunk of docs linked from top hits
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .parser import slug
from .store import OKFStore
from .tokens import count_tokens


@dataclass
class Hit:
    chunk_id: str
    doc_id: str
    title: str
    heading_path: str
    text: str
    score: float
    tokens: int
    via: str = "vector"   # "vector" | "link"


@dataclass
class Result:
    hits: list[Hit] = field(default_factory=list)
    tokens_used: int = 0

    def context(self) -> str:
        parts = [f"[{h.doc_id} › {h.heading_path}]\n{h.text}" for h in self.hits]
        return "\n\n---\n\n".join(parts)


def _where(doc_type: str | None, tags: list[str] | None) -> dict | None:
    conds = []
    if doc_type:
        conds.append({"type": doc_type})
    for t in tags or []:
        conds.append({f"tag_{slug(t)}": True})
    if not conds:
        return None
    return conds[0] if len(conds) == 1 else {"$and": conds}


def retrieve(store: OKFStore, query: str, *, budget_tokens: int = 600,
             candidates: int = 20, min_score: float = 0.15, rel_cutoff: float = 0.7,
             doc_type: str | None = None, tags: list[str] | None = None,
             expand_links: bool = False) -> Result:
    raw = store.search(query, candidates, _where(doc_type, tags))
    res = Result()
    if not raw:
        return res

    best = raw[0]["score"]
    keep = [r for r in raw if r["score"] >= max(min_score, best * rel_cutoff)]
    if not keep:                 # never return nothing when something matched
        keep = raw[:1]

    seen: set[str] = set()

    def add(r, via, score):
        if r["id"] in seen:
            return False
        t = count_tokens(r["text"])
        if res.tokens_used + t > budget_tokens and res.hits:
            return False
        m = r["meta"]
        res.hits.append(Hit(r["id"], m["doc_id"], m["title"], m["heading_path"],
                            r["text"], score, t, via))
        res.tokens_used += t
        seen.add(r["id"])
        return True

    for r in keep:
        add(r, "vector", r["score"])

    if expand_links:
        targets: list[str] = []
        for r in keep[:3]:
            targets += [s for s in r["meta"].get("links", "").split("|") if s]
        have_docs = {h.doc_id for h in res.hits}
        for r in store.first_chunks_by_slug(list(dict.fromkeys(targets))):
            if r["meta"]["doc_id"] not in have_docs:
                add(r, "link", best * 0.5)
    return res
