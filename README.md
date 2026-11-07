# OKF + Vector DB

Structure-aware retrieval over **Open Knowledge Format** (markdown + YAML frontmatter + links).
Instead of loading every `.md` file into the prompt, index them once and fetch only what a question needs.

## How it differs from plain RAG
| Step | Plain RAG | This project |
|---|---|---|
| Chunking | fixed size | by heading, heading path embedded with the text |
| Filtering | none | `type` / `tags` from frontmatter, applied before vector search |
| Result size | fixed top-k | adaptive cut + **token budget** (no top-k, no re-ranker) |
| Multi-hop | none | optional expansion through `[[links]]` |
| Re-index | full | incremental, by content hash |

> A vector search still ranks candidates. "No top-k" here means the cut-off is a score threshold
> plus a token budget, not a hard-coded N.

## Quick start
```bash
pip install -r requirements.txt
python -m okfvdb ingest knowledge
python -m okfvdb query "what does a cross-encoder do" --budget 600 --show
python -m okfvdb query "chunk size" --tag chunking --expand
python -m okfvdb eval knowledge eval/questions.yaml --budget 400
pytest
```
Offline / CI: add `--embedder hash` (keyword-hash embedder, tests only).
Default embedder: `sentence-transformers/all-MiniLM-L6-v2`.

## Layout
```
okfvdb/parser.py     frontmatter, title, [[wikilinks]] and .md links
okfvdb/chunker.py    heading-aware chunks
okfvdb/store.py      Chroma store, incremental ingest, metadata
okfvdb/retriever.py  filter -> search -> adaptive cut -> budget pack -> link expansion
okfvdb/evaluate.py   full-load vs file-level RAG vs this project
knowledge/           sample OKF corpus (10 files)
eval/questions.yaml  gold questions (gold doc + must_contain phrase)
```

## Results (sample corpus, hash embedder, approx tokens)
| strategy | doc recall | answer in ctx | avg tokens |
|---|---|---|---|
| full_load | 1.00 | 1.00 | 1271 |
| file_rag (top-3 files) | 1.00 | 1.00 | 386 |
| okf_vdb | 1.00 | 1.00 | 104 |

These numbers are from a tiny 10-file corpus and are only a smoke test. Re-run `eval` with the
default embedder and your real OKF files for results you can quote.

## Roadmap
- [ ] Real corpus + larger gold set (50+ questions)
- [ ] Compare against a re-ranker to measure what skipping it costs
- [ ] LLM answer-quality eval (RAGAS faithfulness)
- [ ] MCP server so any agent can query the OKF store
