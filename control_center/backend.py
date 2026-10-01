"""Qt-facing adapter for the first Control Center vertical slice."""
from __future__ import annotations

from pathlib import Path
import json
import subprocess

from core.application import EmbervaultRuntime
from core.game_detection import GameDetector
from core.profiles import ProfileService
from core.save_manager import SaveManagerError, SaveManagerService
from core.save_workflow import SaveWorkflowService
from core.settings import SettingsService
from core.operations import OperationStatus
from core.compatibility import evaluate
from core.modules import LaunchContext

MAX_WORKER_OUTPUT = 1024 * 1024

try:
    from PySide6.QtCore import QObject, Property, Signal, Slot
except ImportError:  # Keep core imports and headless checks usable without Qt.
    QObject = object  # type: ignore[misc,assignment]
    class _Signal:
        def emit(self):
            return None
    Signal = lambda *args, **kwargs: _Signal()  # type: ignore[assignment]
    Property = lambda _type, notify=None: (lambda fn: property(fn))  # type: ignore[assignment]
    def Slot(*args, **kwargs):  # type: ignore[no-redef]
        return lambda fn: fn


class ControlCenterBackend(QObject):
    stateChanged = Signal() if QObject is not object else None

    def __init__(self, data_root: Path, parent=None, runtime: EmbervaultRuntime | None = None):
        super().__init__(parent) if QObject is not object else super().__init__()
        self.data_root = Path(data_root)
        self.settings_service = SettingsService(self.data_root)
        self.settings = self.settings_service.load()
        self.profile_service = ProfileService(self.data_root)
        self.profiles = self.profile_service.ensure_defaults()
        self.save_manager = runtime.saves if runtime else SaveManagerService(self.data_root)
        self.save_workflow = runtime.save_workflow if runtime else None
        self.operations = runtime.operations if runtime else None
        self.logs = runtime.logs if runtime else None
        self.modules = runtime.modules if runtime else None
        self.packages = runtime.packages if runtime else None
        self.troubleshooter = runtime.troubleshooter if runtime else None
        self.game_settings = runtime.game_settings if runtime else None
        self.research = runtime.research if runtime else None
        self.knowledge = runtime.knowledge if runtime else None
        self.catalog = runtime.catalog if runtime else None
        self.content = runtime.content if runtime else None
        self.characters = runtime.characters if runtime else None
        self.risk = runtime.risk if runtime else None
        self.launcher = runtime.launcher if runtime else None
        self.detector = runtime.game if runtime else GameDetector()
        self._game_status = "Not configured"
        self._build = "Unknown build"
        self._profile_name = self.profiles[0].name if self.profiles else "No profile"
        self._safety = "No backup required"
        self._save_directory = ""
        self._last_save_message = "No save selected"
        self._selected_backup_id = ""
        self._restore_preview = "No restore selected"
        self._selected_profile_id = self.profiles[0].id if self.profiles else ""
        self._knowledge_query = ""

    @Property(str, notify=stateChanged)
    def gameStatus(self):
        return self._game_status

    @Property(str, notify=stateChanged)
    def gameBuild(self):
        return self._build

    @Property(str, notify=stateChanged)
    def profileName(self):
        return self._profile_name

    @Property(str, notify=stateChanged)
    def safetySummary(self):
        return self._safety

    @Property(str, notify=stateChanged)
    def saveSummary(self):
        count = len(self.save_manager.list_backups())
        return f"{count} verified backup{'s' if count != 1 else ''}"

    @Property(bool, notify=stateChanged)
    def canBackup(self):
        return bool(self._save_directory)

    @Property(str, notify=stateChanged)
    def lastSaveMessage(self):
        return self._last_save_message

    @Property("QStringList", notify=stateChanged)
    def profileOptions(self):
        return [profile.name for profile in self.profiles]

    @Property("QStringList", notify=stateChanged)
    def backupOptions(self):
        return [backup.id for backup in self.save_manager.list_backups()]

    @Property(str, notify=stateChanged)
    def restorePreview(self):
        return self._restore_preview

    @Property("QStringList", notify=stateChanged)
    def recentOperations(self):
        if not self.operations:
            return []
        return [
            f"{operation.operation_type} · {operation.status} · {operation.message}"
            for operation in self.operations.list_recent(8)
        ]

    @Property("QStringList", notify=stateChanged)
    def moduleOptions(self):
        if not self.modules:
            return []
        return [
            f"{module.name} · v{module.version} · {module.publisher} · {module.feature_state} · "
            f"{', '.join(module.capabilities) or 'no declared capabilities'}"
            for module in self.modules.discover().values()
        ]

    @Property("QStringList", notify=stateChanged)
    def packageOptions(self):
        if not getattr(self, "packages", None):
            return []
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            return []
        detected_build = self._build if self._build not in {"Unknown build", "Choose game folder"} else None
        return [
            f"{'Enabled' if self.packages.is_enabled(profile, package.id) else 'Disabled'} · "
            f"{package.name} · {package.package_type} · {package.version} · "
            f"Compatibility: {evaluate(required_builds=list(package.required_builds), detected_build=detected_build).state}"
            + (f" · Depends on: {', '.join(package.dependencies)}" if package.dependencies else "")
            for package in self.packages.list()
        ]

    @Property("QStringList", notify=stateChanged)
    def externalPackageOptions(self):
        if not self.packages or not self.settings.game_path:
            return []
        external = self.packages.inspect_external(Path(self.settings.game_path) / "mods")
        managed = {item.id for item in self.packages.list()}
        return [f"External · {item.name} · v{item.version} · {item.id}"
                for item in external if item.id not in managed]

    @Property("QStringList", notify=stateChanged)
    def deploymentOptions(self):
        if not self.packages or not self.settings.game_path:
            return ["Choose a game folder to inspect deployment readiness."]
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            return []
        plan = self.packages.deployment_plan(profile, Path(self.settings.game_path))
        return (["No enabled packages to deploy."] if not plan else
                [f"{item.status.upper()} · {item.package_id} · {item.reason or item.destination}"
                 for item in plan])

    @Slot()
    def inspectDeploymentPlan(self):
        if not self.packages or not self.settings.game_path:
            self._last_save_message = "Choose a game folder before inspecting deployment"
        else:
            profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
            plan = self.packages.deployment_plan(profile, Path(self.settings.game_path)) if profile else []
            ready = sum(1 for item in plan if item.status == "ready")
            conflicts = sum(1 for item in plan if item.status != "ready")
            self._last_save_message = f"Deployment plan: {ready} ready, {conflicts} requiring attention"
        self.stateChanged.emit()

    @Slot()
    def deployReadyPackages(self):
        if not self.packages or not self.settings.game_path:
            self._last_save_message = "Choose a game folder before deploying packages"
        else:
            profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
            operation = self.operations.start("package-deploy", profile_id=self._selected_profile_id) if self.operations else None
            try:
                deployed = self.packages.deploy_ready(profile, Path(self.settings.game_path)) if profile else []
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Deployed {len(deployed)} package(s)")
                self._last_save_message = f"Deployed {len(deployed)} package(s) to the game mods folder"
            except (OSError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Property("QStringList", notify=stateChanged)
    def diagnosticOptions(self):
        if not self.troubleshooter:
            return []
        return [f"{item.severity.upper()} · {item.title} · {item.message}" for item in self.troubleshooter.scan()]

    @Slot()
    def runDiagnostics(self):
        if self.troubleshooter:
            operation = self.operations.start("troubleshooter-scan", profile_id=self._selected_profile_id) if self.operations else None
            try:
                findings = self.troubleshooter.scan()
                attention = sum(1 for item in findings if item.severity == "attention")
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Diagnostics completed: {attention} attention finding(s)")
                if self.logs:
                    self.logs.info("Troubleshooter scan completed", operation_id=operation.id if operation else None,
                                    profile_id=self._selected_profile_id, details={"attention": attention})
                self._last_save_message = f"Read-only health scan completed: {attention} attention finding(s)"
            except (OSError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Property("QStringList", notify=stateChanged)
    def settingOptions(self):
        if not self.game_settings:
            return []
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            return []
        values = self.game_settings.values(profile)
        return [f"{definition.name} · {values[definition.key]}" for definition in self.game_settings.definitions()]

    @Property("QStringList", notify=stateChanged)
    def researchOptions(self):
        if not self.research:
            return []
        return [f"{item.status.upper()} · {item.title} · {len(item.evidence)} evidence note(s)"
                for item in self.research.list() if item.profile_id == self._selected_profile_id]

    @Property("QStringList", notify=stateChanged)
    def knowledgeOptions(self):
        if not self.knowledge:
            return []
        return [f"{entry.category} · {entry.title} — {entry.summary}" for entry in self.knowledge.search(self._knowledge_query)]

    @Slot(str)
    def searchKnowledge(self, query: str):
        self._knowledge_query = query
        self.stateChanged.emit()

    @Slot()
    def exportCatalog(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            selected, _ = QFileDialog.getSaveFileName(None, "Export Ember Vault catalog", "embervault-catalog.json", "JSON (*.json)")
        except ImportError:
            selected = ""
        if selected and self.catalog:
            operation = self.operations.start("catalog-export") if self.operations else None
            try:
                destination = self.catalog.export(Path(selected))
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Exported catalog to {destination}")
                self._last_save_message = f"Catalog exported to {destination}"
            except OSError as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
            self.stateChanged.emit()

    @Property("QStringList", notify=stateChanged)
    def contentOptions(self):
        if not self.content:
            return []
        return [
            f"{item.status.upper()} · {item.name} · {item.profile_id}"
            + (f" · {item.description}" if item.description else "")
            for item in self.content.list() if item.profile_id == self._selected_profile_id
        ]

    @Slot(str, str)
    def createContentProject(self, name: str, description: str = ""):
        if not self.content:
            return
        operation = self.operations.start("content-project-create", profile_id=self._selected_profile_id) if self.operations else None
        try:
            project = self.content.create(name, self._selected_profile_id, description)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Created content project {project.id}")
            self._last_save_message = f"Created content project {project.id}"
        except (OSError, ValueError) as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(str)
    def setLatestContentStatus(self, status: str):
        if not self.content:
            return
        projects = [item for item in self.content.list() if item.profile_id == self._selected_profile_id]
        if not projects:
            self._last_save_message = "Create a content project first"
        else:
            operation = self.operations.start("content-project-status", profile_id=self._selected_profile_id) if self.operations else None
            try:
                project = self.content.set_status(projects[-1].id, status)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Content project status {project.status}")
                self._last_save_message = f"Content project is {project.status}"
            except (KeyError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def exportLatestContentProject(self):
        if not self.content:
            return
        projects = [item for item in self.content.list() if item.profile_id == self._selected_profile_id]
        if not projects:
            self._last_save_message = "Create a content project first"
        else:
            project = projects[-1]
            operation = self.operations.start("content-project-export", profile_id=project.profile_id) if self.operations else None
            try:
                destination = self.content.export(project)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Exported content project {project.id}")
                self._last_save_message = f"Exported design manifest to {destination}"
            except OSError as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Property("QStringList", notify=stateChanged)
    def characterOptions(self):
        if not self.characters:
            return []
        return [f"{item.name} · level {item.planned_level} · {item.profile_id}"
                + (f" · {item.notes}" if item.notes else "")
                for item in self.characters.list() if item.profile_id == self._selected_profile_id]

    @Property("QStringList", notify=stateChanged)
    def riskOptions(self):
        if not self.risk:
            return []
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            return []
        return [
            f"{capability}: {'ready' if self.risk.evaluate(capability, profile).allowed else 'gated'}"
            for capability in ("trainer", "research", "content-creator")
        ]

    def _launchGuardedModule(self, module_id: str, capability: str):
        if not self.launcher:
            return
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            self._last_save_message = "Select a profile first"
            self.stateChanged.emit()
            return
        operation = self.operations.start(f"module-launch-{capability}", profile_id=profile.id) if self.operations else None
        backup_id = self._selected_backup_id or None
        try:
            process = self.launcher.launch(
                module_id, capability,
                profile,
                LaunchContext(
                    profile.id, self.settings.game_path or None, operation.id if operation else None,
                    backup_id
                ),
                backup_id,
            )
            output, _ = process.communicate(timeout=15)
            if process.returncode != 0:
                raise RuntimeError(f"Module exited with code {process.returncode}")
            result = output.strip() if output else "no worker output"
            if len(result.encode("utf-8")) > MAX_WORKER_OUTPUT:
                raise RuntimeError("Worker returned too much output")
            try:
                worker_result = json.loads(result)
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise RuntimeError("Worker returned invalid JSON") from exc
            if (not isinstance(worker_result, dict)
                    or worker_result.get("contract_version") != 1
                    or worker_result.get("read_only") is not True
                    or worker_result.get("status") != "ready"
                    or not isinstance(worker_result.get("game_path"), str)
                    or not isinstance(worker_result.get("operation"), str)
                    or (module_id == "embervault.research" and
                        (not isinstance(worker_result.get("evidence"), list) or
                         any(not isinstance(item, str) or not item.strip()
                             for item in worker_result.get("evidence", []))))
                    or (module_id == "embervault.trainer" and
                        (not isinstance(worker_result.get("checks"), list) or
                         any(not isinstance(item, str) or not item.strip()
                             for item in worker_result.get("checks", []))))
                    or (module_id == "embervault.content-creator" and
                        (not isinstance(worker_result.get("checks"), list) or
                         any(not isinstance(item, str) or not item.strip()
                             for item in worker_result.get("checks", []))))
                    or worker_result.get("profile") != profile.id
                    or (operation and worker_result.get("operation") != operation.id)):
                raise RuntimeError("Worker returned an invalid or non-read-only contract")
            if module_id == "embervault.research" and self.research:
                records = [item for item in self.research.list()
                           if item.profile_id == profile.id]
                if records:
                    record = records[-1]
                    for observation in worker_result["evidence"]:
                        self.research.add_evidence(record.id, f"worker observation: {observation}")
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Launched {module_id}: {result}")
            if self.logs:
                self.logs.info("Guarded module completed", operation_id=operation.id if operation else None,
                                profile_id=profile.id, details={"module_id": module_id, "output": result})
            if module_id == "embervault.research":
                evidence_count = len(worker_result.get("evidence", []))
                self._last_save_message = (
                    f"Completed guarded {capability} worker: research evidence probe "
                    f"({evidence_count} observations) · {worker_result.get('game_path', '')}"
                )
            elif module_id == "embervault.trainer":
                self._last_save_message = (
                    f"Completed guarded {capability} readiness audit "
                    f"({len(worker_result.get('checks', []))} checks)"
                )
            elif module_id == "embervault.content-creator":
                self._last_save_message = (
                    f"Completed guarded {capability} design audit "
                    f"({len(worker_result.get('checks', []))} checks)"
                )
            else:
                self._last_save_message = f"Completed guarded {capability} worker: {result}"
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            message = "Guarded module timed out and was terminated"
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, message)
            if self.logs:
                self.logs.error(message, operation_id=operation.id if operation else None,
                                 profile_id=profile.id, details={"module_id": module_id})
            self._last_save_message = message
        except (PermissionError, KeyError, OSError, RuntimeError, ValueError) as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            if self.logs:
                self.logs.error("Guarded module failed", operation_id=operation.id if operation else None,
                                 profile_id=profile.id, details={"module_id": module_id, "error": str(exc)})
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def launchTrainer(self):
        self._launchGuardedModule("embervault.trainer", "trainer")

    @Slot()
    def launchResearchWorker(self):
        self._launchGuardedModule("embervault.research", "research")

    @Slot()
    def launchContentWorker(self):
        self._launchGuardedModule("embervault.content-creator", "content-creator")

    @Slot(str, str)
    def createCharacter(self, name: str, notes: str = ""):
        if not self.characters:
            return
        operation = self.operations.start("character-project-create", profile_id=self._selected_profile_id) if self.operations else None
        try:
            record = self.characters.create(name, self._selected_profile_id, notes)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Created character project {record.id}")
            self._last_save_message = f"Created character project {record.id}"
        except (OSError, ValueError) as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(int)
    def stageLatestCharacterLevel(self, level: int):
        if not self.characters:
            return
        records = [item for item in self.characters.list() if item.profile_id == self._selected_profile_id]
        if not records:
            self._last_save_message = "Create a character project first"
        else:
            operation = self.operations.start("character-level-stage", profile_id=self._selected_profile_id) if self.operations else None
            try:
                record = self.characters.stage_level(records[-1].id, level)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Staged level {record.planned_level} for {record.id}")
                self._last_save_message = f"Staged level {record.planned_level} for {record.name}"
            except (KeyError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def exportLatestCharacterPlan(self):
        if not self.characters:
            return
        records = [item for item in self.characters.list() if item.profile_id == self._selected_profile_id]
        if not records:
            self._last_save_message = "Create a character project first"
        else:
            record = records[-1]
            operation = self.operations.start("character-plan-export", profile_id=record.profile_id) if self.operations else None
            try:
                destination = self.characters.export(record)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Exported character plan {record.id}")
                self._last_save_message = f"Exported character plan to {destination}"
            except OSError as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(str, str)
    def createResearchRecord(self, title: str, hypothesis: str):
        if not self.research:
            return
        operation = self.operations.start("research-create", profile_id=self._selected_profile_id) if self.operations else None
        try:
            record = self.research.create(title, hypothesis, self._selected_profile_id)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Created research record {record.id}")
            self._last_save_message = f"Created research record {record.id}"
        except (OSError, ValueError) as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(str)
    def addResearchEvidence(self, note: str):
        if not self.research:
            return
        records = [item for item in self.research.list() if item.profile_id == self._selected_profile_id]
        if not records:
            self._last_save_message = "Create a research record first"
        else:
            operation = self.operations.start("research-evidence", profile_id=self._selected_profile_id) if self.operations else None
            try:
                record = self.research.add_evidence(records[-1].id, note)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Added evidence to {record.id}")
                self._last_save_message = f"Added evidence to {record.id}"
            except (KeyError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(str)
    def setLatestResearchStatus(self, status: str):
        if not self.research:
            return
        records = [item for item in self.research.list() if item.profile_id == self._selected_profile_id]
        if not records:
            self._last_save_message = "Create a research record first"
        else:
            operation = self.operations.start("research-status", profile_id=self._selected_profile_id) if self.operations else None
            try:
                record = self.research.set_status(records[-1].id, status)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Research status {record.status}")
                self._last_save_message = f"Research record is {record.status}"
            except (KeyError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def publishLatestResearch(self):
        if not self.research:
            return
        records = [item for item in self.research.list() if item.profile_id == self._selected_profile_id]
        if not records:
            self._last_save_message = "Create a research record first"
        else:
            operation = self.operations.start("research-publish", profile_id=self._selected_profile_id) if self.operations else None
            try:
                record = self.research.publish(records[-1].id)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Published research {record.id}")
                self._last_save_message = f"Published research record {record.id}"
            except (KeyError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def unpublishLatestResearch(self):
        if not self.research:
            return
        records = [item for item in self.research.list() if item.profile_id == self._selected_profile_id]
        if not records:
            self._last_save_message = "Create a research record first"
        else:
            operation = self.operations.start("research-unpublish", profile_id=self._selected_profile_id) if self.operations else None
            try:
                record = self.research.unpublish(records[-1].id)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Unpublished research {record.id}")
                self._last_save_message = f"Unpublished research record {record.id}"
            except KeyError as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(int)
    def stageSetting(self, index: int):
        if not self.game_settings:
            return
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        definitions = self.game_settings.definitions()
        if not profile or not 0 <= index < len(definitions):
            return
        definition = definitions[index]
        values = self.game_settings.values(profile)
        current = values[definition.key]
        if definition.value_type == "boolean":
            value = not current
        else:
            value = float(current) + 0.25
            if value > 4.0:
                value = 0.25
        operation = self.operations.start("game-setting-stage", profile_id=profile.id) if self.operations else None
        try:
            updated = self.game_settings.stage(profile, definition.key, value)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Staged {definition.key}")
            self.profiles = [updated if item.id == updated.id else item for item in self.profiles]
            self._last_save_message = f"Staged {definition.name} for {updated.name}"
        except ValueError as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def resetGameSettings(self):
        if not self.game_settings:
            return
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            return
        operation = self.operations.start("game-settings-reset", profile_id=profile.id) if self.operations else None
        updated = self.game_settings.reset(profile)
        if operation and self.operations:
            self.operations.finish(operation, OperationStatus.SUCCEEDED, "Reset game settings")
        self.profiles = [updated if item.id == updated.id else item for item in self.profiles]
        self._last_save_message = f"Reset game settings for {updated.name}"
        self.stateChanged.emit()

    @Slot()
    def exportGameSettings(self):
        if not self.game_settings:
            return
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            return
        operation = self.operations.start("game-settings-export", profile_id=profile.id) if self.operations else None
        try:
            destination = self.game_settings.export(profile)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Exported settings to {destination.name}")
            self._last_save_message = f"Exported staged settings to {destination}"
        except OSError as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Property("QStringList", notify=stateChanged)
    def profileDetails(self):
        return [
            f"{profile.name} · {profile.profile_type} · {profile.description}"
            for profile in self.profiles
        ]

    @Slot()
    def refresh(self):
        if self.settings.game_path:
            installation = self.detector.detect(Path(self.settings.game_path))
            issues = self.detector.validate(installation)
            self._game_status = "Ready" if not issues else "Needs attention"
            self._build = installation.build_id or "Build unknown"
        else:
            self._game_status = "Not configured"
            self._build = "Choose game folder"
        if self.stateChanged is not None:
            self.stateChanged.emit()

    @Slot()
    def chooseGameFolder(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            selected = QFileDialog.getExistingDirectory(None, "Choose Enshrouded installation folder")
        except ImportError:
            selected = ""
        if selected:
            self.settings.game_path = selected
            self.settings_service.save(self.settings)
            self._last_save_message = f"Game folder set to {selected}"
            self.refresh()

    @Slot(result=str)
    def saveManagerSummary(self):
        return self.saveSummary

    @Slot(int)
    def selectProfile(self, index: int):
        if 0 <= index < len(self.profiles):
            self._selected_profile_id = self.profiles[index].id
            self._profile_name = self.profiles[index].name
            self.stateChanged.emit()

    @Slot(str)
    def createProfile(self, name: str):
        operation = self.operations.start("profile-create") if self.operations else None
        try:
            profile = self.profile_service.create_custom(name)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Created profile {profile.id}",)
            self.profiles.append(profile)
            self._selected_profile_id = profile.id
            self._profile_name = profile.name
            self._last_save_message = f"Created profile {profile.name}"
        except ValueError as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def deleteActiveProfile(self):
        if self._selected_profile_id in {"default", "research"}:
            self._last_save_message = "Built-in profiles cannot be deleted"
        else:
            operation = self.operations.start("profile-delete", profile_id=self._selected_profile_id) if self.operations else None
            try:
                deleted = self._selected_profile_id
                owned_records = (
                    [item for item in self.research.list() if item.profile_id == deleted] if self.research else []
                ) + (
                    [item for item in self.content.list() if item.profile_id == deleted] if self.content else []
                ) + (
                    [item for item in self.characters.list() if item.profile_id == deleted] if self.characters else []
                )
                if owned_records:
                    raise ValueError("Profile owns project records; remove or migrate them before deletion")
                self.profile_service.delete_custom(deleted)
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, f"Deleted profile {deleted}")
                self.profiles = [item for item in self.profiles if item.id != deleted]
                fallback = next((item for item in self.profiles if item.id == "default"), self.profiles[0])
                self._selected_profile_id = fallback.id
                self._profile_name = fallback.name
                self._last_save_message = f"Deleted profile {deleted}"
            except ValueError as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(int)
    def togglePackage(self, index: int):
        if not getattr(self, "packages", None):
            return
        available = self.packages.list()
        if not 0 <= index < len(available):
            return
        selected = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not selected:
            return
        package = available[index]
        enabled = not self.packages.is_enabled(selected, package.id)
        operation = self.operations.start("package-enable" if enabled else "package-disable", profile_id=selected.id, package_id=package.id) if self.operations else None
        try:
            detected_build = self._build if self._build not in {"Unknown build", "Choose game folder"} else None
            updated = self.packages.set_enabled(selected, package.id, enabled, detected_build)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, "Package state updated")
            self.profiles = [updated if item.id == updated.id else item for item in self.profiles]
            self._last_save_message = f"{'Enabled' if enabled else 'Disabled'} {package.name} for {updated.name}"
        except (OSError, ValueError) as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def importPackage(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            selected = QFileDialog.getExistingDirectory(None, "Choose package folder")
            if not selected:
                selected, _ = QFileDialog.getOpenFileName(
                    None, "Choose package ZIP", "", "Packages (*.zip)"
                )
        except ImportError:
            selected = ""
        if selected and self.packages:
            try:
                operation = self.operations.start("package-import") if self.operations else None
                package = self.packages.install_from_archive(Path(selected)) if selected.lower().endswith(".zip") else self.packages.install_from_directory(Path(selected))
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.SUCCEEDED, "Package imported")
                self._last_save_message = f"Imported {package.name}"
            except (OSError, ValueError) as exc:
                if operation and self.operations:
                    self.operations.finish(operation, OperationStatus.FAILED, str(exc))
                if self.logs:
                    self.logs.error("Troubleshooter scan failed", operation_id=operation.id if operation else None,
                                    profile_id=self._selected_profile_id, details={"error": str(exc)})
                self._last_save_message = str(exc)
            self.stateChanged.emit()

    @Slot(int)
    def removePackage(self, index: int):
        if not self.packages:
            return
        available = self.packages.list()
        if not 0 <= index < len(available):
            return
        package = available[index]
        operation = self.operations.start("package-remove", package_id=package.id) if self.operations else None
        try:
            self.packages.remove(package.id)
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, "Package removed")
            self._last_save_message = f"Removed {package.name}"
        except (OSError, ValueError) as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(int)
    def undeployPackage(self, index: int):
        if not self.packages or not self.settings.game_path:
            self._last_save_message = "Choose a game folder before undeploying packages"
            self.stateChanged.emit()
            return
        available = self.packages.list()
        if not 0 <= index < len(available):
            return
        package = available[index]
        operation = self.operations.start("package-undeploy", profile_id=self._selected_profile_id,
                                          package_id=package.id) if self.operations else None
        try:
            self.packages.undeploy(package.id, Path(self.settings.game_path))
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.SUCCEEDED, "Package undeployed")
            self._last_save_message = f"Undeployed {package.name}"
        except (OSError, ValueError) as exc:
            if operation and self.operations:
                self.operations.finish(operation, OperationStatus.FAILED, str(exc))
            self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(int)
    def selectBackup(self, index: int):
        backups = self.save_manager.list_backups()
        self._selected_backup_id = backups[index].id if 0 <= index < len(backups) else ""
        self._restore_preview = "Backup selected" if self._selected_backup_id else "No restore selected"
        self.stateChanged.emit()

    @Slot()
    def previewRestore(self):
        if not self._selected_backup_id or not self._save_directory:
            self._restore_preview = "Choose a save folder and backup first"
        else:
            try:
                if self.save_workflow:
                    result = self.save_workflow.preview_restore(
                        self._selected_backup_id, Path(self._save_directory), self._selected_profile_id
                    )
                    plan = result.payload
                else:
                    plan = self.save_manager.preview_restore(self._selected_backup_id, Path(self._save_directory))
                self._restore_preview = f"{len(plan['files_to_add_or_replace'])} files will be restored; current state will be backed up first"
            except SaveManagerError as exc:
                self._restore_preview = str(exc)
        self.stateChanged.emit()

    @Slot()
    def verifySelected(self):
        if not self._selected_backup_id:
            self._last_save_message = "Choose a backup first"
        else:
            try:
                if self.save_workflow:
                    self.save_workflow.verify(self._selected_backup_id, self._selected_profile_id)
                elif not self.save_manager.verify_backup(self._selected_backup_id):
                    raise SaveManagerError("Backup verification failed")
                self._last_save_message = f"Verified {self._selected_backup_id}"
            except (OSError, SaveManagerError, ValueError) as exc:
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def restoreSelected(self):
        if not self._selected_backup_id or not self._save_directory:
            self._last_save_message = "Choose a save folder and backup first"
        else:
            try:
                if self.save_workflow:
                    result = self.save_workflow.restore(
                        self._selected_backup_id, Path(self._save_directory), self._selected_profile_id
                    )
                    current = result.snapshot
                    operation_id = result.operation.id
                else:
                    current = self.save_manager.backup(Path(self._save_directory), "automatic-before-restore")
                    self.save_manager.restore(self._selected_backup_id, Path(self._save_directory), current_backup=current)
                    operation_id = "legacy"
                self._last_save_message = f"Restored and verified {self._selected_backup_id} ({operation_id})"
                self._safety = f"Current state preserved as {current.id}"
            except (OSError, SaveManagerError) as exc:
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot()
    def chooseSaveFolder(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            selected = QFileDialog.getExistingDirectory(None, "Choose Enshrouded save folder")
        except ImportError:
            selected = ""
        if selected:
            self._save_directory = selected
            self._last_save_message = f"Selected {selected}"
            self.stateChanged.emit()

    @Slot()
    def inspectSaves(self):
        if not self._save_directory:
            self._last_save_message = "Choose a save folder first"
        else:
            try:
                if self.save_workflow:
                    result = self.save_workflow.inspect(Path(self._save_directory), self._selected_profile_id)
                    files = result.payload["files"]
                else:
                    files = self.save_manager.inspect(Path(self._save_directory))
                self._last_save_message = f"Inspected {len(files)} file{'s' if len(files) != 1 else ''}"
            except SaveManagerError as exc:
                self._last_save_message = str(exc)
        self.stateChanged.emit()

    @Slot(str)
    def createBackup(self, label: str):
        if not self._save_directory:
            self._last_save_message = "Choose a save folder first"
        else:
            try:
                if self.save_workflow:
                    result = self.save_workflow.backup(Path(self._save_directory), label, self._selected_profile_id)
                    snapshot = result.snapshot
                else:
                    snapshot = self.save_manager.backup(Path(self._save_directory), label)
                self._last_save_message = f"Verified {snapshot.id}"
                self._safety = "Backup verified"
            except (OSError, SaveManagerError) as exc:
                self._last_save_message = str(exc)
        self.stateChanged.emit()
