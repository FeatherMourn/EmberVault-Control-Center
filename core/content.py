"""Content Creator project metadata, separate from live game content."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from .storage import write_json_atomic


@dataclass
class ContentProject:
    id: str
    name: str
    profile_id: str
    status: str = "draft"
    description: str = ""


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
                projects.append(project)
            return projects
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return []

    def create(self, name: str, profile_id: str, description: str = "") -> ContentProject:
        if not name.strip() or not profile_id.strip():
            raise ValueError("Content project name and profile are required")
        project = ContentProject(f"EV-CONTENT-{uuid.uuid4().hex[:8].upper()}", name.strip(), profile_id, description=description.strip())
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
                write_json_atomic(self.path, [asdict(item) for item in projects])
                return project
        raise KeyError(project_id)
