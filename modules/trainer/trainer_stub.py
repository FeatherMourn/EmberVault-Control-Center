"""Non-mutating process-contract stub for future Trainer development."""
from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="")
    parser.add_argument("--game-path", default="")
    parser.add_argument("--operation", default="")
    args = parser.parse_args()
    print(json.dumps({"status": "stub-ready", "profile": args.profile, "operation": args.operation}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
