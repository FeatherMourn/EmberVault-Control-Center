"""Durable operation tracking for reviewable actions."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

from .integration import IntegrationContext


class OperationStatus(StrEnum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperationPhase(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVE = "approve"
    EXECUTE = "execute"
    VERIFY = "verify"
    RECOVER = "recover"


PHASE_ORDER = tuple(OperationPhase)


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
    capability: str | None = None
    capability_state: str | None = None
    recovery_expectation: str | None = None
    message: str = ""
    phase: str = OperationPhase.EXECUTE
    progress: int = 0
    cancellable: bool = True
    recovery_guidance: str = ""
    risk_level: str = "low"
    notifications: list[dict[str, str]] = field(default_factory=list)


class OperationService:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def start(self, operation_type: str, **context) -> Operation:
        requested_phase = context.pop("phase", None)
        capability = context.get("capability") or self._capability_for(operation_type)
        capability_state = context.get("capability_state") or self._state_for(operation_type)
        recovery_expectation = context.get("recovery_expectation") or self._recovery_for(operation_type)
        operation = Operation(
            id=f"EV-OP-{uuid.uuid4().hex[:8].upper()}",
            operation_type=operation_type,
            started_at=datetime.now(timezone.utc).isoformat(),
            profile_id=context.get("profile_id"), package_id=context.get("package_id"),
            capability=capability,
            capability_state=capability_state,
            recovery_expectation=recovery_expectation,
            phase=requested_phase or OperationPhase.DRAFT,
            cancellable=bool(context.get("cancellable", True)),
            recovery_guidance=context.get("recovery_guidance", recovery_expectation),
            risk_level=context.get("risk_level") or self._risk_for(operation_type),
        )
        self._append(operation)
        # A normal user-triggered command has already passed through the UI's
        # draft/review/approval surface. Persist those lifecycle checkpoints
        # before returning control to the workflow at execution time. Callers
        # that need a genuinely paused phase can pass phase= explicitly.
        if requested_phase is None:
            for phase, message in ((OperationPhase.REVIEW, "Operation plan created"),
                                   (OperationPhase.APPROVE, "Operation approved by Control Center"),
                                   (OperationPhase.EXECUTE, "Operation execution started")):
                self.transition(operation, phase, message)
        return operation

    @staticmethod
    def _capability_for(operation_type: str) -> str:
        prefix = operation_type.split("-", 1)[0]
        return {
            "package": "mods", "module": "mods", "tuning": "tuning",
            "research": "research", "knowledge": "knowledge",
            "content": "content-creator", "character": "character-tools",
            "trainer": "trainer", "save": "save-manager",
            "catalog": "catalog", "troubleshooter": "operations",
        }.get(prefix, "operations")

    @staticmethod
    def _state_for(operation_type: str) -> str:
        if any(token in operation_type for token in ("deploy", "restore", "rollback")):
            return "staged"
        if any(token in operation_type for token in ("research", "trainer", "content", "character")):
            return "plan-only"
        if any(token in operation_type for token in ("inspection", "verify", "scan", "export", "catalog")):
            return "read-only"
        return "ready"

    @staticmethod
    def _recovery_for(operation_type: str) -> str:
        if any(token in operation_type for token in ("deploy", "restore", "rollback", "tuning")):
            return "verified backup or rollback required"
        if any(token in operation_type for token in ("research", "trainer", "content", "character")):
            return "no live mutation; preserve source record"
        return "retain operation record for review"

    @staticmethod
    def _risk_for(operation_type: str) -> str:
        if any(token in operation_type for token in ("deploy", "restore", "rollback", "tuning", "trainer")):
            return "high"
        if any(token in operation_type for token in ("package", "profile", "content", "publish", "import")):
            return "medium"
        return "low"

    def finish(self, operation: Operation, status: OperationStatus, message: str = "", backup_id: str | None = None) -> Operation:
        operation.status = status
        operation.message = message
        operation.backup_id = backup_id or operation.backup_id
        if status == OperationStatus.SUCCEEDED:
            operation.phase = OperationPhase.VERIFY
            operation.progress = 100
        elif status in {OperationStatus.FAILED, OperationStatus.CANCELLED}:
            operation.phase = OperationPhase.RECOVER
        self._notify(operation, "success" if status == OperationStatus.SUCCEEDED else "error",
                     f"operation.{status}", message or status)
        operation.finished_at = datetime.now(timezone.utc).isoformat()
        self._append(operation)
        return operation

    def transition(self, operation: Operation, phase: OperationPhase, message: str = "") -> Operation:
        """Advance an active operation through the shared lifecycle."""
        if operation.status != OperationStatus.STARTED:
            raise ValueError("Only active operations can change phase")
        try:
            current = PHASE_ORDER.index(OperationPhase(operation.phase))
            target = PHASE_ORDER.index(OperationPhase(phase))
        except ValueError as exc:
            raise ValueError("Unknown operation phase") from exc
        if target < current:
            raise ValueError("Operation phases cannot move backwards")
        operation.phase = OperationPhase(phase)
        if message:
            operation.message = message
        self._notify(operation, "info", f"phase.{operation.phase}", message or f"Entered {operation.phase}")
        self._append(operation)
        return operation

    def update_progress(self, operation: Operation, progress: int, message: str = "") -> Operation:
        if operation.status != OperationStatus.STARTED:
            raise ValueError("Only active operations can report progress")
        operation.progress = max(0, min(100, int(progress)))
        if message:
            operation.message = message
        self._notify(operation, "info", "operation.progress", f"Progress {operation.progress}%")
        self._append(operation)
        return operation

    def cancel(self, operation: Operation, message: str = "Cancelled by user") -> Operation:
        if not operation.cancellable:
            raise ValueError("Operation is not cancellable")
        return self.finish(operation, OperationStatus.CANCELLED, message)

    def notify(self, operation: Operation, level: str, code: str, message: str) -> Operation:
        """Append a structured, user-visible notification to an operation."""
        self._notify(operation, level, code, message)
        self._append(operation)
        return operation

    @staticmethod
    def _notify(operation: Operation, level: str, code: str, message: str) -> None:
        if level not in {"info", "success", "warning", "error"}:
            raise ValueError("Unknown operation notification level")
        operation.notifications.append({"level": level, "code": code, "message": message})

    @staticmethod
    def integration_context(operation: Operation) -> IntegrationContext:
        """Return the validated handoff context carried by an operation."""
        if not all((operation.capability, operation.capability_state, operation.recovery_expectation)):
            raise ValueError("Operation is missing cross-module integration metadata")
        return IntegrationContext.from_operation(
            operation,
            capability=operation.capability,
            capability_state=operation.capability_state,
            recovery_expectation=operation.recovery_expectation,
        )

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
                    if (not isinstance(operation.id, str) or not operation.id.strip()
                            or not isinstance(operation.operation_type, str) or not operation.operation_type.strip()
                            or operation.status not in {item.value for item in OperationStatus}):
                        continue
                    records[operation.id] = operation
        latest = list(records.values())[-max(0, limit):]
        return list(reversed(latest))

    def _append(self, operation: Operation) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(operation), sort_keys=True) + "\n")
