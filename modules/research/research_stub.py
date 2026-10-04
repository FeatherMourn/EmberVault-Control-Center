"""Read-only research evidence probe.

The worker deliberately reports observations only; it never writes to the game
directory or save data.  More game-specific probes can be added behind this
contract as their safety and evidence requirements become clear.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from embervault_sdk import ModuleResult


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="")
    parser.add_argument("--game-path", default="")
    parser.add_argument("--operation", default="")
    args = parser.parse_args()
    game = Path(args.game_path) if args.game_path else None
    evidence = [
        "probe: research worker completed without writes",
        f"game_path_configured: {bool(args.game_path)}",
    ]
    if game:
        evidence.append(f"game_path_exists: {game.exists()}")
        evidence.append(f"game_path_is_directory: {game.is_dir()}")
    result = ModuleResult("ready", "Research worker prepared a read-only evidence session.", {
        "profile_id": args.profile,
        "operation_id": args.operation,
        "application_state": "read-only",
        "mutates_workspace": False,
        "evidence": [{"id": "research-worker-session", "kind": "runtime", "state": "observed", "summary": item} for item in evidence],
        "recovery": {"expectation": "Read-only research worker", "rollback": "Terminate the worker", "verification": "Confirm no game or save files changed", "backup_required": False},
    })
    payload = result.to_dict()
    payload.update({"read_only": True, "profile": args.profile, "game_path": args.game_path, "operation": args.operation})
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
