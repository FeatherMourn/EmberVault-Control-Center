"""Local, searchable knowledge entries for the Control Center."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeEntry:
    id: str
    title: str
    category: str
    summary: str
    content: str


class KnowledgeService:
    def __init__(self, root: Path):
        self.path = Path(root) / "knowledge" / "entries.json"
        source_root = Path(__file__).resolve().parents[1] / "knowledge" / "entries.json"
        installed_root = Path(sys.prefix) / "knowledge" / "entries.json"
        self.seed_path = source_root if source_root.exists() else installed_root
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def entries(self) -> list[KnowledgeEntry]:
        source = self.path if self.path.exists() else self.seed_path
        if not source.exists():
            return []
        try:
            return [KnowledgeEntry(**item) for item in json.loads(source.read_text(encoding="utf-8"))]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def search(self, query: str = "") -> list[KnowledgeEntry]:
        needle = query.strip().lower()
        if not needle:
            return self.entries()
        return [entry for entry in self.entries() if needle in " ".join((entry.title, entry.category, entry.summary, entry.content)).lower()]
