"""Token counting. Uses tiktoken when available, else ~4 chars/token."""
from __future__ import annotations

import math

_enc = None
try:  # optional; may need network for its first-time vocab download
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    _enc = None


def count_tokens(text: str) -> int:
    if _enc is not None:
        return len(_enc.encode(text))
    return math.ceil(len(text) / 4)


def counter_name() -> str:
    return "tiktoken:cl100k_base" if _enc is not None else "approx(chars/4)"
