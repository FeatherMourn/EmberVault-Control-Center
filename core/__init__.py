"""Shared Embervault Core services."""

from .compatibility import Compatibility, CompatibilityState
from .game_detection import GameInstallation, GameDetector
from .operations import Operation, OperationService, OperationStatus
from .profiles import Profile, ProfileService
from .settings import Settings, SettingsService

__all__ = [
    "Compatibility", "CompatibilityState", "GameInstallation", "GameDetector",
    "Operation", "OperationService", "OperationStatus", "Profile", "ProfileService",
    "Settings", "SettingsService",
]
