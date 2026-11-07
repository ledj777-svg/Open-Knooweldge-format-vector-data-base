"""Parse an OKF markdown file: YAML frontmatter + body + outgoing links."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")


@dataclass
class OKFDocument:
    doc_id: str
    path: str
    title: str
    meta: dict = field(default_factory=dict)
    body: str = ""
    links: list[str] = field(default_factory=list)  # target doc ids

    @property
    def type(self) -> str:
        return str(self.meta.get("type", "note"))

    @property
    def tags(self) -> list[str]:
        t = self.meta.get("tags", [])
        if isinstance(t, str):
            t = [x.strip() for x in t.split(",")]
        return [str(x).strip().lower() for x in t if str(x).strip()]


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def parse_okf(path: Path, root: Path) -> OKFDocument:
    text = path.read_text(encoding="utf-8")
    meta: dict = {}
    m = FRONTMATTER_RE.match(text)
    if m:
        try:
            meta = yaml.safe_load(m.group(1)) or {}
            if not isinstance(meta, dict):
                meta = {}
        except yaml.YAMLError:
            meta = {}
        text = text[m.end():]

    rel = path.relative_to(root).with_suffix("")
    doc_id = str(meta.get("id") or rel.as_posix())

    title = meta.get("title")
    if not title:
        h1 = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = h1.group(1).strip() if h1 else path.stem

    links: list[str] = []
    for target in WIKILINK_RE.findall(text):
        links.append(slug(target.strip()))
    for target in MDLINK_RE.findall(text):
        links.append(slug(Path(target).stem))
    links = [l for l in dict.fromkeys(links) if l != slug(doc_id)]

    return OKFDocument(doc_id=doc_id, path=str(path), title=str(title),
                       meta=meta, body=text.strip(), links=links)


def load_corpus(root: str | Path) -> list[OKFDocument]:
    root = Path(root)
    return [parse_okf(p, root) for p in sorted(root.rglob("*.md"))]
