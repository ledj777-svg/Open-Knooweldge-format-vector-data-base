---
title: Re-ranking
type: concept
tags: [rag, reranking]
---
# Re-ranking

A re-ranker rescoring step reorders retrieved candidates with a more accurate but slower model.

## Cross-encoders
A cross-encoder reads the query and a passage together and outputs a relevance score. It is more accurate than comparing embeddings, but it must run once per candidate, so latency grows with the candidate count.

## When to skip it
For a small, well-structured knowledge base with metadata filters and heading-level chunks, the vector ranking is often good enough. Add a re-ranker when the corpus is large or noisy. See [[rag-overview]].
