"""Backup-bound Trainer session plans; no trainer mutation is performed."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .profiles import Profile
from .save_manager import SaveManagerError, SaveManagerService
from .storage import write_json_atomic


@dataclass
class TrainerPlan:
    id: str
    profile_id: str
    target: str
    notes: str
    backup_id: str
    created_at: str


class TrainerPlanService:
    def __init__(self, root: Path, saves: SaveManagerService | None = None):
        self.path = Path(root) / "trainer" / "plans.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.saves = saves

    def list(self) -> list[TrainerPlan]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                return []
            result = []
            for item in raw:
                if not isinstance(item, dict):
                    continue
                try:
                    result.append(TrainerPlan(**item))
                except (TypeError, ValueError):
                    continue
            return result
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def create(self, profile: Profile, target: str, notes: str, backup_id: str) -> TrainerPlan:
        if profile.profile_type != "research":
            raise ValueError("Trainer plans require the isolated Research profile")
        if not target.strip() or not backup_id.strip():
            raise ValueError("Trainer target and verified backup are required")
        if self.saves:
            backup = next((item for item in self.saves.list_backups() if item.id == backup_id), None)
            if not backup or not backup.verified:
                raise ValueError("Trainer plan requires an existing verified backup")
            try:
                if not self.saves.verify_backup(backup.id):
                    raise ValueError("Trainer plan requires a checksum-valid backup")
            except SaveManagerError as exc:
                raise ValueError("Trainer plan requires a checksum-valid backup") from exc
        plan = TrainerPlan(
            id=f"EV-TRAIN-{uuid.uuid4().hex[:8].upper()}", profile_id=profile.id,
            target=target.strip(), notes=notes.strip(), backup_id=backup_id.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        records = self.list()
        records.append(plan)
        write_json_atomic(self.path, [asdict(item) for item in records])
        return plan

    def export(self, plan: TrainerPlan) -> Path:
        destination = self.path.parent.parent / "exports" / "trainer" / f"{plan.id}.json"
        write_json_atomic(destination, {
            "schema_version": 1,
            "plan": asdict(plan),
            "application_state": "trainer-plan-only",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        })
        return destination
