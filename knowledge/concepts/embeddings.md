---
title: Embeddings
type: concept
tags: [embeddings, retrieval]
---
# Embeddings

An embedding model maps text to a vector so that similar meanings land close together.

## Choosing a model
all-MiniLM-L6-v2 produces 384-dimension vectors and runs on a laptop CPU, which makes it a good default for prototypes. Larger models give better recall at higher latency and cost.

## Similarity
Cosine similarity is the standard metric. With normalised vectors it equals the dot product. Never mix vectors from different models in one index because their dimensions and spaces differ.
