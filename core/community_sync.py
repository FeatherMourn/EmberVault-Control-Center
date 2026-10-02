"""Conflict-safe, reviewable handoffs for the EmberVault website."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from .storage import write_json_atomic


class CommunitySyncService:
    def __init__(self, root: Path, catalog):
        self.root = Path(root)
        self.catalog = catalog
        self.path = self.root / "community" / "handoff.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def prepare(self) -> dict:
        payload = self.catalog.build()
        return {"schema_version": 1, "handoff_type": "embervault-public-sync",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "authority": "website", "catalog": payload}

    def stage(self) -> Path:
        handoff = self.prepare()
        self.catalog.validate(handoff["catalog"])
        write_json_atomic(self.path, handoff)
        return self.path

    @staticmethod
    def compare(local: dict, remote: dict) -> dict:
        if not isinstance(local, dict) or not isinstance(remote, dict):
            raise ValueError("Community handoffs must be objects")
        left = local.get("catalog", local)
        right = remote.get("catalog", remote)
        if not isinstance(left, dict) or not isinstance(right, dict):
            raise ValueError("Community handoffs must contain catalog objects")
        differences = sorted(key for key in set(left) | set(right) if left.get(key) != right.get(key))
        return {"status": "identical" if not differences else "conflict",
                "conflicting_sections": differences, "automatic_overwrite": False}

    def import_remote(self, remote: dict) -> dict:
        """Validate and compare a website snapshot; never overwrite local data."""
        self.catalog.validate(remote.get("catalog", remote))
        local = self.prepare()
        result = self.compare(local, remote)
        result["review_required"] = result["status"] == "conflict"
        result["authority"] = "website"
        return result
