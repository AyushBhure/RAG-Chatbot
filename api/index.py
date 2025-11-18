"""Vercel serverless entrypoint for the FastAPI app."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

from app.main import app  # noqa: E402

handler = app

