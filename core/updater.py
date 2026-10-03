"""External updater planning and recovery metadata.

This layer deliberately prepares a replacement contract but does not replace a
running installation. A future helper process can consume the contract after
the Control Center exits.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class UpdatePlan:
    version: str
    staged_package: str
    installation: str
    backup: str
    startup_probe: str
    status: str = "review-only"

    def to_dict(self) -> dict:
        return {"schema_version": 1, **asdict(self)}


class ExternalUpdaterService:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.path = self.root / "distribution" / "updater"
        self.path.mkdir(parents=True, exist_ok=True)

    def prepare(self, version: str, staged_package: Path, installation: Path,
                startup_probe: str = "--smoke-test") -> Path:
        staged_package = Path(staged_package).resolve()
        installation = Path(installation).resolve()
        if not staged_package.is_file():
            raise ValueError("Staged update package is missing")
        if not installation.exists():
            raise ValueError("Installation target is missing")
        backup = self.path / "backups" / datetime.now(timezone.utc).strftime("backup-%Y%m%dT%H%M%SZ")
        plan = UpdatePlan(version=version, staged_package=str(staged_package),
                          installation=str(installation), backup=str(backup),
                          startup_probe=startup_probe)
        destination = self.path / "pending-update.json"
        destination.write_text(json.dumps(plan.to_dict(), indent=2) + "\n", encoding="utf-8")
        return destination

    def backup(self, plan_file: Path) -> Path:
        plan = json.loads(Path(plan_file).read_text(encoding="utf-8"))
        backup = Path(plan["backup"])
        source = Path(plan["installation"])
        if backup.exists():
            raise ValueError("Rollback backup already exists")
        shutil.copytree(source, backup)
        return backup

    def approve(self, plan_file: Path) -> Path:
        path = Path(plan_file)
        plan = json.loads(path.read_text(encoding="utf-8"))
        plan["status"] = "approved"
        path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        return path

    def helper_command(self, plan_file: Path) -> list[str]:
        plan = json.loads(Path(plan_file).read_text(encoding="utf-8"))
        if plan.get("status") != "approved":
            raise ValueError("External updater requires explicit approval")
        return ["python", "tools/external_updater.py", "--plan", str(Path(plan_file).resolve())]

    def apply_approved(self, plan_file: Path, startup_probe) -> bool:
        """Replace an installation and roll back when the supplied probe fails."""
        plan = json.loads(Path(plan_file).read_text(encoding="utf-8"))
        if plan.get("status") != "approved":
            raise ValueError("External updater requires explicit approval")
        source, target, backup = Path(plan["staged_package"]), Path(plan["installation"]), Path(plan["backup"])
        if not source.is_file() or not target.is_dir():
            raise ValueError("Approved update paths are invalid")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            raise ValueError("Rollback backup already exists")
        shutil.copytree(target, backup)
        with tempfile.TemporaryDirectory(dir=target.parent) as temp:
            incoming = Path(temp) / "incoming"
            incoming.mkdir()
            with zipfile.ZipFile(source) as archive:
                for member in archive.infolist():
                    destination = (incoming / member.filename).resolve()
                    if incoming.resolve() not in destination.parents:
                        raise ValueError("Update archive contains an unsafe path")
                archive.extractall(incoming)
            old = target.with_name(target.name + ".old")
            target.rename(old)
            incoming.rename(target)
            try:
                if not startup_probe(plan["startup_probe"]):
                    raise RuntimeError("Updated application failed startup probe")
            except Exception:
                if target.exists():
                    shutil.rmtree(target)
                old.rename(target)
                plan["status"] = "rolled-back"
                Path(plan_file).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
                return False
            shutil.rmtree(old)
        plan["status"] = "applied"
        Path(plan_file).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        return True

    def recover_pending(self, plan_file: Path) -> str:
        """Recover a plan left behind by an interrupted helper process."""
        path = Path(plan_file)
        plan = json.loads(path.read_text(encoding="utf-8"))
        target, backup = Path(plan["installation"]), Path(plan["backup"])
        old = target.with_name(target.name + ".old")
        if plan.get("status") in {"applied", "rolled-back"}:
            return plan["status"]
        if target.exists() and old.exists():
            shutil.rmtree(old)
            plan["status"] = "applied-recovered"
        elif not target.exists() and old.exists():
            old.rename(target)
            plan["status"] = "rolled-back-recovered"
        elif target.exists() and backup.exists():
            plan["status"] = "pending-review"
        else:
            plan["status"] = "recovery-required"
        path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        return plan["status"]

    @staticmethod
    def validate_startup(exit_code: int, expected_code: int = 0) -> bool:
        return exit_code == expected_code
