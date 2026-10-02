"""Audit portable release bundles without extracting or executing them."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    checked = 0
    for platform in ("windows", "linux"):
        path = args.directory / f"embervault-control-center-1.0.0rc1-{platform}.zip"
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if any(name.startswith(("/", "\\")) or ".." in Path(name).parts for name in names):
                raise ValueError(f"Unsafe path in {platform} distribution")
            manifest = json.loads(archive.read("release-manifest.json"))
            wheel_name = manifest["wheel"]
            wheel = archive.read(wheel_name)
            if hashlib.sha256(wheel).hexdigest() != manifest["sha256"]:
                raise ValueError(f"Wheel hash mismatch in {platform} distribution")
            if manifest.get("platform") != platform or manifest.get("version") != "1.0.0rc1":
                raise ValueError(f"Release identity mismatch in {platform} distribution")
            if manifest.get("live_mutation_supported") is not False or manifest.get("data_preserving_uninstall") is not True:
                raise ValueError(f"Safety flags are invalid in {platform} distribution")
            if "INSTALL.txt" not in names:
                raise ValueError(f"Install instructions are missing in {platform} distribution")
        checked += 1
    print(f"Distribution audit passed: {checked} bundles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
