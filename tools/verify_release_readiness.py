"""Run the complete local release-readiness gate in one command."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(command: list[str], label: str) -> None:
    print(f"== {label} ==")
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("distribution", type=Path)
    parser.add_argument("--website-catalog", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], "test suite")
    run([sys.executable, "-m", "compileall", "-q", "core", "control_center", "tools"], "compilation")
    run([sys.executable, "tools/verify_release.py", str(args.wheel)], "wheel assets")
    run([sys.executable, "tools/verify_distribution.py", str(args.distribution)], "distribution contents")
    run([sys.executable, "tools/audit_distribution.py", str(args.distribution)], "distribution safety")
    if args.website_catalog:
        run([sys.executable, "tools/verify_catalog.py", str(args.website_catalog)], "public catalog")
    print("Release readiness gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
