from pathlib import Path

from okfvdb.chunker import chunk_document
from okfvdb.embedder import HashEmbedder
from okfvdb.parser import load_corpus, parse_okf
from okfvdb.retriever import retrieve
from okfvdb.store import OKFStore

KB = Path(__file__).resolve().parents[1] / "knowledge"


def test_parse_frontmatter_and_links():
    d = parse_okf(KB / "concepts" / "okf.md", KB)
    assert d.doc_id == "concepts/okf"
    assert d.type == "concept" and "okf" in d.tags
    assert "rag-overview" in d.links and "vector-databases" in d.links


def test_chunks_follow_headings():
    d = parse_okf(KB / "concepts" / "chunking.md", KB)
    paths = [c.heading_path for c in chunk_document(d, min_chars=10)]
    assert any("Parent-child" in p for p in paths)
    assert all(c.embed_text.startswith(d.title) for c in chunk_document(d))


def _store(tmp_path):
    return OKFStore(str(tmp_path / "db"), HashEmbedder())


def test_incremental_ingest(tmp_path):
    s, docs = _store(tmp_path), load_corpus(KB)
    r1 = s.ingest(docs)
    assert r1.added == r1.chunks_total and r1.deleted == 0
    r2 = s.ingest(docs)
    assert r2.added == 0 and r2.unchanged == r1.chunks_total
    r3 = s.ingest(docs[:-1])           # a file was removed
    assert r3.deleted > 0


def test_retrieve_within_budget_and_filters(tmp_path):
    s = _store(tmp_path)
    s.ingest(load_corpus(KB))
    res = retrieve(s, "what does a cross-encoder do", budget_tokens=300)
    assert res.hits and res.tokens_used <= 300
    assert res.hits[0].doc_id == "concepts/reranking"

    only_practice = retrieve(s, "what does a cross-encoder do", doc_type="practice")
    assert all(h.doc_id.startswith("practices/") for h in only_practice.hits)

    tagged = retrieve(s, "chunk size", tags=["chunking"])
    assert tagged.hits and all(h.doc_id == "concepts/chunking" for h in tagged.hits)


def test_link_expansion(tmp_path):
    s = _store(tmp_path)
    s.ingest(load_corpus(KB))
    res = retrieve(s, "re-ranker cross-encoder", budget_tokens=2000, expand_links=True)
    assert any(h.via == "link" for h in res.hits)
