"""Read-only Control Center adapter for Mod Manager review payloads."""
from __future__ import annotations


def prepare_mod_manager_display(review: dict) -> dict:
    if not isinstance(review, dict) or review.get("contract_version", 1) != 1:
        raise ValueError("Mod Manager review requires contract version 1.")
    package = review.get("package", review)
    if not isinstance(package, dict) or not package.get("package_id"):
        raise ValueError("Mod Manager review requires a package identity.")
    return {
        "title": "Mod Manager Review",
        "package_id": str(package["package_id"]),
        "version": str(package.get("version", "unknown")),
        "inventory": list(review.get("inventory", [])),
        "compatibility": dict(review.get("compatibility", {})),
        "integrity": dict(review.get("integrity", {})),
        "backup_readiness": str(review.get("backup_readiness", "unknown")),
        "recovery_history": dict(review.get("recovery_history", {})),
        "approval_granted": False,
        "plan_only": True,
        "read_only": True,
        "mutates_workspace": False,
        "actions": [],
    }
