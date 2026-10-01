"""Qt-facing adapter for the first Control Center vertical slice."""
from __future__ import annotations

from pathlib import Path

from core.game_detection import GameDetector
from core.profiles import ProfileService
from core.save_manager import SaveManagerError, SaveManagerService
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

    def __init__(self, data_root: Path, parent=None):
        super().__init__(parent) if QObject is not object else super().__init__()
        self.data_root = Path(data_root)
        self.settings_service = SettingsService(self.data_root)
        self.settings = self.settings_service.load()
        self.profile_service = ProfileService(self.data_root)
        self.profiles = self.profile_service.ensure_defaults()
        self.save_manager = SaveManagerService(self.data_root)
        self.detector = GameDetector()
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
                current = self.save_manager.backup(Path(self._save_directory), "automatic-before-restore")
                self.save_manager.restore(self._selected_backup_id, Path(self._save_directory), current_backup=current)
                self._last_save_message = f"Restored and verified {self._selected_backup_id}"
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
                snapshot = self.save_manager.backup(Path(self._save_directory), label)
                self._last_save_message = f"Verified {snapshot.id}"
                self._safety = "Backup verified"
            except (OSError, SaveManagerError) as exc:
                self._last_save_message = str(exc)
        self.stateChanged.emit()
