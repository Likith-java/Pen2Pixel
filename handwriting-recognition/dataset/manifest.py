"""Deterministic JSONL manifest generation.

Manifests store paths, labels and metadata only; image bytes are never copied.
No timestamps are written, so identical inputs produce byte-identical files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from dataset.idx import sha256_file

GENERATOR_VERSION = "1.0"


def config_digest(config_path: Path) -> str:
    """Return the SHA-256 digest of the configuration file."""
    return sha256_file(config_path)


def render_manifest(meta: Mapping[str, Any], records: list[dict[str, Any]]) -> str:
    """Render a deterministic manifest as JSONL text."""
    ordered_records = sorted(records, key=lambda record: str(record["id"]))
    lines = [json.dumps({"type": "meta", **dict(sorted(meta.items()))}, sort_keys=True, ensure_ascii=False)]
    lines.extend(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in ordered_records)
    return "\n".join(lines) + "\n"


def write_manifest(path: Path, meta: Mapping[str, Any], records: list[dict[str, Any]]) -> Path:
    """Write a manifest to disk and return its path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_manifest(meta, records), encoding="utf-8")
    return path
