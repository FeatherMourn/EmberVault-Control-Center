"""Content Creator project metadata, separate from live game content."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path
from .storage import write_json_atomic


@dataclass
class ContentProject:
    id: str
    name: str
    profile_id: str
    status: str = "draft"
    description: str = ""
    design_type: str = "furniture"
    design_notes: str = ""
    asset_references: list[str] = field(default_factory=list)
    published: bool = False
    published_at: str = ""


class ContentProjectService:
    def __init__(self, root: Path):
        self.path = Path(root) / "content-projects" / "projects.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[ContentProject]:
        if not self.path.exists():
            return []
        try:
            projects = []
            raw_projects = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw_projects, list):
                return []
            for item in raw_projects:
                if not isinstance(item, dict):
                    continue
                try:
                    project = ContentProject(**item)
                except (TypeError, ValueError):
                    continue
                if project.status not in {"draft", "ready", "blocked"}:
                    project.status = "draft"
                if project.design_type not in {"furniture", "building", "recipe", "other"}:
                    project.design_type = "furniture"
                if not isinstance(project.design_notes, str):
                    project.design_notes = ""
                if not isinstance(project.asset_references, list):
                    project.asset_references = []
                else:
                    project.asset_references = [item.strip() for item in project.asset_references
                                                if isinstance(item, str) and item.strip() and not Path(item).is_absolute() and ".." not in Path(item).parts]
                if not isinstance(project.published, bool):
                    project.published = False
                if not isinstance(project.published_at, str):
                    project.published_at = ""
                projects.append(project)
            return projects
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def create(self, name: str, profile_id: str, description: str = "", design_type: str = "furniture", design_notes: str = "", asset_references: list[str] | None = None) -> ContentProject:
        if not name.strip() or not profile_id.strip():
            raise ValueError("Content project name and profile are required")
        if design_type not in {"furniture", "building", "recipe", "other"}:
            raise ValueError("Unknown content design type")
        references = self._normalize_asset_references(asset_references or [])
        project = ContentProject(f"EV-CONTENT-{uuid.uuid4().hex[:8].upper()}", name.strip(), profile_id,
                                 description=description.strip(), design_type=design_type,
                                 design_notes=design_notes.strip(), asset_references=references)
        projects = self.list()
        projects.append(project)
        write_json_atomic(self.path, [asdict(item) for item in projects])
        return project

    def set_status(self, project_id: str, status: str) -> ContentProject:
        if status not in {"draft", "ready", "blocked"}:
            raise ValueError("Unknown content project status")
        projects = self.list()
        for project in projects:
            if project.id == project_id:
                if status == "ready" and not project.description.strip():
                    raise ValueError("Add a development brief before marking content ready")
                project.status = status
                if project.published:
                    project.published = False
                    project.published_at = ""
                write_json_atomic(self.path, [asdict(item) for item in projects])
                return project
        raise KeyError(project_id)

    def update_design(self, project_id: str, design_type: str, design_notes: str, asset_references: list[str] | None = None) -> ContentProject:
        if design_type not in {"furniture", "building", "recipe", "other"}:
            raise ValueError("Unknown content design type")
        projects = self.list()
        for project in projects:
            if project.id == project_id:
                project.design_type = design_type
                project.design_notes = design_notes.strip()
                project.asset_references = self._normalize_asset_references(asset_references or [])
                if project.published:
                    project.published = False
                    project.published_at = ""
                write_json_atomic(self.path, [asdict(item) for item in projects])
                return project
        raise KeyError(project_id)

    @staticmethod
    def _normalize_asset_references(references: list[str]) -> list[str]:
        if not isinstance(references, list):
            raise ValueError("Asset references must be a list")
        result = []
        for reference in references:
            if not isinstance(reference, str) or not reference.strip():
                continue
            path = Path(reference.strip())
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Asset references must remain relative to the project")
            result.append(reference.strip())
        return list(dict.fromkeys(result))

    def publish(self, project_id: str) -> ContentProject:
        projects = self.list()
        for project in projects:
            if project.id == project_id:
                if project.status != "ready" or not project.description.strip():
                    raise ValueError("Mark the content project ready before publishing")
                project.published = True
                project.published_at = datetime.now(timezone.utc).isoformat()
                write_json_atomic(self.path, [asdict(item) for item in projects])
                return project
        raise KeyError(project_id)

    def unpublish(self, project_id: str) -> ContentProject:
        projects = self.list()
        for project in projects:
            if project.id == project_id:
                project.published = False
                project.published_at = ""
                write_json_atomic(self.path, [asdict(item) for item in projects])
                return project
        raise KeyError(project_id)

    def export(self, project: ContentProject) -> Path:
        """Export project metadata without touching live game content."""
        destination = self.path.parent.parent / "exports" / "content-projects" / f"{project.id}.json"
        write_json_atomic(destination, {
            "schema_version": 1,
            "project": asdict(project),
            "application_state": "design-only",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        })
        return destination
