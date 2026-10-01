"""Character editor project data; intentionally separate from save mutation."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from .storage import write_json_atomic


@dataclass
class CharacterRecord:
    id: str
    name: str
    profile_id: str
    notes: str = ""
    planned_level: int = 1


class CharacterService:
    def __init__(self, root: Path):
        self.path = Path(root) / "characters" / "records.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[CharacterRecord]:
        if not self.path.exists():
            return []
        try:
            return [CharacterRecord(**item) for item in json.loads(self.path.read_text(encoding="utf-8"))]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def create(self, name: str, profile_id: str, notes: str = "") -> CharacterRecord:
        if not name.strip() or not profile_id.strip():
            raise ValueError("Character name and profile are required")
        record = CharacterRecord(f"EV-CHAR-{uuid.uuid4().hex[:8].upper()}", name.strip(), profile_id, notes.strip())
        records = self.list()
        records.append(record)
        write_json_atomic(self.path, [asdict(item) for item in records])
        return record

    def stage_level(self, record_id: str, level: int) -> CharacterRecord:
        if not 1 <= level <= 50:
            raise ValueError("Planned level must be between 1 and 50")
        records = self.list()
        for record in records:
            if record.id == record_id:
                record.planned_level = level
                write_json_atomic(self.path, [asdict(item) for item in records])
                return record
        raise KeyError(record_id)
