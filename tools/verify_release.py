"""Verify the required non-Python assets in an EmberVault wheel."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


REQUIRED = (
    "ui/Main.qml",
    "contracts/catalog.schema.json",
    "contracts/content-project.schema.json",
    "contracts/knowledge-entry.schema.json",
    "contracts/research-summary.schema.json",
    "contracts/game-settings.schema.json",
    "modules/example/module.json",
    "modules/example/module.py",
    "modules/research/research_stub.py",
    "modules/tuning-audit/tuning_stub.py",
    "knowledge/entries.json",
    "packages/example-mod/package.json",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.wheel) as archive:
        names = set(archive.namelist())
    missing = [path for path in REQUIRED if not any(name.endswith(".data/data/" + path) for name in names)]
    if missing:
        print("Missing release assets:")
        print("\n".join(missing))
        return 1
    print(f"Release asset verification passed: {len(REQUIRED)} assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
