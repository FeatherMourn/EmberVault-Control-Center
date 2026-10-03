"""Distribution, update, repair, and uninstall planning with data preservation."""
from __future__ import annotations

import hashlib
import json
import base64
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from .storage import write_json_atomic
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


@dataclass
class ReleaseManifest:
    version: str
    channel: str
    platform: str
    package_name: str
    sha256: str = ""
    minimum_core_version: str = ""
    signature: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "ReleaseManifest":
        if not isinstance(payload, dict) or payload.get("schema_version", 1) != 1:
            raise ValueError("Invalid release manifest schema")
        required = ("version", "channel", "platform", "package_name", "sha256")
        if any(not isinstance(payload.get(key), str) or not payload[key].strip() for key in required):
            raise ValueError("Release manifest is missing required fields")
        digest = payload["sha256"].lower()
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("Release manifest has an invalid SHA-256 digest")
        if payload["channel"] not in {"stable", "beta", "nightly"}:
            raise ValueError("Unsupported release channel")
        if payload["platform"] not in {"windows", "linux"}:
            raise ValueError("Unsupported release platform")
        return cls(version=payload["version"].strip(), channel=payload["channel"],
                   platform=payload["platform"], package_name=payload["package_name"].strip(),
                   sha256=digest, minimum_core_version=str(payload.get("minimum_core_version", "")),
                   signature=str(payload.get("signature", "")))

    def to_dict(self) -> dict:
        return {"schema_version": 1, **asdict(self)}

    def signing_bytes(self) -> bytes:
        payload = self.to_dict()
        payload.pop("signature", None)
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


class DistributionService:
    channels = {"stable", "beta", "nightly"}
    platforms = {"windows", "linux"}

    def __init__(self, root: Path, signature_verifier=None, trusted_keys: dict[str, str] | None = None):
        self.root = Path(root)
        self.path = self.root / "distribution"
        self.path.mkdir(parents=True, exist_ok=True)
        self.trusted_keys = dict(trusted_keys or {})
        self.signature_verifier = signature_verifier or self.verify_signature
        self.history_path = self.path / "staged-updates.jsonl"

    def check_update(self, current: str, release: dict) -> dict:
        # Older local release records may be used for comparison only. They are
        # accepted here, but cannot pass verify_package/stage_package.
        if isinstance(release, dict) and not release.get("sha256"):
            if release.get("channel") not in self.channels or release.get("platform") not in self.platforms:
                raise ValueError("Invalid release manifest")
            manifest = ReleaseManifest(version=str(release.get("version", "")),
                channel=release["channel"], platform=release["platform"],
                package_name=str(release.get("package_name", "")), sha256="")
        else:
            manifest = ReleaseManifest.from_dict(release)
        available = manifest.version
        newer = self._version_key(available) > self._version_key(current)
        return {"available": newer, "current": current, "release": manifest.to_dict(),
                "backup_required": newer, "signature_verified": False,
                "application_state": "review-only"}

    def discover_feed(self, current: str, feed: Path | dict, *, platform: str = "windows",
                      core_version: str = "") -> dict:
        """Read and validate one signed release-feed entry; never installs it."""
        try:
            payload = json.loads(Path(feed).read_text(encoding="utf-8")) if isinstance(feed, (str, Path)) else feed
        except (OSError, json.JSONDecodeError) as exc:
            return {"state": "invalid-feed", "message": str(exc), "application_state": "review-only"}
        if not isinstance(payload, dict):
            return {"state": "invalid-feed", "message": "Release feed must be an object", "application_state": "review-only"}
        release = payload.get("release", payload)
        try:
            manifest = ReleaseManifest.from_dict(release)
        except ValueError as exc:
            return {"state": "invalid-feed", "message": str(exc), "application_state": "review-only"}
        if manifest.platform != platform:
            return {"state": "incompatible", "message": "Release platform is not supported", "application_state": "review-only"}
        if manifest.minimum_core_version and self._version_key(core_version) < self._version_key(manifest.minimum_core_version):
            return {"state": "incompatible", "message": "Release requires a newer Control Center", "application_state": "review-only"}
        if not self.verify_signature(manifest):
            return {"state": "invalid-signature", "message": "Release signature could not be verified", "application_state": "review-only"}
        result = self.check_update(current, manifest.to_dict())
        result.update({"state": "available" if result["available"] else "current", "signature_verified": True})
        return result

    def verify_package(self, package: Path, manifest: ReleaseManifest) -> bool:
        """Verify staged bytes; signature verification is intentionally a separate gate."""
        return Path(package).is_file() and self._sha256(Path(package)) == manifest.sha256

    def verify_signature(self, manifest: ReleaseManifest) -> bool:
        if not manifest.signature or not self.trusted_keys:
            return False
        try:
            key_id, encoded = manifest.signature.split(":", 1)
            key = Ed25519PublicKey.from_public_bytes(base64.b64decode(self.trusted_keys[key_id]))
            key.verify(base64.b64decode(encoded), manifest.signing_bytes())
            return True
        except (KeyError, ValueError, TypeError, InvalidSignature):
            return False

    def stage_package(self, package: Path, manifest: ReleaseManifest) -> Path:
        """Copy a verified package to a review-only staging directory."""
        source = Path(package)
        signature_ok = bool(manifest.signature and self.signature_verifier and
                            self.signature_verifier(manifest))
        result = {"version": manifest.version, "package_name": manifest.package_name,
                  "sha256": manifest.sha256, "signature_verified": signature_ok,
                  "status": "rejected"}
        if not signature_ok:
            self._record_stage(result)
            raise ValueError("Release signature could not be verified")
        if not self.verify_package(source, manifest):
            self._record_stage(result)
            raise ValueError("Package checksum does not match the release manifest")
        staging = self.path / "staged" / manifest.version
        staging.mkdir(parents=True, exist_ok=True)
        destination = staging / manifest.package_name
        shutil.copy2(source, destination)
        result["status"] = "staged"
        result["path"] = str(destination)
        self._record_stage(result)
        return destination

    def _record_stage(self, record: dict) -> None:
        with self.history_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")

    def backup_before_update(self, destination: Path) -> Path:
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        backup = destination / datetime.now(timezone.utc).strftime("backup-%Y%m%dT%H%M%SZ")
        shutil.copytree(self.root, backup, ignore=shutil.ignore_patterns("distribution"))
        return backup

    def repair_plan(self, installed_files: list[Path], expected_hashes: dict[str, str]) -> dict:
        missing, mismatched = [], []
        for path in installed_files:
            key = str(path)
            if not path.is_file():
                missing.append(key)
            elif key in expected_hashes and self._sha256(path) != expected_hashes[key]:
                mismatched.append(key)
        return {"missing": missing, "mismatched": mismatched, "repair_required": bool(missing or mismatched),
                "automatic_repair": False, "application_state": "review-only"}

    def uninstall_plan(self) -> dict:
        preserved = sorted(str(path.relative_to(self.root)) for path in self.root.iterdir()
                           if path.name not in {"distribution"})
        return {"application_state": "review-only", "preserve_data": True,
                "preserved_paths": preserved, "delete_installation_only": True,
                "automatic_delete": False}

    @staticmethod
    def _version_key(version: str) -> tuple:
        return tuple(int(part) if part.isdigit() else 0 for part in version.lstrip("v").split("."))

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
