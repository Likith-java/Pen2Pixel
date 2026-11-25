"""IAM parser tests using synthetic fixtures; no real IAM data is assumed."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from dataset.iam import (
    SplitUnavailableError,
    build_iam_manifests,
    read_official_splits,
)

SPLIT_CFG = {"dir": "split", "train": "train.txt", "val": "val.txt", "test": "test.txt"}
ANNOTATION_CFG = {
    "forms_file": "forms.txt",
    "lines_file": "lines.txt",
    "words_file": "words.txt",
    "writers_file": "writers.txt",
}


def _write_image(path: Path, value: int = 255) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.full((8, 16), value, dtype=np.uint8)).save(path)


def _fixture(tmp_path: Path) -> None:
    lines = ["f01-01-01\t000\tok\tHello world", "f02-01-01\t001\tok\tSecond line", "f03-01-01\t002\tok\tThird line"]
    forms = [
        "f01-01 000 ok 1 f01-01-01",
        "f02-01 001 ok 1 f02-01-01",
        "f03-01 002 ok 1 f03-01-01",
    ]
    words = [
        "f01-01-01-01\t000\tok\t0 0 5 8\tHello",
        "f02-01-01-01\t001\tok\t0 0 5 8\tSecond",
        "f03-01-01-01\t002\tok\t0 0 5 8\tThird",
    ]
    (tmp_path / "lines.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (tmp_path / "forms.txt").write_text("\n".join(forms) + "\n", encoding="utf-8")
    (tmp_path / "words.txt").write_text("\n".join(words) + "\n", encoding="utf-8")
    (tmp_path / "writers.txt").write_text("000\tWriter A\n001\tWriter B\n002\tWriter C\n", encoding="utf-8")
    split_dir = tmp_path / "split"
    split_dir.mkdir()
    (split_dir / "train.txt").write_text("f01-01-01\n", encoding="utf-8")
    (split_dir / "val.txt").write_text("f02-01-01\n", encoding="utf-8")
    (split_dir / "test.txt").write_text("f03-01-01\n", encoding="utf-8")
    for value, line_id in enumerate(("f01-01-01", "f02-01-01", "f03-01-01"), start=100):
        _write_image(tmp_path / "lines" / line_id.split("-")[0] / f"{line_id}.png", value)


def test_synthetic_iam_manifests_and_stats(tmp_path: Path) -> None:
    _fixture(tmp_path)
    records, stats, issues = build_iam_manifests(tmp_path, SPLIT_CFG, ANNOTATION_CFG, "lines", True)
    assert not issues, issues
    assert [len(records[name]) for name in ("train", "val", "test")] == [1, 1, 1]
    assert stats["line_count"] == 3
    assert stats["writer_count"] == 3
    assert stats["writers_by_split"] == {"train": 1, "val": 1, "test": 1}
    assert records["train"][0]["transcription"] == "Hello world"
    assert records["train"][0]["usable"] is True
    assert records["train"][0]["width"] == 16 and records["train"][0]["height"] == 8


def test_detects_missing_image_and_empty_transcription(tmp_path: Path) -> None:
    _fixture(tmp_path)
    (tmp_path / "lines" / "f01" / "f01-01-01.png").unlink()
    (tmp_path / "lines.txt").write_text("f01-01-01\t000\tok\t\n", encoding="utf-8")
    records, _, issues = build_iam_manifests(tmp_path, SPLIT_CFG, ANNOTATION_CFG, "lines", True)
    assert records["train"][0]["usable"] is False
    assert any("missing_image" in issue for issue in issues)
    assert any("empty_transcription" in issue for issue in issues)


def test_writer_overlap_is_reported(tmp_path: Path) -> None:
    _fixture(tmp_path)
    (tmp_path / "split" / "test.txt").write_text("f02-01-01\n", encoding="utf-8")
    _, _, issues = build_iam_manifests(tmp_path, SPLIT_CFG, ANNOTATION_CFG, "lines", False)
    assert any("writer overlap" in issue for issue in issues)


def test_missing_official_split_does_not_invent_a_split(tmp_path: Path) -> None:
    _fixture(tmp_path)
    (tmp_path / "split" / "test.txt").unlink()
    with pytest.raises(SplitUnavailableError):
        read_official_splits(tmp_path, SPLIT_CFG)
