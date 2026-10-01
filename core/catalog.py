"""Portable catalog export for the Ember Vault website and research hub."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .knowledge import KnowledgeService
from .modules import ModuleRegistry
from .packages import PackageService
from .research import ResearchService
from .content import ContentProjectService
from .storage import write_json_atomic


class CatalogExportService:
    def __init__(self, root: Path, modules: ModuleRegistry, packages: PackageService,
                 knowledge: KnowledgeService, research: ResearchService):
        self.root = Path(root)
        self.modules = modules
        self.packages = packages
        self.knowledge = knowledge
        self.research = research
        self.content = None

    def set_content(self, content: ContentProjectService) -> None:
        self.content = content

    def build(self) -> dict:
        packages = sorted(self.packages.list(), key=lambda item: item.id)
        modules = sorted(self.modules.discover().values(), key=lambda item: item.id)
        knowledge = sorted(self.knowledge.entries(), key=lambda item: item.id)
        research = sorted((item for item in self.research.list() if item.published), key=lambda item: item.id)
        content = sorted((item for item in (self.content.list() if self.content else []) if item.published), key=lambda item: item.id)
        return {
            "schema_version": 1,
            "contract_versions": {"module_manifest": 1, "package_manifest": 1, "research_record": 1, "content_project": 1},
            "packages": [asdict(item) | {"path": None} for item in packages],
            "modules": [asdict(item) | {"path": None} for item in modules],
            "knowledge": [asdict(item) for item in knowledge],
            "research": [{"id": item.id, "title": item.title, "hypothesis": item.hypothesis,
                          "status": item.status, "evidence_count": len(item.evidence),
                          "created_at": item.created_at, "published_at": item.published_at} for item in research],
            "content_projects": [{"id": item.id, "name": item.name, "status": item.status,
                                  "published_at": item.published_at} for item in content],
        }

    @staticmethod
    def validate(payload: dict) -> None:
        """Validate the public handoff without requiring a web runtime."""
        if not isinstance(payload, dict) or payload.get("schema_version") != 1:
            raise ValueError("Catalog schema version must be 1")
        required = ("contract_versions", "packages", "modules", "knowledge", "research", "content_projects")
        if any(key not in payload for key in required):
            raise ValueError("Catalog is missing a required collection")
        if not isinstance(payload["contract_versions"], dict):
            raise ValueError("Catalog contract versions must be an object")
        for key in ("module_manifest", "package_manifest"):
            if not isinstance(payload["contract_versions"].get(key), int):
                raise ValueError(f"Catalog contract version is missing: {key}")
        for collection in ("packages", "modules", "knowledge", "research", "content_projects"):
            if not isinstance(payload[collection], list):
                raise ValueError(f"Catalog collection is not an array: {collection}")
        for item in payload["research"]:
            if not isinstance(item, dict) or set(item) != {"id", "title", "hypothesis", "status", "evidence_count", "created_at", "published_at"}:
                raise ValueError("Research catalog records must remain sanitized")
            if item["status"] != "completed" or not isinstance(item["evidence_count"], int) or item["evidence_count"] < 1:
                raise ValueError("Research catalog records must be completed with evidence")
        for item in payload["content_projects"]:
            if not isinstance(item, dict) or set(item) != {"id", "name", "status", "published_at"}:
                raise ValueError("Content catalog records must remain sanitized")
            if item["status"] != "ready":
                raise ValueError("Only ready content projects may be public")

    def export(self, destination: Path) -> Path:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = self.build()
        self.validate(payload)
        write_json_atomic(destination, payload)
        return destination
