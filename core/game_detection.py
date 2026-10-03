"""Read-only Enshrouded installation and runtime detection."""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class GameInstallation:
    path: Path
    executable: Path
    build_id: str | None
    running: bool
    saves_path: Path | None

    def to_dict(self) -> dict:
        result = asdict(self)
        for key in ("path", "executable", "saves_path"):
            if result[key] is not None:
                result[key] = str(result[key])
        return result


class GameDetector:
    """Detect a selected installation without changing game files."""

    def __init__(self, saves_root: Path | None = None):
        self.saves_root = saves_root

    @staticmethod
    def is_running(process_name: str = "enshrouded.exe") -> bool:
        try:
            output = subprocess.check_output(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                text=True, stderr=subprocess.DEVNULL,
            )
            return process_name.lower() in output.lower()
        except (OSError, subprocess.SubprocessError):
            return False

    @staticmethod
    def _build_id(game_dir: Path) -> str | None:
        for parent in (game_dir, *game_dir.parents):
            manifest = parent / "steamapps" / "appmanifest_1203620.acf"
            if not manifest.is_file():
                continue
            try:
                match = re.search(r'"buildid"\s+"(\d+)"', manifest.read_text(errors="ignore"), re.I)
                return match.group(1) if match else None
            except OSError:
                return None
        return None

    def detect(self, game_dir: Path) -> GameInstallation:
        path = Path(game_dir).expanduser().resolve()
        executable = path / "Enshrouded.exe"
        saves = self.saves_root or Path(os.environ.get("APPDATA", "")) / "Enshrouded"
        saves_path = saves if saves.is_dir() else None
        return GameInstallation(path, executable, self._build_id(path), self.is_running(), saves_path)

    def discover(self, roots: list[Path] | None = None) -> list[GameInstallation]:
        """Suggest likely installations without selecting or modifying one."""
        roots = roots or [Path("C:/"), Path("D:/"), Path("E:/"), Path("F:/"), Path("G:/"), Path("H:/")]
        candidates: list[Path] = []
        for root in roots:
            candidates.extend([
                root / "SteamLibrary" / "steamapps" / "common" / "Enshrouded",
                root / "Program Files (x86)" / "Steam" / "steamapps" / "common" / "Enshrouded",
                root / "Program Files" / "Steam" / "steamapps" / "common" / "Enshrouded",
            ])
        seen: set[Path] = set()
        results: list[GameInstallation] = []
        for candidate in candidates:
            try:
                resolved = candidate.resolve()
            except OSError:
                continue
            if resolved in seen or not (resolved / "Enshrouded.exe").is_file():
                continue
            seen.add(resolved)
            results.append(self.detect(resolved))
        return results

    def validate(self, installation: GameInstallation) -> list[str]:
        issues: list[str] = []
        if not installation.path.is_dir():
            issues.append("Game directory does not exist.")
        if not installation.executable.is_file():
            issues.append("Enshrouded.exe was not found.")
        if installation.build_id is None:
            issues.append("Steam build evidence is unavailable.")
        return issues
