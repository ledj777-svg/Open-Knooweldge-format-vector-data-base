---
title: Guardrails and PII Masking
type: practice
tags: [safety, guardrails]
---
# Guardrails and PII Masking

## PII masking
Detect names, emails and phone numbers before text reaches the model or the logs, and replace them with placeholders such as EMAIL_1. Keep the mapping server-side so the response can be restored.

## Output checks
Validate model output against a schema, and block responses that leak secrets or ignore the supplied context. Log every blocked response for review.

## Where it fits
Apply masking at ingestion time as well as query time, so sensitive values never enter the vector index. Related: [[agents]].
