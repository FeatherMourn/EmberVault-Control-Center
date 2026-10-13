"""Display-safe Passport review adapter for Control Center."""
from __future__ import annotations


def prepare_passport_display(review: dict) -> dict:
    if not isinstance(review, dict) or review.get("contract_version") != 1:
        raise ValueError("Passport review requires contract version 1.")
    return {
        "title": "Mod Package Passport",
        "package_id": str(review.get("package_id", "unknown")),
        "version": str(review.get("version", "unknown")),
        "builds": list(review.get("builds", [])),
        "targets": list(review.get("targets", [])),
        "state": str(review.get("state", "blocked")),
        "issues": list(review.get("issues", [])),
        "plan_only": True,
        "actions": [],
        "read_only": True,
        "mutates_workspace": False,
    }
