"""Non-mutating Content Creator design-workspace audit."""
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
    parser.add_argument("--backup", default="")
    parser.add_argument("--project", default="")
    args = parser.parse_args()
    checks = [f"profile_selected: {bool(args.profile)}",
              "design_workspace_only: True",
              "live_game_content_touched: False",
              f"recovery_context_available: {bool(args.backup)}"]
    project_state = "not_supplied"
    project_path = args.project or (args.game_path if Path(args.game_path).is_file() else "")
    if project_path:
        try:
            project = json.loads(open(project_path, encoding="utf-8").read())
            required = {"schema_version", "schema_id", "application_state", "evidence_summary", "live_game_files_touched"}
            missing = sorted(required - project.keys())
            if missing or project.get("schema_version") != 1 or project.get("application_state") != "design-only" or project.get("live_game_files_touched") is not False:
                project_state = "blocked"
                checks.append("project_export_contract: invalid")
            else:
                project_state = "validated"
                checks.append("project_export_contract: valid")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            project_state = "blocked"
            checks.append("project_export_contract: unreadable")
    result = ModuleResult("ready", "Content Creator prepared a design-only workspace audit.", {
        "profile_id": args.profile,
        "operation_id": args.operation,
        "application_state": "design-only",
        "mutates_workspace": False,
        "project_state": project_state,
        "evidence": [{"id": "content-creator-session", "kind": "runtime", "state": "observed", "summary": item} for item in checks],
        "recovery": {"expectation": "Design-only content workflow", "rollback": "Discard the exported design package", "verification": "Confirm no live game content changed", "backup_required": bool(args.backup)},
    })
    payload = result.to_dict()
    payload.update({"read_only": True, "profile": args.profile, "game_path": args.game_path, "operation": args.operation,
                    "checks": checks, "project_state": project_state})
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
