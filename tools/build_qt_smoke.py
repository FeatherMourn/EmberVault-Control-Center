"""Build the minimal PySide6/QML frozen smoke executable."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--console", action="store_true")
    args = parser.parse_args()
    command = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
        "--console" if args.console else "--windowed", "--name", "EmberVaultQtSmoke", "--distpath", str(args.destination),
        "--add-data", f"{ROOT / 'tools' / 'qt_minimal_smoke.qml'};.",
        "--hidden-import", "PySide6.QtCore", "--hidden-import", "PySide6.QtQml",
        "--hidden-import", "PySide6.QtWidgets", str(ROOT / "tools" / "qt_minimal_smoke.py"),
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    print(args.destination / "EmberVaultQtSmoke" / "EmberVaultQtSmoke.exe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
