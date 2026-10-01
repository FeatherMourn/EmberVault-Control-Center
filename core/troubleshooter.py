"""Read-only health checks for the Control Center workspace."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .game_detection import GameDetector
from .compatibility import CompatibilityState, evaluate
from .modules import ModuleRegistry
from .packages import PackageService
from .profiles import ProfileService
from .settings import SettingsService


@dataclass(frozen=True)
class Diagnostic:
    key: str
    title: str
    severity: str
    message: str


class TroubleshooterService:
    def __init__(self, root: Path, settings: SettingsService, profiles: ProfileService,
                 modules: ModuleRegistry, packages: PackageService, detector: GameDetector):
        self.root = Path(root)
        self.settings = settings
        self.profiles = profiles
        self.modules = modules
        self.packages = packages
        self.detector = detector

    def scan(self) -> list[Diagnostic]:
        findings: list[Diagnostic] = []
        settings = self.settings.load()
        detected_build = None
        if not settings.game_path:
            findings.append(Diagnostic("game-path", "Game location", "attention", "Choose the Enshrouded installation folder."))
        else:
            installation = self.detector.detect(Path(settings.game_path))
            detected_build = installation.build_id
            issues = self.detector.validate(installation)
            if issues:
                findings.append(Diagnostic("game-installation", "Game installation", "attention", "; ".join(issues)))
            else:
                findings.append(Diagnostic("game-installation", "Game installation", "ready", "Installation detected and readable."))
        profiles = self.profiles.list()
        findings.append(Diagnostic("profiles", "Profiles", "ready" if profiles else "attention",
                                   f"{len(profiles)} profile{'s' if len(profiles) != 1 else ''} available."))
        modules = self.modules.discover()
        findings.append(Diagnostic("modules", "Module registry", "ready", f"{len(modules)} module manifest{'s' if len(modules) != 1 else ''} discovered."))
        packages = self.packages.list()
        findings.append(Diagnostic("packages", "Package registry", "ready", f"{len(packages)} package{'s' if len(packages) != 1 else ''} discovered."))
        for package in packages:
            compatibility = evaluate(required_builds=list(package.required_builds), detected_build=detected_build)
            if compatibility.state in {CompatibilityState.INCOMPATIBLE, CompatibilityState.BLOCKED}:
                findings.append(Diagnostic(
                    f"package-{package.id}", package.name, "attention",
                    "; ".join(compatibility.reasons),
                ))
        return findings
