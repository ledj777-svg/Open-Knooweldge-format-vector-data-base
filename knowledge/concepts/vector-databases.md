---
title: Vector Databases
type: concept
tags: [vector-db, retrieval]
---
# Vector Databases

A vector database stores embeddings and answers nearest-neighbour queries quickly using approximate indexes such as HNSW.

## Metadata filtering
Most vector stores let you attach metadata to each vector and filter on it before or during search. Filtering by document type or tag from [[okf]] frontmatter shrinks the candidate pool and improves precision.

## Options
Chroma is easy to run locally and embeds in a Python process. Qdrant and pgvector suit larger or production deployments. Pick based on scale and operational needs, not on benchmarks alone.
