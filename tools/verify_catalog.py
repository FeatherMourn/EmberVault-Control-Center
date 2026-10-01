"""Validate an EmberVault catalog snapshot outside the desktop application."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.catalog import CatalogExportService


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an EmberVault catalog JSON snapshot")
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.catalog.read_text(encoding="utf-8"))
        CatalogExportService.validate(payload)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Catalog validation failed: {exc}")
        return 1
    print(f"Catalog validation passed: {args.catalog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
