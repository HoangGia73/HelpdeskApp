"""IT Support Tool Suite package metadata."""
from pathlib import Path
import sys


def _read_version():
    """Read the release version in source and PyInstaller environments."""
    if getattr(sys, "frozen", False):
        version_file = Path(sys._MEIPASS) / "VERSION"
    else:
        version_file = Path(__file__).resolve().parents[2] / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return "unknown"


__version__ = _read_version()