"""Create a signed, verifiable release bundle from a packaged artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from core.distribution import DistributionService
from tools.sign_release import sign_manifest


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_release(artifact: Path, version: str, key: Path, key_id: str, output: Path) -> Path:
    artifact = Path(artifact).resolve(); output = Path(output).resolve()
    if not artifact.is_file():
        raise ValueError("Release artifact is missing")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"embervault-{version}-windows.zip"
    shutil.copy2(artifact, archive)
    unsigned = output / "release-unsigned.json"
    unsigned.write_text(json.dumps({"version": version, "channel": "stable", "platform": "windows",
        "package_name": archive.name, "sha256": sha256(archive)}, indent=2) + "\n", encoding="utf-8")
    manifest = output / "release.json"
    sign_manifest(unsigned, key, key_id, manifest)
    unsigned.unlink()
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path); parser.add_argument("version")
    parser.add_argument("private_key", type=Path); parser.add_argument("key_id")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    package_release(args.artifact, args.version, args.private_key, args.key_id, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
