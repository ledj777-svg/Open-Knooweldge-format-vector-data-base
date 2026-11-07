---
title: RAG Overview
type: concept
tags: [rag, retrieval]
---
# RAG Overview

Retrieval-augmented generation fetches relevant passages at query time and places them in the prompt so the model answers from supplied evidence instead of memory.

## Pipeline
Documents are chunked, embedded and stored. At query time the question is embedded, the nearest chunks are retrieved, optionally re-ranked, and passed to the model.

## Common failure modes
Chunks that cut a topic in half, retrieving too many near-duplicates, and missing context that lives in a linked document. See [[chunking]] and [[reranking]].
