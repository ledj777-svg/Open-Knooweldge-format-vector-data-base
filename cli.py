"""CLI:  python -m okfvdb {ingest,query,eval} ..."""
from __future__ import annotations

import argparse
import json

from .embedder import get_embedder
from .parser import load_corpus
from .retriever import retrieve
from .store import OKFStore
from .tokens import counter_name


def _store(a) -> OKFStore:
    return OKFStore(a.db, get_embedder(a.embedder))


def cmd_ingest(a):
    docs = load_corpus(a.kb)
    r = _store(a).ingest(docs, max_chars=a.max_chars)
    print(f"docs={r.docs} chunks={r.chunks_total} added={r.added} "
          f"unchanged={r.unchanged} deleted={r.deleted}")


def cmd_query(a):
    res = retrieve(_store(a), a.question, budget_tokens=a.budget,
                   min_score=a.min_score, rel_cutoff=a.rel_cutoff,
                   doc_type=a.type, tags=a.tag, expand_links=a.expand)
    if a.json:
        print(json.dumps([h.__dict__ for h in res.hits], indent=2))
        return
    for h in res.hits:
        print(f"{h.score:.3f}  {h.via:6}  {h.doc_id} › {h.heading_path}  ({h.tokens} tok)")
    print(f"\n{len(res.hits)} chunks, {res.tokens_used} tokens ({counter_name()})\n")
    if a.show:
        print(res.context())


def cmd_eval(a):
    from .evaluate import run_eval
    run_eval(_store(a), a.kb, a.questions, a.budget, a.out)


def main(argv=None):
    p = argparse.ArgumentParser(prog="okfvdb")
    p.add_argument("--db", default=".chroma")
    p.add_argument("--embedder", default="st", help="st | st:<model> | hash (offline/tests)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ingest"); s.add_argument("kb"); s.add_argument("--max-chars", type=int, default=1200)
    s.set_defaults(fn=cmd_ingest)

    s = sub.add_parser("query"); s.add_argument("question")
    s.add_argument("--budget", type=int, default=600)
    s.add_argument("--min-score", type=float, default=0.15)
    s.add_argument("--rel-cutoff", type=float, default=0.7)
    s.add_argument("--type"); s.add_argument("--tag", action="append")
    s.add_argument("--expand", action="store_true", help="pull in linked docs")
    s.add_argument("--show", action="store_true", help="print the assembled context")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_query)

    s = sub.add_parser("eval"); s.add_argument("kb"); s.add_argument("questions")
    s.add_argument("--budget", type=int, default=600); s.add_argument("--out", default="eval/results.md")
    s.set_defaults(fn=cmd_eval)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
