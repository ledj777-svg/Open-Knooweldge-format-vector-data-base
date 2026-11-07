"""Heading-aware chunking. Each chunk carries its heading path for context."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from .parser import OKFDocument

HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    heading_path: str
    text: str          # raw section text (what the LLM receives)
    embed_text: str    # what gets embedded (title + heading path + text)
    content_hash: str
    ordinal: int


def _split_long(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    parts, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        if cur and len(cur) + len(para) + 2 > max_chars:
            parts.append(cur.strip())
            cur = ""
        cur += para + "\n\n"
    if cur.strip():
        parts.append(cur.strip())
    return parts


def chunk_document(doc: OKFDocument, max_chars: int = 1200, min_chars: int = 120) -> list[Chunk]:
    sections: list[tuple[str, str]] = []
    stack: list[tuple[int, str]] = []
    cur_lines: list[str] = []
    cur_path = doc.title

    def flush():
        body = "\n".join(cur_lines).strip()
        if body:
            sections.append((cur_path, body))

    for line in doc.body.splitlines():
        m = HEADING_RE.match(line)
        if m:
            flush()
            cur_lines = []
            level, name = len(m.group(1)), m.group(2)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, name))
            cur_path = " > ".join(n for _, n in stack)
        else:
            cur_lines.append(line)
    flush()

    # merge tiny sections into the previous one (keeps context together)
    merged: list[tuple[str, str]] = []
    for path, body in sections:
        if merged and len(body) < min_chars:
            p, b = merged[-1]
            merged[-1] = (p, b + "\n\n" + body)
        else:
            merged.append((path, body))

    chunks: list[Chunk] = []
    i = 0
    for path, body in merged:
        for piece in _split_long(body, max_chars):
            embed_text = f"{doc.title} | {path}\n{piece}"
            h = hashlib.sha1(embed_text.encode()).hexdigest()[:16]
            chunks.append(Chunk(
                chunk_id=f"{doc.doc_id}#{i}", doc_id=doc.doc_id, title=doc.title,
                heading_path=path, text=piece, embed_text=embed_text,
                content_hash=h, ordinal=i,
            ))
            i += 1
    return chunks
