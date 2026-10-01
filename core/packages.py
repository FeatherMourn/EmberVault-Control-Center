"""Safe package discovery and profile-scoped mod enablement."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .profiles import Profile, ProfileService
from .compatibility import CompatibilityState, evaluate


@dataclass(frozen=True)
class PackageManifest:
    id: str
    name: str
    version: str
    author: str = "Unknown"
    description: str = ""
    package_type: str = "mod"
    required_builds: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    path: Path | None = None

    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        data = json.loads(path.read_text(encoding="utf-8"))
        package_id = str(data["id"])
        if not package_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for char in package_id):
            raise ValueError("Package id contains invalid characters")
        return cls(
            id=package_id, name=str(data["name"]), version=str(data["version"]),
            author=str(data.get("author", "Unknown")), description=str(data.get("description", "")),
            package_type=str(data.get("package_type", "mod")),
            required_builds=tuple(str(value) for value in data.get("required_builds", [])),
            dependencies=tuple(str(value) for value in data.get("dependencies", [])),
            path=path.parent,
        )


class PackageService:
    """Discover packages and change only profile enablement state."""

    def __init__(self, root: Path, profiles: ProfileService):
        self.root = Path(root)
        self.directory = self.root / "packages"
        source_directory = Path(__file__).resolve().parents[1] / "packages"
        installed_directory = Path(sys.prefix) / "packages"
        self.seed_directory = source_directory if source_directory.is_dir() else installed_directory
        self.profiles = profiles
        self._packages: dict[str, PackageManifest] = {}

    def discover(self) -> dict[str, PackageManifest]:
        self._packages = {}
        directory = self.directory if self.directory.is_dir() else self.seed_directory
        if not directory.is_dir():
            return {}
        for manifest_path in sorted(directory.glob("*/package.json")):
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

    def set_enabled(self, profile: Profile, package_id: str, enabled: bool, detected_build: str | None = None) -> Profile:
        if package_id not in self._packages:
            raise ValueError(f"Unknown package: {package_id}")
        if enabled:
            compatibility = evaluate(required_builds=list(self._packages[package_id].required_builds), detected_build=detected_build)
            if compatibility.state == CompatibilityState.INCOMPATIBLE:
                raise ValueError("Package is incompatible with the detected game build")
            missing = [
                dependency for dependency in self._packages[package_id].dependencies
                if dependency not in self._packages or not self.is_enabled(profile, dependency)
            ]
            if missing:
                raise ValueError(f"Enable package dependencies first: {', '.join(missing)}")
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
        # Stage outside the managed directory so a failed copy cannot leave a
        # package that discovery might mistake for an installed package.
        with tempfile.TemporaryDirectory(prefix="embervault-package-stage-", dir=self.directory.parent) as temp:
            staged = Path(temp) / manifest.id
            shutil.copytree(source, staged)
            shutil.move(str(staged), str(target))
        self._packages[manifest.id] = PackageManifest.from_file(target / "package.json")
        return self._packages[manifest.id]

    def install_from_archive(self, archive: Path) -> PackageManifest:
        archive = Path(archive)
        if not archive.is_file() or archive.suffix.lower() != ".zip":
            raise ValueError("Package archive must be a .zip file")
        with tempfile.TemporaryDirectory(prefix="embervault-package-") as temp:
            staging = Path(temp)
            with zipfile.ZipFile(archive) as bundle:
                for member in bundle.infolist():
                    target = (staging / member.filename).resolve()
                    if staging.resolve() not in target.parents and target != staging.resolve():
                        raise ValueError("Package archive contains an unsafe path")
                bundle.extractall(staging)
            candidates = [staging, *[item for item in staging.iterdir() if item.is_dir()]]
            source = next((item for item in candidates if (item / "package.json").is_file()), None)
            if source is None:
                raise ValueError("Package archive must contain package.json")
            return self.install_from_directory(source)

    def remove(self, package_id: str) -> None:
        package = self.get(package_id)
        if not package or not package.path:
            raise ValueError(f"Unknown installed package: {package_id}")
        if any(package_id in profile.enabled_packages for profile in self.profiles.list()):
            raise ValueError("Disable the package in every profile before removing it")
        dependents = [item.name for item in self._packages.values() if package_id in item.dependencies]
        if dependents:
            raise ValueError(f"Remove dependent packages first: {', '.join(dependents)}")
        managed_path = self.directory / package_id
        if not managed_path.is_dir():
            raise ValueError("Seed packages cannot be removed from the repository")
        shutil.rmtree(managed_path)
        self._packages.pop(package_id, None)
