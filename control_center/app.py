"""Qt Quick application entry point."""
from __future__ import annotations

import sys
from pathlib import Path
from core.application import EmbervaultRuntime
from .backend import ControlCenterBackend


def _application_root() -> Path:
    """Return the source, installed-data, or frozen bundle root."""
    bundled = getattr(sys, "_MEIPASS", None)
    if bundled:
        return Path(bundled)
    package_root = Path(__file__).resolve().parents[1]
    if (package_root / "ui" / "Main.qml").is_file():
        return package_root
    prefix_root = Path(sys.prefix)
    if (prefix_root / "ui" / "Main.qml").is_file():
        return prefix_root
    return package_root


ROOT = _application_root()


def _ui_path() -> Path:
    local = ROOT / "ui" / "Main.qml"
    if local.is_file():
        return local
    return ROOT / "ui" / "Main.qml"


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        from PySide6.QtQml import QQmlApplicationEngine
    except ImportError as exc:
        print(f"PySide6 is required to launch EmberVault Control Center: {exc}", file=sys.stderr)
        return 2

    standalone_content_creator = "--content-creator" in sys.argv
    requested_profile = next((arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--profile=") and "=" in arg), "")
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    runtime = EmbervaultRuntime.create(ROOT / "runtime-data")
    backend = ControlCenterBackend(runtime.root, runtime=runtime)
    if requested_profile:
        for index, profile in enumerate(backend.profiles):
            if profile.id == requested_profile:
                backend.selectProfile(index)
                break
    backend.refresh()
    if "--smoke-test" in sys.argv:
        health = runtime.health()
        if health.get("modules", 0) < 5 or health.get("knowledge", 0) < 8:
            print(f"Packaged seed inventory is incomplete: {health}", file=sys.stderr)
            return 1
    engine.rootContext().setContextProperty("controlCenter", backend)
    engine.rootContext().setContextProperty("standaloneContentCreator", standalone_content_creator)
    engine.load(str(_ui_path()))
    if not engine.rootObjects():
        return 1
    if "--smoke-test" in sys.argv:
        # Give QML one event-loop turn to finish bindings before exiting.
        QTimer.singleShot(250, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
