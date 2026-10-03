"""Entry point for the future out-of-process replacement worker.

It currently validates an approved plan and prints the guarded sequence. File
replacement remains disabled until the launcher and rollback integration are
completed and acceptance-tested.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.updater import ExternalUpdaterService


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    if plan.get("status") != "approved":
        raise SystemExit("Update plan is not approved")
    sequence = {"status": "validated", "sequence": [
        "stop-control-center", "verify-backup", "replace-installation",
        "launch-startup-probe", "rollback-on-failure"
    ], "application_state": "review-only"}
    if not args.execute:
        print(json.dumps(sequence))
        return 0

    target = Path(plan["installation"])
    executable = target / "EmberVaultControlCenter.exe"
    if not executable.is_file():
        raise SystemExit("Packaged Control Center executable is missing")

    def startup_probe(argument: str) -> bool:
        try:
            result = subprocess.run([str(executable), argument], cwd=target, timeout=45,
                                    check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    service = ExternalUpdaterService(Path(plan["installation"]).parent)
    applied = service.apply_approved(Path(args.plan), startup_probe)
    print(json.dumps({"status": "applied" if applied else "rolled-back", "application_state": "completed" if applied else "recovered"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
