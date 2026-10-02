"""Make bundled PySide6 Qt DLLs discoverable before Qt modules import."""
from __future__ import annotations

import os
import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    qt_root = Path(sys._MEIPASS) / "PySide6"
    if qt_root.is_dir() and hasattr(os, "add_dll_directory"):
        # Keep the handle alive for the lifetime of the process.
        sys._embervault_qt_dll_directory = os.add_dll_directory(str(qt_root))
