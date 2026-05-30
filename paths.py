"""Repository root paths — all durable data lives under ``ROOT``."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SANDBOX = ROOT / "sandbox"
STATE = ROOT / "state"