---
title: Open Knowledge Format
type: concept
tags: [okf, knowledge-base]
---
# Open Knowledge Format

OKF stores knowledge as plain markdown files. Each file starts with YAML frontmatter holding a title, a type and tags, followed by a body organised under headings.

## Why it helps retrieval
Frontmatter gives metadata filters, headings give natural chunk boundaries, and links between files form a lightweight knowledge graph. A retriever can use all three instead of treating files as flat text.

## The token problem
Passing every OKF file to the model on each request is simple but costly. Token use grows linearly with the size of the knowledge base, and irrelevant files dilute the answer. See [[rag-overview]] and [[vector-databases]] for the alternative.
