"""Validate an EmberVault catalog snapshot outside the desktop application."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_catalog(payload: dict) -> None:
    """Validate only the public catalog contract; no desktop imports required."""
    required = ("generated_at", "contract_versions", "packages", "modules", "knowledge", "research", "content_projects")
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Catalog schema version must be 1")
    if any(key not in payload for key in required) or set(payload) != {"schema_version", *required}:
        raise ValueError("Catalog is missing a required collection")
    if not isinstance(payload["generated_at"], str) or not payload["generated_at"].strip():
        raise ValueError("Catalog generation timestamp is required")
    versions = payload["contract_versions"]
    if not isinstance(versions, dict):
        raise ValueError("Catalog contract versions must be an object")
    for key in ("module_manifest", "package_manifest", "research_record", "content_project", "tuning_adapter"):
        version = versions.get(key)
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            raise ValueError(f"Catalog contract version is missing: {key}")
    for collection in ("packages", "modules", "knowledge", "research", "content_projects"):
        if not isinstance(payload[collection], list):
            raise ValueError(f"Catalog collection is not an array: {collection}")
    for collection in ("packages", "modules"):
        for item in payload[collection]:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
                raise ValueError(f"{collection.title()} catalog records must contain an id")
            if collection == "modules" and item.get("process_mode") not in {"embedded", "separate"}:
                raise ValueError("Module catalog records must declare embedded or separate process_mode")
    for item in payload["knowledge"]:
        if not isinstance(item, dict) or set(item) != {"id", "title", "category", "summary", "content", "published_at"}:
            raise ValueError("Knowledge catalog records must match the public contract")
        if any(not isinstance(item[key], str) or not item[key].strip()
               for key in ("id", "title", "category", "summary", "content", "published_at")):
            raise ValueError("Knowledge catalog records must contain non-empty fields")
    for item in payload["research"]:
        if not isinstance(item, dict) or set(item) != {"id", "title", "hypothesis", "status", "evidence_count", "created_at", "published_at"}:
            raise ValueError("Research catalog records must remain sanitized")
        if item["status"] != "completed" or not isinstance(item["evidence_count"], int) or item["evidence_count"] < 1:
            raise ValueError("Research catalog records must be completed with evidence")
    for item in payload["content_projects"]:
        if not isinstance(item, dict) or set(item) != {"id", "name", "status", "published_at"}:
            raise ValueError("Content catalog records must remain sanitized")
        if item["status"] != "ready":
            raise ValueError("Only ready content projects may be public")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an EmberVault catalog JSON snapshot")
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.catalog.read_text(encoding="utf-8"))
        validate_catalog(payload)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Catalog validation failed: {exc}")
        return 1
    print(f"Catalog validation passed: {args.catalog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
