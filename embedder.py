"""Pluggable embedders.

- "st":   sentence-transformers (default; local; one-time model download)
- "hash": deterministic hashed bag-of-words. Offline, zero deps. For tests/CI only.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol


class Embedder(Protocol):
    name: str
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    name = "hash"

    def __init__(self, dim: int = 1024):
        self.dim = dim

    @staticmethod
    def _tok(text: str) -> list[str]:
        words = re.findall(r"[a-z0-9]+", text.lower())
        return words + [f"{a}_{b}" for a, b in zip(words, words[1:])]

    def embed(self, texts):
        out = []
        for t in texts:
            v = [0.0] * self.dim
            for tok in self._tok(t):
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                v[h % self.dim] += 1.0
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / n for x in v])
        return out


class STEmbedder:
    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.name = f"st:{model}"
        self.model = SentenceTransformer(model)

    def embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()


def get_embedder(name: str = "st") -> Embedder:
    if name == "hash":
        return HashEmbedder()
    if name == "st":
        return STEmbedder()
    if name.startswith("st:"):
        return STEmbedder(name[3:])
    raise ValueError(f"unknown embedder: {name}")
