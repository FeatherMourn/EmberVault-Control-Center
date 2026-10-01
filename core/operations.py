"""Durable operation tracking for reviewable actions."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path


class OperationStatus(StrEnum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Operation:
    id: str
    operation_type: str
    started_at: str
    status: str = OperationStatus.STARTED
    finished_at: str | None = None
    profile_id: str | None = None
    package_id: str | None = None
    backup_id: str | None = None
    message: str = ""


class OperationService:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def start(self, operation_type: str, **context) -> Operation:
        operation = Operation(
            id=f"EV-OP-{uuid.uuid4().hex[:8].upper()}",
            operation_type=operation_type,
            started_at=datetime.now(timezone.utc).isoformat(),
            profile_id=context.get("profile_id"), package_id=context.get("package_id"),
        )
        self._append(operation)
        return operation

    def finish(self, operation: Operation, status: OperationStatus, message: str = "", backup_id: str | None = None) -> Operation:
        operation.status = status
        operation.message = message
        operation.backup_id = backup_id or operation.backup_id
        operation.finished_at = datetime.now(timezone.utc).isoformat()
        self._append(operation)
        return operation

    def list_recent(self, limit: int = 20) -> list[Operation]:
        """Return the latest operation records, newest first."""
        if not self.path.exists():
            return []
        records: dict[str, Operation] = {}
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    try:
                        operation = Operation(**json.loads(line))
                    except (ValueError, TypeError, json.JSONDecodeError):
                        continue
                    records[operation.id] = operation
        latest = list(records.values())[-max(0, limit):]
        return list(reversed(latest))

    def _append(self, operation: Operation) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(operation), sort_keys=True) + "\n")
