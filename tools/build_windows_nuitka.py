"""Build the Windows Control Center with Qt-aware Nuitka deployment."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIRS = (
    "ui", "contracts", "knowledge", "modules", "adapters", "packages",
    "templates", "backups", "profiles", "research", "characters",
    "content-projects", "trainer", "promotion", "community", "distribution",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--console", action="store_true", help="Keep a console for troubleshooting")
    args = parser.parse_args()
    command = [
        sys.executable, "-m", "nuitka", "--update-check=never", "--standalone", "--follow-imports",
        "--enable-plugin=pyside6", "--include-qt-plugins=qml",
        f"--output-dir={args.destination}", "--output-filename=EmberVaultControlCenter.exe",
        "--assume-yes-for-downloads",
    ]
    if not args.console:
        command.append("--windows-disable-console")
    for data_dir in DATA_DIRS:
        dir_path = ROOT / data_dir
        if dir_path.exists():
            command.append(f"--include-data-dir={dir_path}={data_dir}")
    command.append(str(ROOT / "tools" / "windows_entry.py"))
    subprocess.run(command, cwd=ROOT, check=True)
    print(args.destination / "windows_entry.dist" / "EmberVaultControlCenter.exe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
