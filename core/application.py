"""Composition root for Embervault Core services."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .game_detection import GameDetector
from .game_settings import GameSettingsService
from .knowledge import KnowledgeService
from .logging_service import StructuredLogService
from .modules import ModuleRegistry
from .operations import OperationService
from .packages import PackageService
from .profiles import ProfileService
from .research import ResearchService
from .save_manager import SaveManagerService
from .save_workflow import SaveWorkflowService
from .settings import SettingsService
from .troubleshooter import TroubleshooterService


@dataclass
class EmbervaultRuntime:
    root: Path
    settings: SettingsService
    profiles: ProfileService
    logs: StructuredLogService
    operations: OperationService
    saves: SaveManagerService
    modules: ModuleRegistry
    game: GameDetector
    save_workflow: SaveWorkflowService
    packages: PackageService
    troubleshooter: TroubleshooterService
    game_settings: GameSettingsService
    research: ResearchService
    knowledge: KnowledgeService

    @classmethod
    def create(cls, root: Path) -> "EmbervaultRuntime":
        root = Path(root)
        runtime = cls(
            root=root,
            settings=SettingsService(root),
            profiles=ProfileService(root),
            logs=StructuredLogService(root / "logs" / "events.jsonl"),
            operations=OperationService(root / "operations.jsonl"),
            saves=SaveManagerService(root),
            modules=ModuleRegistry(root / "modules"),
            game=GameDetector(),
            save_workflow=None,  # wired immediately below after shared services exist
            packages=None,  # wired immediately below after profiles exist
            troubleshooter=None,
            game_settings=None,
            research=None,
            knowledge=None,
        )
        runtime.save_workflow = SaveWorkflowService(runtime.saves, runtime.operations, runtime.logs)
        runtime.profiles.ensure_defaults()
        runtime.packages = PackageService(root, runtime.profiles)
        runtime.packages.discover()
        runtime.troubleshooter = TroubleshooterService(
            root, runtime.settings, runtime.profiles, runtime.modules, runtime.packages, runtime.game
        )
        runtime.game_settings = GameSettingsService(runtime.profiles)
        runtime.research = ResearchService(root)
        runtime.knowledge = KnowledgeService(root.parent)
        runtime.modules.discover()
        runtime.logs.info("Embervault Core initialized")
        return runtime

    def health(self) -> dict:
        settings = self.settings.load()
        installation = self.game.detect(Path(settings.game_path)) if settings.game_path else None
        return {
            "core": "ready",
            "game": installation.to_dict() if installation else None,
            "profiles": len(self.profiles.list()),
            "modules": len(self.modules.discover()),
            "backups": len(self.saves.list_backups()),
            "packages": len(self.packages.list()),
        }
