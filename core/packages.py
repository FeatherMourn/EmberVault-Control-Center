"""Safe package discovery and profile-scoped mod enablement."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .profiles import Profile, ProfileService


@dataclass(frozen=True)
class PackageManifest:
    id: str
    name: str
    version: str
    author: str = "Unknown"
    description: str = ""
    package_type: str = "mod"
    required_builds: tuple[str, ...] = ()
    path: Path | None = None

    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            id=str(data["id"]), name=str(data["name"]), version=str(data["version"]),
            author=str(data.get("author", "Unknown")), description=str(data.get("description", "")),
            package_type=str(data.get("package_type", "mod")),
            required_builds=tuple(str(value) for value in data.get("required_builds", [])),
            path=path.parent,
        )


class PackageService:
    """Discover packages and change only profile enablement state."""

    def __init__(self, root: Path, profiles: ProfileService):
        self.root = Path(root)
        self.directory = self.root / "packages"
        self.profiles = profiles
        self._packages: dict[str, PackageManifest] = {}

    def discover(self) -> dict[str, PackageManifest]:
        self._packages = {}
        if not self.directory.is_dir():
            return {}
        for manifest_path in sorted(self.directory.glob("*/package.json")):
            try:
                manifest = PackageManifest.from_file(manifest_path)
                if manifest.id in self._packages:
                    raise ValueError(f"Duplicate package id: {manifest.id}")
                self._packages[manifest.id] = manifest
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
        return dict(self._packages)

    def list(self) -> list[PackageManifest]:
        return list(self.discover().values())

    def get(self, package_id: str) -> PackageManifest | None:
        return self._packages.get(package_id)

    def is_enabled(self, profile: Profile, package_id: str) -> bool:
        return package_id in profile.enabled_packages

    def set_enabled(self, profile: Profile, package_id: str, enabled: bool) -> Profile:
        if package_id not in self._packages:
            raise ValueError(f"Unknown package: {package_id}")
        enabled_packages = set(profile.enabled_packages)
        if enabled:
            enabled_packages.add(package_id)
        else:
            enabled_packages.discard(package_id)
        updated = Profile(**{**profile.__dict__, "enabled_packages": sorted(enabled_packages)})
        self.profiles.save(updated)
        return updated

    def install_from_directory(self, source: Path) -> PackageManifest:
        """Import a package directory after validating its manifest."""
        source = Path(source)
        manifest_path = source / "package.json"
        if not source.is_dir() or not manifest_path.is_file():
            raise ValueError("Package folder must contain package.json")
        manifest = PackageManifest.from_file(manifest_path)
        if manifest.id in self._packages or any(item.id == manifest.id for item in self.list()):
            raise ValueError(f"Package already installed: {manifest.id}")
        target = self.directory / manifest.id
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
        self._packages[manifest.id] = PackageManifest.from_file(target / "package.json")
        return self._packages[manifest.id]
