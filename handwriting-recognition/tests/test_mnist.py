"""MNIST integrity tests using the real local IDX files plus synthetic fixtures."""

from __future__ import annotations

import struct
from pathlib import Path

from config import get_path, load_config
from dataset.idx import mnist_manifest_records, validate_idx_split
from dataset.manifest import render_manifest

TRAIN_FILES = ("train-images.idx3-ubyte", "train-labels.idx1-ubyte")
TEST_FILES = ("t10k-images.idx3-ubyte", "t10k-labels.idx1-ubyte")


def _validate(mnist_dir: Path, files: tuple[str, str], name: str):
    cfg = load_config()
    mnist_cfg = cfg["dataset"]["mnist"]
    return validate_idx_split(
        mnist_dir / files[0],
        mnist_dir / files[1],
        int(mnist_cfg["expected_rows"]),
        int(mnist_cfg["expected_cols"]),
        int(mnist_cfg["expected_label_classes"]),
        name,
    )


def test_real_mnist_train_integrity() -> None:
    mnist_dir = get_path(load_config(), "paths.mnist_dir")
    report = _validate(mnist_dir, TRAIN_FILES, "train")
    assert report.ok, report.issues
    assert report.image_count == 60000
    assert report.label_count == 60000
    assert (report.rows, report.cols) == (28, 28)
    assert report.unique_labels == tuple(range(10))
    assert (report.pixel_min, report.pixel_max) == (0, 255)
    assert sum(report.label_histogram) == 60000


def test_real_mnist_test_integrity_and_split_separation() -> None:
    mnist_dir = get_path(load_config(), "paths.mnist_dir")
    train = _validate(mnist_dir, TRAIN_FILES, "train")
    test = _validate(mnist_dir, TEST_FILES, "test")
    assert test.ok, test.issues
    assert test.image_count == 10000
    assert test.label_count == 10000
    assert train.image_sha256 != test.image_sha256
    assert train.label_sha256 != test.label_sha256


def test_manifest_records_are_deterministic() -> None:
    mnist_dir = get_path(load_config(), "paths.mnist_dir")
    report = _validate(mnist_dir, TEST_FILES, "test")
    records = mnist_manifest_records(report, mnist_dir.parent.parent.parent)
    assert len(records) == 10000
    assert records[0]["id"] == "test-00000"
    assert records[0]["label"] in range(10)
    meta = {"dataset": "mnist", "split": "test"}
    assert render_manifest(meta, records[:5]) == render_manifest(meta, records[:5])


def _write_synthetic_idx(folder: Path, count: int, rows: int, cols: int) -> None:
    images = folder / "images.idx3-ubyte"
    labels = folder / "labels.idx1-ubyte"
    images.write_bytes(
        struct.pack(">IIII", 2051, count, rows, cols) + bytes(bytearray(count * rows * cols))
    )
    labels.write_bytes(struct.pack(">II", 2049, count) + bytes(bytearray(count)))


def test_detects_corrupted_synthetic_idx(tmp_path: Path) -> None:
    _write_synthetic_idx(tmp_path, 2, 2, 2)
    labels = tmp_path / "labels.idx1-ubyte"
    labels.write_bytes(struct.pack(">II", 2049, 3) + bytes(bytearray([0, 1, 12])))
    report = validate_idx_split(
        tmp_path / "images.idx3-ubyte",
        labels,
        2,
        2,
        10,
        "synthetic_bad",
    )
    assert not report.ok
    assert any("count" in issue for issue in report.issues)
    assert any("label range" in issue for issue in report.issues)
    truncated = tmp_path / "truncated.idx1-ubyte"
    truncated.write_bytes(struct.pack(">II", 2049, 2) + bytes(bytearray([0])))
    size_report = validate_idx_split(
        tmp_path / "images.idx3-ubyte", truncated, 2, 2, 10, "synthetic_truncated"
    )
    assert any("size" in issue for issue in size_report.issues)
