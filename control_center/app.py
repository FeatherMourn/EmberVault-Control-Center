"""Qt Quick application entry point."""
from __future__ import annotations

import sys
from pathlib import Path
from .backend import ControlCenterBackend


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
    except ImportError:
        print("PySide6 is required to launch Embervault Control Center. Install project dependencies first.", file=sys.stderr)
        return 2

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = ControlCenterBackend(ROOT / "runtime-data")
    backend.refresh()
    engine.rootContext().setContextProperty("controlCenter", backend)
    engine.load(str(ROOT / "ui" / "Main.qml"))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
