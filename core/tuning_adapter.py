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
            "owned_package_id",
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
        if payload["owned_package_id"] != "embervault.eml-tuning-adapter":
            raise ValueError("Adapter ownership is not recognized")

    def prepare_operation(self, profile_type: str, backup_verified: bool,
                          game_running: bool, staged_value: float,
                          current_value: float) -> dict[str, Any]:
        """Build a fail-closed preview; this method never writes game state."""
        manifest = self.manifest()
        if profile_type != "research":
            raise ValueError("EML tuning requires the Research profile")
        if not backup_verified:
            raise ValueError("A verified recovery point is required")
        if game_running:
            raise ValueError("Close Enshrouded before preparing a tuning operation")
        if not isinstance(staged_value, (int, float)) or not 0.0 <= staged_value <= 1.0:
            raise ValueError("baseCritChance must be between 0.0 and 1.0")
        if not isinstance(current_value, (int, float)) or not 0.0 <= current_value <= 1.0:
            raise ValueError("The current adapter value is invalid")
        return {
            "adapter_id": manifest["id"],
            "loader": manifest["loader"],
            "game_build": manifest["game_build"],
            "resource": manifest["evidence"]["resource"],
            "field": manifest["evidence"]["field"],
            "old_value": float(current_value),
            "new_value": float(staged_value),
            "mutation_performed": False,
            "state": "prepared",
        }

    def execute_operation(self, preview: dict[str, Any], *, profile_type: str,
                          backup_verified: bool, game_running: bool,
                          mutation_enabled: bool = False) -> dict[str, Any]:
        """Refuse live writes until an explicitly owned adapter target exists.

        The EML probe already proves the in-process write path. This method is
        the Control Center transaction gate; it deliberately has no implicit
        target path or permission to modify the installed game.
        """
        if not mutation_enabled:
            raise PermissionError("The EML adapter is not enabled for live mutation")
        if profile_type != "research":
            raise PermissionError("EML tuning requires the Research profile")
        if not backup_verified:
            raise PermissionError("A verified recovery point is required")
        if game_running:
            raise PermissionError("Close Enshrouded before applying tuning")
        if preview.get("state") != "prepared" or preview.get("mutation_performed"):
            raise ValueError("Only an unused prepared preview can be executed")
        raise PermissionError("No owned EML adapter package target is configured")

