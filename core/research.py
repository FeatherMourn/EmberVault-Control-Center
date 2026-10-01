"""Isolated research records and evidence notes."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from .storage import write_json_atomic


@dataclass
class ResearchRecord:
    id: str
    title: str
    hypothesis: str
    profile_id: str
    status: str = "planned"
    evidence: list[str] = field(default_factory=list)
    created_at: str = ""


class ResearchService:
    def __init__(self, root: Path):
        self.path = Path(root) / "research" / "records.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[ResearchRecord]:
        if not self.path.exists():
            return []
        try:
            records = []
            for item in json.loads(self.path.read_text(encoding="utf-8")):
                record = ResearchRecord(**item)
                if record.status not in {"planned", "running", "completed", "blocked"}:
                    record.status = "planned"
                if not isinstance(record.evidence, list):
                    record.evidence = []
                else:
                    record.evidence = [item.strip() for item in record.evidence if isinstance(item, str) and item.strip()]
                records.append(record)
            return records
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def create(self, title: str, hypothesis: str, profile_id: str) -> ResearchRecord:
        if not title.strip() or not hypothesis.strip() or not profile_id.strip():
            raise ValueError("Research title, hypothesis, and profile are required")
        record = ResearchRecord(
            id=f"EV-RES-{uuid.uuid4().hex[:8].upper()}", title=title.strip(),
            hypothesis=hypothesis.strip(), profile_id=profile_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        records = self.list()
        records.append(record)
        write_json_atomic(self.path, [asdict(item) for item in records])
        return record

    def add_evidence(self, record_id: str, note: str) -> ResearchRecord:
        records = self.list()
        for record in records:
            if record.id == record_id:
                if not note.strip():
                    raise ValueError("Evidence note is required")
                record.evidence.append(note.strip())
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)

    def set_status(self, record_id: str, status: str) -> ResearchRecord:
        if status not in {"planned", "running", "completed", "blocked"}:
            raise ValueError("Unknown research status")
        records = self.list()
        for record in records:
            if record.id == record_id:
                if status == "completed" and not record.evidence:
                    raise ValueError("Add evidence before completing research")
                record.status = status
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)
