"""Qt-facing adapter for the first Control Center vertical slice."""
from __future__ import annotations

from pathlib import Path

from core.application import EmbervaultRuntime
from core.game_detection import GameDetector
from core.profiles import ProfileService
from core.save_manager import SaveManagerError, SaveManagerService
from core.save_workflow import SaveWorkflowService
from core.settings import SettingsService

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
        self.modules = runtime.modules if runtime else None
        self.packages = runtime.packages if runtime else None
        self.troubleshooter = runtime.troubleshooter if runtime else None
        self.game_settings = runtime.game_settings if runtime else None
        self.research = runtime.research if runtime else None
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
        return [f"{module.name} · {module.feature_state}" for module in self.modules.discover().values()]

    @Property("QStringList", notify=stateChanged)
    def packageOptions(self):
        if not getattr(self, "packages", None):
            return []
        profile = next((item for item in self.profiles if item.id == self._selected_profile_id), None)
        if not profile:
            return []
        return [
            f"{'Enabled' if self.packages.is_enabled(profile, package.id) else 'Disabled'} · {package.name} · {package.version}"
            for package in self.packages.list()
        ]

    @Property("QStringList", notify=stateChanged)
    def diagnosticOptions(self):
        if not self.troubleshooter:
            return []
        return [f"{item.severity.upper()} · {item.title} · {item.message}" for item in self.troubleshooter.scan()]

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
        return [f"{item.status.upper()} · {item.title} · {len(item.evidence)} evidence note(s)" for item in self.research.list()]

    @Slot(str, str)
    def createResearchRecord(self, title: str, hypothesis: str):
        if not self.research:
            return
        try:
            record = self.research.create(title, hypothesis, self._selected_profile_id)
            self._last_save_message = f"Created research record {record.id}"
        except ValueError as exc:
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
        updated = self.game_settings.stage(profile, definition.key, value)
        self.profiles = [updated if item.id == updated.id else item for item in self.profiles]
        self._last_save_message = f"Staged {definition.name} for {updated.name}"
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

    @Slot(result=str)
    def saveManagerSummary(self):
        return self.saveSummary

    @Slot(int)
    def selectProfile(self, index: int):
        if 0 <= index < len(self.profiles):
            self._selected_profile_id = self.profiles[index].id
            self._profile_name = self.profiles[index].name
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
        updated = self.packages.set_enabled(selected, package.id, not self.packages.is_enabled(selected, package.id))
        self.profiles = [updated if item.id == updated.id else item for item in self.profiles]
        self._last_save_message = f"{'Enabled' if package.id in updated.enabled_packages else 'Disabled'} {package.name} for {updated.name}"
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
