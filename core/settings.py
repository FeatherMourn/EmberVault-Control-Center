"""Persistent application settings with atomic writes."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Settings:
    game_path: str | None = None
    backup_directory: str | None = None
    module_directory: str | None = None
    update_channel: str = "stable"
    theme: str = "ember-dark"
    advanced_mode: bool = False


class SettingsService:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.path = self.root / "settings.json"

    def load(self) -> Settings:
        if not self.path.is_file():
            return Settings()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return Settings(**{k: raw[k] for k in asdict(Settings()) if k in raw})
        except (OSError, ValueError, TypeError):
            return Settings()

    def save(self, settings: Settings) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix="settings-", suffix=".tmp", dir=self.root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(asdict(settings), handle, indent=2)
                handle.write("\n")
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
