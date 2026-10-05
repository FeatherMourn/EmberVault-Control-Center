"""Standalone Content Creator application entry point."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtQml import QQmlApplicationEngine

from core.application import EmbervaultRuntime
from control_center.backend import ControlCenterBackend


def main() -> int:
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    runtime = EmbervaultRuntime.create(ROOT / "runtime-data")
    backend = ControlCenterBackend(runtime.root, runtime=runtime)
    requested_profile = next((arg.split("=", 1)[1] for arg in sys.argv
                              if arg.startswith("--profile=") and "=" in arg), "")
    if requested_profile:
        for index, profile in enumerate(backend.profiles):
            if profile.id == requested_profile:
                backend.selectProfile(index)
                break
    backend.refresh()
    engine.rootContext().setContextProperty("controlCenter", backend)
    engine.load(str(ROOT / "ui" / "ContentCreator.qml"))
    if not engine.rootObjects():
        return 1
    if "--smoke-test" in sys.argv:
        QTimer.singleShot(250, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
