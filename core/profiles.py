"""Profile storage for isolated Enshrouded configurations."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Profile:
    id: str
    name: str
    description: str = ""
    profile_type: str = "custom"
    enabled_packages: list[str] = field(default_factory=list)
    settings: dict = field(default_factory=dict)
    target_build: str | None = None
    last_known_good_operation: str | None = None


class ProfileService:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.directory = self.root / "profiles"

    def _path(self, profile_id: str) -> Path:
        if not profile_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in profile_id):
            raise ValueError("Invalid profile id")
        return self.directory / f"{profile_id}.json"

    def list(self) -> list[Profile]:
        profiles = []
        for path in sorted(self.directory.glob("*.json")) if self.directory.is_dir() else []:
            try:
                profiles.append(Profile(**json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, ValueError, TypeError):
                continue
        return profiles

    def save(self, profile: Profile) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self._path(profile.id)
        fd, temp_name = tempfile.mkstemp(prefix=f"{profile.id}-", suffix=".tmp", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(asdict(profile), handle, indent=2)
                handle.write("\n")
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def ensure_defaults(self) -> list[Profile]:
        if self.list():
            return self.list()
        defaults = [
            Profile("default", "Default", "Safe starting profile.", "stable"),
            Profile("research", "Research", "Isolated experimental profile.", "research"),
        ]
        for profile in defaults:
            self.save(profile)
        return defaults
