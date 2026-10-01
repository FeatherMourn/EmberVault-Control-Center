"""Portable catalog export for the Ember Vault website and research hub."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .knowledge import KnowledgeService
from .modules import ModuleRegistry
from .packages import PackageService
from .research import ResearchService
from .storage import write_json_atomic


class CatalogExportService:
    def __init__(self, root: Path, modules: ModuleRegistry, packages: PackageService,
                 knowledge: KnowledgeService, research: ResearchService):
        self.root = Path(root)
        self.modules = modules
        self.packages = packages
        self.knowledge = knowledge
        self.research = research

    def build(self) -> dict:
        packages = sorted(self.packages.list(), key=lambda item: item.id)
        modules = sorted(self.modules.discover().values(), key=lambda item: item.id)
        knowledge = sorted(self.knowledge.entries(), key=lambda item: item.id)
        research = sorted((item for item in self.research.list() if item.published), key=lambda item: item.id)
        return {
            "schema_version": 1,
            "contract_versions": {"module_manifest": 1, "package_manifest": 1, "research_record": 1},
            "packages": [asdict(item) | {"path": None} for item in packages],
            "modules": [asdict(item) | {"path": None} for item in modules],
            "knowledge": [asdict(item) for item in knowledge],
            "research": [{"id": item.id, "title": item.title, "hypothesis": item.hypothesis,
                          "status": item.status, "evidence_count": len(item.evidence),
                          "created_at": item.created_at, "published_at": item.published_at} for item in research],
        }

    def export(self, destination: Path) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(destination, self.build())
        return destination
