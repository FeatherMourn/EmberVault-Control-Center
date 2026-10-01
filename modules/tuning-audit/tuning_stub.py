"""Read-only audit for staged gameplay settings.

This worker verifies only the execution context. It intentionally does not
apply, inject, or rewrite any game configuration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="")
    parser.add_argument("--game-path", default="")
    parser.add_argument("--operation", default="")
    args = parser.parse_args()
    game = Path(args.game_path) if args.game_path else None
    checks = [
        f"profile_selected: {bool(args.profile)}",
        f"game_path_configured: {bool(args.game_path)}",
        f"game_path_exists: {game.exists() if game else False}",
        "settings_source: staged-profile-values",
        "live_game_settings_changed: False",
    ]
    print(json.dumps({
        "contract_version": 1,
        "status": "ready",
        "read_only": True,
        "profile": args.profile,
        "game_path": args.game_path,
        "operation": args.operation,
        "checks": checks,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
