"""Entry point for generating Pen2Pixel dataset manifests and quality report."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "handwriting-recognition"))

from dataset.pipeline import build  # noqa: E402

if __name__ == "__main__":
    result = build()
    for key, value in result.items():
        print(f"{key}: {value}")
