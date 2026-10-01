"""Evidence-backed, fail-closed runtime tuning adapter metadata."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TuningAdapterService:
    """Loads reviewed evidence without granting mutation authority by itself."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.manifest_path = self.root / "adapters" / "eml-balancing-table.json"

    def manifest(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Unable to read tuning adapter manifest") from exc
        self.validate(payload)
        return payload

    @staticmethod
    def validate(payload: dict[str, Any]) -> None:
        required = {
            "schema_version", "id", "name", "version", "process_mode",
            "loader", "game_build", "supported_setting_keys", "evidence",
            "backup_requirements", "mutation_scope", "verification_steps",
            "feature_state",
        }
        if not isinstance(payload, dict) or set(payload) != required:
            raise ValueError("Tuning adapter manifest has an invalid shape")
        if payload["schema_version"] != 1 or payload["process_mode"] != "separate":
            raise ValueError("Unsupported tuning adapter manifest")
        if payload["loader"] != "EML" or payload["game_build"] != "1076226":
            raise ValueError("Adapter is not compatible with the reviewed EML build")
        keys = payload["supported_setting_keys"]
        if keys != ["baseCritChance"]:
            raise ValueError("Only the evidenced scalar tuning key may be enabled")
        evidence = payload["evidence"]
        if not isinstance(evidence, dict) or evidence.get("write_ok") is not True \
                or evidence.get("readback_ok") is not True \
                or evidence.get("restore_ok") is not True \
                or evidence.get("panic") is not False \
                or evidence.get("probe_removed") is not True \
                or evidence.get("stable_profile_restored") is not True:
            raise ValueError("Adapter lacks complete reversible runtime evidence")
        if payload["feature_state"] != "experimental":
            raise ValueError("Adapter must remain experimental until behavior is verified")

