"""PyInstaller entry point that preserves the control_center package context."""
from control_center.app import main


if __name__ == "__main__":
    raise SystemExit(main())
