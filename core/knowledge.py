"""Local, searchable knowledge entries for the Control Center."""
from __future__ import annotations

import json
import sys
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from .storage import write_json_atomic


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
            raw_entries = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []
        if not isinstance(raw_entries, list):
            return []
        entries: list[KnowledgeEntry] = []
        seen: set[str] = set()
        for item in raw_entries:
            if not isinstance(item, dict):
                continue
            values = {key: item.get(key) for key in ("id", "title", "category", "summary", "content")}
            if not all(isinstance(value, str) and value.strip() for value in values.values()):
                continue
            entry_id = values["id"].strip()
            if entry_id in seen:
                continue
            seen.add(entry_id)
            entries.append(KnowledgeEntry(**{key: value.strip() for key, value in values.items()}))
        return entries

    def search(self, query: str = "") -> list[KnowledgeEntry]:
        needle = query.strip().lower()
        if not needle:
            return self.entries()
        return [entry for entry in self.entries() if needle in " ".join((entry.title, entry.category, entry.summary, entry.content)).lower()]

    def create(self, title: str, category: str, summary: str, content: str) -> KnowledgeEntry:
        values = (title, category, summary, content)
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("Knowledge title, category, summary, and content are required")
        entry = KnowledgeEntry(
            id=f"EV-KNOW-{uuid.uuid4().hex[:8].upper()}",
            title=title.strip(), category=category.strip(),
            summary=summary.strip(), content=content.strip(),
        )
        records = self.entries()
        records.append(entry)
        write_json_atomic(self.path, [asdict(item) for item in records])
        return entry
