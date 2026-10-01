"""Qt-facing adapter for the first Control Center vertical slice."""
from __future__ import annotations

from pathlib import Path

from core.game_detection import GameDetector
from core.profiles import ProfileService
from core.save_manager import SaveManagerService
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
