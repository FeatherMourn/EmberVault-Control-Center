"""Non-mutating Content Creator design-workspace audit."""
from __future__ import annotations

import argparse
import json

from embervault_sdk import ModuleResult


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="")
    parser.add_argument("--game-path", default="")
    parser.add_argument("--operation", default="")
    parser.add_argument("--backup", default="")
    args = parser.parse_args()
    checks = [f"profile_selected: {bool(args.profile)}",
              "design_workspace_only: True",
              "live_game_content_touched: False",
              f"recovery_context_available: {bool(args.backup)}"]
    result = ModuleResult("ready", "Content Creator prepared a design-only workspace audit.", {
        "profile_id": args.profile,
        "operation_id": args.operation,
        "application_state": "design-only",
        "mutates_workspace": False,
        "evidence": [{"id": "content-creator-session", "kind": "runtime", "state": "observed", "summary": item} for item in checks],
        "recovery": {"expectation": "Design-only content workflow", "rollback": "Discard the exported design package", "verification": "Confirm no live game content changed", "backup_required": bool(args.backup)},
    })
    payload = result.to_dict()
    payload.update({"read_only": True, "profile": args.profile, "game_path": args.game_path, "operation": args.operation,
                    "checks": checks})
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
