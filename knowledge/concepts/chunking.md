---
title: Chunking Strategies
type: concept
tags: [rag, chunking]
---
# Chunking Strategies

## Fixed-size chunking
Split text every N characters with some overlap. Fast and predictable, but it ignores document structure and often cuts sentences in half.

## Heading-aware chunking
Split on markdown headings so each chunk is one coherent section, and prepend the heading path to the text before embedding. This is the natural fit for [[okf]] files.

## Parent-child chunking
Embed small child chunks for precise matching but return the larger parent section to the model for context. It trades a few extra tokens for fewer broken answers.
