---
title: Evaluating RAG Systems
type: practice
tags: [evaluation, rag]
---
# Evaluating RAG Systems

## Retrieval metrics
Recall at k measures whether a gold document appears among the retrieved items. Track it together with the number of tokens placed in the prompt, because a method that wins on recall by sending everything is not an improvement.

## Generation metrics
RAGAS reports faithfulness, which checks that the answer is supported by the retrieved context, and answer relevancy, which checks that it addresses the question.

## Practical advice
Build a small gold set of real questions with the expected source document and a phrase the answer must contain. Re-run it after every chunking or embedding change. See [[rag-overview]].
