"""Minimal frozen Qt/QML smoke target used before bundling Control Center."""
from pathlib import Path
import sys

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine


def main() -> int:
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    root = Path(__file__).resolve().parent / "qt_minimal_smoke.qml"
    engine.load(QUrl.fromLocalFile(str(root)))
    if not engine.rootObjects():
        return 1
    QTimer.singleShot(250, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
