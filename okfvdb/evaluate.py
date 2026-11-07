"""Compare context strategies on a question set.

Strategies
  full_load : every OKF file in the prompt (the current approach)
  file_rag  : classic file-level RAG, top-3 whole files
  okf_vdb   : this project (chunks + metadata + budget, no top-k / no rerank)

Metrics
  doc_recall      : fraction of gold docs present in the context
  answer_in_ctx   : fraction of `must_contain` phrases present in the context
  tokens          : context size
"""
from __future__ import annotations

import yaml

from .retriever import retrieve
from .store import OKFStore
from .tokens import count_tokens, counter_name


def _recall(gold, got):
    return sum(g in got for g in gold) / len(gold) if gold else 1.0


def _phrases(must, ctx):
    ctx = ctx.lower()
    return sum(m.lower() in ctx for m in must) / len(must) if must else 1.0


def run_eval(store: OKFStore, kb: str, qfile: str, budget: int, out: str):
    qs = yaml.safe_load(open(qfile, encoding="utf-8"))
    docs = store.all_docs_text()
    full_ctx = "\n\n".join(docs.values())
    full_tok = count_tokens(full_ctx)

    rows = {"full_load": [], "file_rag": [], "okf_vdb": []}
    for q in qs:
        gold, must = q.get("gold", []), q.get("must_contain", [])

        rows["full_load"].append((1.0, _phrases(must, full_ctx), full_tok))

        raw = store.search(q["q"], 20)
        files, seen = [], set()
        for r in raw:
            d = r["meta"]["doc_id"]
            if d not in seen:
                seen.add(d); files.append(d)
            if len(files) == 3:
                break
        fctx = "\n\n".join(docs[f] for f in files)
        rows["file_rag"].append((_recall(gold, files), _phrases(must, fctx), count_tokens(fctx)))

        res = retrieve(store, q["q"], budget_tokens=budget)
        got = {h.doc_id for h in res.hits}
        rows["okf_vdb"].append((_recall(gold, got), _phrases(must, res.context()), res.tokens_used))

    def avg(xs): return sum(xs) / len(xs)
    lines = [f"# Eval results\n",
             f"questions={len(qs)}  docs={len(docs)}  budget={budget}  tokens={counter_name()}  embedder={store.embedder.name}\n",
             "| strategy | doc recall | answer in ctx | avg tokens | vs full load |",
             "|---|---|---|---|---|"]
    for name, r in rows.items():
        t = avg([x[2] for x in r])
        lines.append(f"| {name} | {avg([x[0] for x in r]):.2f} | {avg([x[1] for x in r]):.2f} "
                     f"| {t:.0f} | {100 * (1 - t / full_tok):.0f}% fewer |")
    text = "\n".join(lines) + "\n"
    print(text)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
