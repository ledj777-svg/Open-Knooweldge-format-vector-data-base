# Eval results

questions=10  docs=10  budget=400  tokens=approx(chars/4)  embedder=hash

| strategy | doc recall | answer in ctx | avg tokens | vs full load |
|---|---|---|---|---|
| full_load | 1.00 | 1.00 | 1271 | 0% fewer |
| file_rag | 1.00 | 1.00 | 386 | 70% fewer |
| okf_vdb | 1.00 | 1.00 | 104 | 92% fewer |
