---
title: Prompt Caching
type: concept
tags: [cost, latency]
---
# Prompt Caching

Prompt caching reuses the already-processed prefix of a prompt so repeated requests with the same prefix are cheaper and faster.

## Cache-augmented generation
For a small, stable knowledge base you can place all documents in a cached prefix and skip retrieval entirely. This works while the corpus fits in the context window and rarely changes.

## Limits
Any edit to the prefix invalidates the cache, and large contexts still dilute attention. Retrieval scales better once the corpus outgrows the window. Compare with [[vector-databases]].
