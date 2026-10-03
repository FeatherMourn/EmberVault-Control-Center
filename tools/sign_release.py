"""Sign a release manifest with an external Ed25519 private key."""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization

from core.distribution import ReleaseManifest


def sign_manifest(source: Path, private_key: Path, key_id: str, destination: Path) -> Path:
    payload = json.loads(Path(source).read_text(encoding="utf-8"))
    payload.pop("signature", None)
    manifest = ReleaseManifest.from_dict({**payload, "sha256": payload.get("sha256", "")})
    key = serialization.load_pem_private_key(Path(private_key).read_bytes(), password=None)
    signature = key.sign(manifest.signing_bytes())
    manifest.signature = f"{key_id}:{base64.b64encode(signature).decode('ascii')}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest.to_dict(), indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("private_key", type=Path)
    parser.add_argument("key_id")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    sign_manifest(args.manifest, args.private_key, args.key_id, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
