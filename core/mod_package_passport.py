"""Control Center validation and plan-only boundary for Mod Package Passports."""
from __future__ import annotations

from typing import Any


def review_package_passport(passport: dict[str, Any], *, backup_id: str | None = None) -> dict[str, Any]:
    required = ("id", "version", "builds", "targets", "files", "dependencies", "evidence")
    issues = [f"missing:{key}" for key in required if key not in passport]
    if passport.get("read_only") is not True:
        issues.append("passport must be read-only")
    if passport.get("runtime_approval") is not False:
        issues.append("runtime approval must be false")
    files = passport.get("files", [])
    if not isinstance(files, list) or any(not isinstance(item, dict) or not item.get("sha256") for item in files):
        issues.append("file hashes are incomplete")
    if passport.get("backup_required") and not backup_id:
        issues.append("verified Save Manager backup is required")
    return {
        "contract_version": 1,
        "package_id": passport.get("id", "unknown"),
        "version": passport.get("version", "unknown"),
        "builds": list(passport.get("builds", [])) if isinstance(passport.get("builds"), list) else [],
        "targets": list(passport.get("targets", [])) if isinstance(passport.get("targets"), list) else [],
        "state": "blocked" if issues else "approval-required",
        "issues": issues,
        "backup_id": backup_id,
        "plan_only": True,
        "executes_installation": False,
        "mutates_workspace": False,
        "authority": "control-center",
    }
