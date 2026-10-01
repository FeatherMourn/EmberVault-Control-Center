"""Qt Quick application entry point."""
from __future__ import annotations

import sys
from pathlib import Path
from core.application import EmbervaultRuntime
from .backend import ControlCenterBackend


ROOT = Path(__file__).resolve().parents[1]


def _ui_path() -> Path:
    local = ROOT / "ui" / "Main.qml"
    if local.is_file():
        return local
    return Path(sys.prefix) / "ui" / "Main.qml"


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        from PySide6.QtQml import QQmlApplicationEngine
    except ImportError:
        print("PySide6 is required to launch Embervault Control Center. Install project dependencies first.", file=sys.stderr)
        return 2

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    runtime = EmbervaultRuntime.create(ROOT / "runtime-data")
    backend = ControlCenterBackend(runtime.root, runtime=runtime)
    backend.refresh()
    engine.rootContext().setContextProperty("controlCenter", backend)
    engine.load(str(_ui_path()))
    if not engine.rootObjects():
        return 1
    if "--smoke-test" in sys.argv:
        # Give QML one event-loop turn to finish bindings before exiting.
        QTimer.singleShot(250, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
