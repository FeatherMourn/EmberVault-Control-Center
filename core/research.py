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
    published: bool = False
    published_at: str = ""
    game_build: str = ""
    game_version: str = ""
    reproduction_steps: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    promotion_status: str = "not-requested"
    promotion_note: str = ""


class ResearchService:
    def __init__(self, root: Path):
        self.path = Path(root) / "research" / "records.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[ResearchRecord]:
        if not self.path.exists():
            return []
        try:
            records = []
            raw_records = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw_records, list):
                return []
            for item in raw_records:
                if not isinstance(item, dict):
                    continue
                try:
                    record = ResearchRecord(**item)
                except (TypeError, ValueError):
                    continue
                if record.status not in {"planned", "running", "completed", "blocked"}:
                    record.status = "planned"
                if not isinstance(record.evidence, list):
                    record.evidence = []
                else:
                    record.evidence = [item.strip() for item in record.evidence if isinstance(item, str) and item.strip()]
                if not isinstance(record.published, bool):
                    record.published = False
                if not isinstance(record.published_at, str):
                    record.published_at = ""
                for field_name in ("game_build", "game_version", "promotion_note"):
                    if not isinstance(getattr(record, field_name), str):
                        setattr(record, field_name, "")
                for field_name in ("reproduction_steps", "failures"):
                    values = getattr(record, field_name)
                    if not isinstance(values, list):
                        values = []
                    setattr(record, field_name, [value.strip() for value in values
                                                 if isinstance(value, str) and value.strip()])
                if record.promotion_status not in {"not-requested", "requested", "approved", "rejected"}:
                    record.promotion_status = "not-requested"
                records.append(record)
            return records
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def create(self, title: str, hypothesis: str, profile_id: str,
               game_build: str = "", game_version: str = "") -> ResearchRecord:
        if not title.strip() or not hypothesis.strip() or not profile_id.strip():
            raise ValueError("Research title, hypothesis, and profile are required")
        record = ResearchRecord(
            id=f"EV-RES-{uuid.uuid4().hex[:8].upper()}", title=title.strip(),
            hypothesis=hypothesis.strip(), profile_id=profile_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            game_build=game_build.strip(), game_version=game_version.strip(),
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
                if record.published:
                    record.published = False
                    record.published_at = ""
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)

    def _append_record_text(self, record_id: str, field_name: str, text: str) -> ResearchRecord:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Research record text is required")
        records = self.list()
        for record in records:
            if record.id == record_id:
                getattr(record, field_name).append(text.strip())
                if record.published:
                    record.published = False
                    record.published_at = ""
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)

    def add_reproduction_step(self, record_id: str, step: str) -> ResearchRecord:
        return self._append_record_text(record_id, "reproduction_steps", step)

    def add_failure(self, record_id: str, failure: str) -> ResearchRecord:
        return self._append_record_text(record_id, "failures", failure)

    def set_promotion_review(self, record_id: str, status: str, note: str = "") -> ResearchRecord:
        if status not in {"not-requested", "requested", "approved", "rejected"}:
            raise ValueError("Unknown promotion review status")
        records = self.list()
        for record in records:
            if record.id == record_id:
                if status in {"requested", "approved"} and record.status != "completed":
                    raise ValueError("Only completed research can enter promotion review")
                if status == "approved" and (not record.evidence or not record.reproduction_steps):
                    raise ValueError("Approved research requires evidence and reproduction steps")
                record.promotion_status = status
                record.promotion_note = note.strip()
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
                if record.published:
                    record.published = False
                    record.published_at = ""
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)

    def publish(self, record_id: str) -> ResearchRecord:
        records = self.list()
        for record in records:
            if record.id == record_id:
                if record.status != "completed" or not record.evidence:
                    raise ValueError("Complete the research and add evidence before publishing")
                record.published = True
                record.published_at = datetime.now(timezone.utc).isoformat()
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)

    def unpublish(self, record_id: str) -> ResearchRecord:
        records = self.list()
        for record in records:
            if record.id == record_id:
                record.published = False
                record.published_at = ""
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)

    def export_summary(self, record: ResearchRecord) -> Path:
        """Export a profile-free research handoff without evidence text."""
        destination = self.path.parent.parent / "exports" / "research" / f"{record.id}.json"
        write_json_atomic(destination, {
            "schema_version": 1,
            "record": {
                "id": record.id, "title": record.title, "hypothesis": record.hypothesis,
                "status": record.status, "evidence_count": len(record.evidence),
                "created_at": record.created_at, "published_at": record.published_at,
                "game_build": record.game_build, "game_version": record.game_version,
                "reproduction_step_count": len(record.reproduction_steps),
                "failure_count": len(record.failures), "promotion_status": record.promotion_status,
            },
            "application_state": "research-summary",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        })
        return destination
