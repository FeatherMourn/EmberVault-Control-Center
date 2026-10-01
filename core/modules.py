"""Independent module manifests, registry discovery, and launch context."""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class ModuleState(StrEnum):
    INSTALLED = "installed"
    DISABLED = "disabled"
    EXPERIMENTAL = "experimental"
    INCOMPATIBLE = "incompatible"
    BROKEN = "broken"


@dataclass(frozen=True)
class ModuleManifest:
    id: str
    name: str
    version: str
    publisher: str
    executable: str | None = None
    minimum_core_version: str = "0.1.0"
    capabilities: tuple[str, ...] = ()
    feature_state: str = "stable"
    entrypoint: str | None = None
    path: Path | None = field(default=None, compare=False)

    @classmethod
    def from_file(cls, path: Path) -> "ModuleManifest":
        data = json.loads(path.read_text(encoding="utf-8"))
        for field_name in ("id", "name", "version"):
            if not isinstance(data.get(field_name), str) or not data[field_name].strip():
                raise ValueError(f"Module {field_name} must be a non-empty string")
        module_id = str(data["id"])
        if not module_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for char in module_id):
            raise ValueError("Module id contains invalid characters")
        executable = data.get("executable")
        if executable is not None:
            if not isinstance(executable, str) or not executable.strip():
                raise ValueError("Module executable must be a non-empty relative path")
            executable_path = Path(executable)
            if executable_path.is_absolute() or ".." in executable_path.parts:
                raise ValueError("Module executable must remain inside its package directory")
        raw_capabilities = data.get("capabilities", [])
        if not isinstance(raw_capabilities, list):
            raise ValueError("Module capabilities must be an array")
        if any(not isinstance(value, str) for value in raw_capabilities):
            raise ValueError("Module capability entries must be strings")
        capabilities = tuple(str(value).strip() for value in raw_capabilities)
        if any(not value for value in capabilities) or len(set(capabilities)) != len(capabilities):
            raise ValueError("Module capabilities must be non-empty and unique")
        return cls(
            id=module_id, name=data["name"].strip(), version=data["version"].strip(),
            publisher=str(data.get("publisher", "Unknown")), executable=executable,
            minimum_core_version=str(data.get("minimum_core_version", "0.1.0")),
            capabilities=capabilities,
            feature_state=str(data.get("feature_state", "stable")),
            entrypoint=data.get("entrypoint"), path=path.parent,
        )


@dataclass(frozen=True)
class LaunchContext:
    profile_id: str | None
    game_path: str | None
    operation_id: str | None


class ModuleRegistry:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        source_directory = Path(__file__).resolve().parents[1] / "modules"
        installed_directory = Path(sys.prefix) / "modules"
        self.seed_directory = source_directory if source_directory.is_dir() else installed_directory
        self._modules: dict[str, ModuleManifest] = {}

    def discover(self) -> dict[str, ModuleManifest]:
        self._modules = {}
        directories = [self.seed_directory]
        if self.directory.is_dir():
            directories.append(self.directory)
        for directory in directories:
            if not directory.is_dir():
                continue
            for manifest_path in sorted(directory.glob("*/module.json")):
                try:
                    manifest = ModuleManifest.from_file(manifest_path)
                    if manifest.id in self._modules:
                        if directory == self.directory:
                            self._modules[manifest.id] = manifest
                        continue
                    self._modules[manifest.id] = manifest
                except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                    continue
        return dict(self._modules)

    def get(self, module_id: str) -> ModuleManifest | None:
        return self._modules.get(module_id)

    def by_capability(self, capability: str) -> list[ModuleManifest]:
        return [m for m in self._modules.values() if capability in m.capabilities]

    def launch(self, module_id: str, context: LaunchContext) -> subprocess.Popen | None:
        manifest = self.get(module_id)
        if not manifest or not manifest.executable or not manifest.path:
            raise ValueError(f"Module '{module_id}' is not a separate-process module.")
        module_root = manifest.path.resolve()
        executable = (module_root / manifest.executable).resolve()
        if module_root not in executable.parents:
            raise ValueError("Module executable must remain inside its package directory.")
        if not executable.is_file():
            raise FileNotFoundError(executable)
        args = [str(executable), "--profile", context.profile_id or "", "--game-path", context.game_path or ""]
        if executable.suffix.lower() == ".py":
            args = [sys.executable, *args]
        if context.operation_id:
            args += ["--operation", context.operation_id]
        return subprocess.Popen(
            args,
            cwd=manifest.path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
