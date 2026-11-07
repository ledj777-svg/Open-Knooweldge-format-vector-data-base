---
title: LLM Agents
type: concept
tags: [agents]
---
# LLM Agents

An agent runs a loop: the model chooses a tool, the tool runs, and the result is fed back until the task is done.

## Sequential multi-agent pipelines
Several specialised agents run in order, each passing its output to the next, such as researcher then writer then reviewer. Sequential flows are easier to debug than free-form agent conversations.

## Memory
Agents often need long-term knowledge. Structured retrieval over [[okf]] files gives an agent facts without bloating every prompt.
