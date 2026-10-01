"""Portable catalog export for the Ember Vault website and research hub."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .knowledge import KnowledgeService
from .modules import ModuleRegistry
from .packages import PackageService


class CatalogExportService:
    def __init__(self, root: Path, modules: ModuleRegistry, packages: PackageService, knowledge: KnowledgeService):
        self.root = Path(root)
        self.modules = modules
        self.packages = packages
        self.knowledge = knowledge

    def build(self) -> dict:
        return {
            "schema_version": 1,
            "packages": [asdict(item) | {"path": None} for item in self.packages.list()],
            "modules": [asdict(item) | {"path": None} for item in self.modules.discover().values()],
            "knowledge": [asdict(item) for item in self.knowledge.entries()],
        }

    def export(self, destination: Path) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return destination
