"""Safe package discovery and profile-scoped mod enablement."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from .profiles import Profile, ProfileService
from .compatibility import CompatibilityState, evaluate


MAX_ARCHIVE_ENTRIES = 2048
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024


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
        return cls.from_data(data, path.parent)

    @classmethod
    def from_data(cls, data: dict, directory: Path) -> "PackageManifest":
        if not isinstance(data, dict):
            raise ValueError("Package manifest must be an object")
        for field_name in ("id", "name", "version"):
            if not isinstance(data.get(field_name), str) or not data[field_name].strip():
                raise ValueError(f"Package {field_name} must be a non-empty string")
        package_id = str(data["id"])
        if not package_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for char in package_id):
            raise ValueError("Package id contains invalid characters")
        raw_required_builds = data.get("required_builds", [])
        raw_dependencies = data.get("dependencies", [])
        if not isinstance(raw_required_builds, list) or not isinstance(raw_dependencies, list):
            raise ValueError("Package required_builds and dependencies must be arrays")
        if any(not isinstance(value, str) for value in [*raw_required_builds, *raw_dependencies]):
            raise ValueError("Package build and dependency entries must be strings")
        package_type = data.get("package_type", "mod")
        if not isinstance(package_type, str) or not package_type.strip():
            raise ValueError("Package type must be a non-empty string")
        required_builds = tuple(str(value).strip() for value in raw_required_builds if str(value).strip())
        dependencies = tuple(str(value) for value in raw_dependencies)
        if any(not dependency or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for char in dependency) for dependency in dependencies):
            raise ValueError("Package dependency contains invalid characters")
        if len(set(dependencies)) != len(dependencies):
            raise ValueError("Package dependencies must be unique")
        if package_id in dependencies:
            raise ValueError("Package cannot depend on itself")
        return cls(
            id=package_id, name=data["name"].strip(), version=data["version"].strip(),
            author=str(data.get("author", "Unknown")), description=str(data.get("description", "")),
            package_type=package_type.strip(),
            required_builds=required_builds,
            dependencies=dependencies,
            path=Path(directory),
        )


@dataclass(frozen=True)
class DeploymentAction:
    package_id: str
    source: Path
    destination: Path
    status: str
    reason: str = ""


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
        directories = [self.seed_directory]
        if self.directory.is_dir():
            directories.append(self.directory)
        for directory in directories:
            if not directory.is_dir():
                continue
            for manifest_path in sorted(directory.glob("*/package.json")):
                try:
                    if manifest_path.parent.is_symlink():
                        continue
                    manifest = PackageManifest.from_file(manifest_path)
                    if manifest.id in self._packages:
                        if directory == self.directory:
                            self._packages[manifest.id] = manifest
                        continue
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
        else:
            dependents = [
                item.name for item in self._packages.values()
                if package_id in item.dependencies and self.is_enabled(profile, item.id)
            ]
            if dependents:
                raise ValueError(f"Disable dependent packages first: {', '.join(dependents)}")
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
        external_manifest_path = source / "mod.json"
        if not source.is_dir() or (not manifest_path.is_file() and not external_manifest_path.is_file()):
            raise ValueError("Package folder must contain package.json or mod.json")
        if any(item.is_symlink() for item in [source, *source.rglob("*")]):
            raise ValueError("Package folder contains an unsafe symlink")
        external = not manifest_path.is_file()
        if external:
            try:
                raw = json.loads(external_manifest_path.read_text(encoding="utf-8"))
                manifest_data = {
                    "id": raw.get("id"), "name": raw.get("name"), "version": raw.get("version"),
                    "author": raw.get("author", raw.get("publisher", "Unknown")),
                    "description": raw.get("description", "Imported external Enshrouded mod"),
                    "package_type": "mod", "required_builds": raw.get("required_builds", []),
                    "dependencies": raw.get("dependencies", []),
                }
                manifest = PackageManifest.from_data(manifest_data, external_manifest_path.parent)
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError("External mod.json is invalid") from exc
        else:
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
            if external:
                (staged / "package.json").write_text(json.dumps({
                    "id": manifest.id, "name": manifest.name, "version": manifest.version,
                    "author": manifest.author, "description": manifest.description,
                    "package_type": manifest.package_type,
                    "required_builds": list(manifest.required_builds),
                    "dependencies": list(manifest.dependencies),
                }, indent=2) + "\n", encoding="utf-8")
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
                members = bundle.infolist()
                if len(members) > MAX_ARCHIVE_ENTRIES:
                    raise ValueError("Package archive contains too many entries")
                if sum(member.file_size for member in members) > MAX_ARCHIVE_BYTES:
                    raise ValueError("Package archive is too large to import safely")
                member_names: set[str] = set()
                for member in members:
                    normalized_name = member.filename.replace("\\", "/")
                    if normalized_name in member_names:
                        raise ValueError("Package archive contains duplicate paths")
                    member_names.add(normalized_name)
                    unix_mode = (member.external_attr >> 16) & 0o170000
                    if unix_mode == 0o120000:
                        raise ValueError("Package archive contains an unsafe symlink")
                    target = (staging / member.filename).resolve()
                    windows_member = PureWindowsPath(member.filename)
                    if (windows_member.is_absolute() or ".." in windows_member.parts
                            or (staging.resolve() not in target.parents and target != staging.resolve())):
                        raise ValueError("Package archive contains an unsafe path")
                bundle.extractall(staging)
            candidates = [staging, *[item for item in staging.iterdir() if item.is_dir()]]
            source = next((item for item in candidates if (item / "package.json").is_file() or (item / "mod.json").is_file()), None)
            if source is None:
                raise ValueError("Package archive must contain package.json or mod.json")
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
        if managed_path.is_symlink():
            raise ValueError("Refusing to remove a symlinked package directory")
        shutil.rmtree(managed_path)
        self._packages.pop(package_id, None)

    def deployment_plan(self, profile: Profile, game_directory: Path) -> list[DeploymentAction]:
        """Describe enabled package destinations without changing the game."""
        destination_root = Path(game_directory) / "mods"
        actions: list[DeploymentAction] = []
        for package_id in profile.enabled_packages:
            package = self._packages.get(package_id)
            if not package or not package.path:
                actions.append(DeploymentAction(package_id, Path(), destination_root / package_id,
                                                "missing", "Package is not installed"))
                continue
            target = destination_root / package_id
            if target.exists():
                actions.append(DeploymentAction(package_id, package.path, target, "conflict",
                                                "Destination already exists"))
            else:
                actions.append(DeploymentAction(package_id, package.path, target, "ready"))
        return actions
