"""Non-mutating process-contract stub for future content creation workers."""
from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="")
    parser.add_argument("--game-path", default="")
    parser.add_argument("--operation", default="")
    args = parser.parse_args()
    print(json.dumps({"contract_version": 1, "status": "ready", "read_only": True,
                      "profile": args.profile, "game_path": args.game_path, "operation": args.operation}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
