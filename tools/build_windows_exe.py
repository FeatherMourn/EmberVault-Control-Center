"""Build a portable Windows desktop bundle for EmberVault Control Center."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


DATA_DIRS = (
    "ui",
    "contracts",
    "knowledge",
    "modules",
    "adapters",
    "packages",
    "templates",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--console", action="store_true", help="Keep a console for troubleshooting output")
    args = parser.parse_args()
    destination = args.destination.resolve()
    work = ROOT / ".release-check" / "pyinstaller"
    if work.exists():
        shutil.rmtree(work)
    destination.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        "EmberVaultControlCenter",
        "--console" if args.console else "--windowed",
        "--onedir",
        "--distpath",
        str(destination),
        "--workpath",
        str(work / "work"),
        "--specpath",
        str(work),
    ]
    for data_dir in DATA_DIRS:
        command.extend(("--add-data", f"{ROOT / data_dir}{';'}{data_dir}"))
    for hidden_import in ("PySide6.QtCore", "PySide6.QtGui", "PySide6.QtQml", "PySide6.QtWidgets"):
        command.extend(("--hidden-import", hidden_import))
    for package in ("PySide6", "shiboken6"):
        command.extend(("--collect-all", package))
    command.extend(("--runtime-hook", str(ROOT / "tools" / "pyinstaller_qt_hook.py")))
    command.append(str(ROOT / "tools" / "windows_entry.py"))
    subprocess.run(command, cwd=ROOT, check=True)
    exe = destination / "EmberVaultControlCenter" / "EmberVaultControlCenter.exe"
    if not exe.is_file():
        raise SystemExit(f"PyInstaller did not create {exe}")
    print(exe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
