"""MNIST IDX loading and integrity validation.

The local IDX files are read in place (memory-mapped where possible). Nothing is
downloaded, rewritten or silently discarded.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

IMAGE_MAGIC = 2051
LABEL_MAGIC = 2049
UNSIGNED_BYTE = 0x08
HEADER_BYTES_IMAGES = 16
HEADER_BYTES_LABELS = 8


@dataclass(frozen=True)
class IdxHeader:
    """Parsed IDX header."""

    magic: int
    dimensions: int
    dtype_code: int
    sizes: tuple[int, ...]
    data_offset: int


@dataclass(frozen=True)
class IdxSplitReport:
    """Validation result for one image/label IDX pair."""

    name: str
    image_path: Path
    label_path: Path
    image_count: int
    label_count: int
    rows: int
    cols: int
    label_min: int
    label_max: int
    unique_labels: tuple[int, ...]
    label_histogram: tuple[int, ...]
    pixel_min: int
    pixel_max: int
    pixel_mean: float
    pixel_std: float
    image_sha256: str
    label_sha256: str
    issues: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """True when no integrity issue was detected."""
        return not self.issues


def parse_idx_header(path: Path) -> IdxHeader:
    """Parse and sanity-check an IDX header.

    Raises:
        ValueError: If the file is too short or its magic number is unknown.
    """
    with path.open("rb") as stream:
        head = stream.read(HEADER_BYTES_IMAGES)
    if len(head) < HEADER_BYTES_LABELS:
        raise ValueError(f"{path.name}: file too short to contain an IDX header")

    magic = int.from_bytes(head[0:4], "big")
    dimensions = head[3]
    dtype_code = head[2]
    if magic not in {IMAGE_MAGIC, LABEL_MAGIC}:
        raise ValueError(f"{path.name}: unsupported IDX magic number {magic}")
    if dtype_code != UNSIGNED_BYTE:
        raise ValueError(f"{path.name}: unsupported IDX data type code {dtype_code}")

    expected_dimensions = 3 if magic == IMAGE_MAGIC else 1
    if dimensions != expected_dimensions:
        raise ValueError(f"{path.name}: expected {expected_dimensions} dimensions, got {dimensions}")
    count_bytes = HEADER_BYTES_IMAGES if magic == IMAGE_MAGIC else HEADER_BYTES_LABELS
    if len(head) < count_bytes:
        raise ValueError(f"{path.name}: truncated IDX header")

    if magic == IMAGE_MAGIC:
        sizes = (
            int.from_bytes(head[4:8], "big"),
            int.from_bytes(head[8:12], "big"),
            int.from_bytes(head[12:16], "big"),
        )
    else:
        sizes = (int.from_bytes(head[4:8], "big"),)
    return IdxHeader(magic, dimensions, dtype_code, sizes, count_bytes)


def sha256_file(path: Path) -> str:
    """Stream a SHA-256 digest of a file without loading it entirely."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_idx_split(
    image_path: Path,
    label_path: Path,
    expected_rows: int,
    expected_cols: int,
    expected_label_classes: int,
    name: str,
) -> IdxSplitReport:
    """Validate one MNIST IDX image/label pair and compute real statistics."""
    issues: list[str] = []
    img_header = parse_idx_header(image_path)
    lbl_header = parse_idx_header(label_path)

    image_count, rows, cols = img_header.sizes
    label_count = lbl_header.sizes[0]

    expected_image_bytes = HEADER_BYTES_IMAGES + image_count * rows * cols
    expected_label_bytes = HEADER_BYTES_LABELS + label_count
    if image_path.stat().st_size != expected_image_bytes:
        issues.append(
            f"{image_path.name}: size {image_path.stat().st_size} != expected {expected_image_bytes}"
        )
    if label_path.stat().st_size != expected_label_bytes:
        issues.append(
            f"{label_path.name}: size {label_path.stat().st_size} != expected {expected_label_bytes}"
        )
    if image_count != label_count:
        issues.append(f"image count {image_count} != label count {label_count}")
    if (rows, cols) != (expected_rows, expected_cols):
        issues.append(f"image dimensions {rows}x{cols} != expected {expected_rows}x{expected_cols}")

    labels_readable = label_path.stat().st_size >= expected_label_bytes
    if labels_readable and label_count > 0:
        labels: np.ndarray = np.memmap(
            label_path, dtype=np.uint8, mode="r", offset=HEADER_BYTES_LABELS, shape=(label_count,)
        )
        label_min = int(labels.min())
        label_max = int(labels.max())
        unique_labels = tuple(int(v) for v in np.unique(labels))
        histogram = np.bincount(labels.astype(np.int64), minlength=expected_label_classes)
        if label_min < 0 or label_max >= expected_label_classes:
            issues.append(f"label range [{label_min}, {label_max}] outside 0..{expected_label_classes - 1}")
    else:
        label_min = label_max = -1
        unique_labels = ()
        histogram = np.zeros(expected_label_classes, dtype=np.int64)

    images_readable = image_path.stat().st_size >= expected_image_bytes
    if images_readable and image_count > 0:
        images: np.ndarray = np.memmap(
            image_path, dtype=np.uint8, mode="r", offset=HEADER_BYTES_IMAGES, shape=(image_count, rows, cols)
        )
        pixel_min = int(images.min())
        pixel_max = int(images.max())
        pixel_mean = float(images.mean())
        pixel_std = float(images.std())
    else:
        pixel_min = pixel_max = -1
        pixel_mean = pixel_std = 0.0

    return IdxSplitReport(
        name=name,
        image_path=image_path,
        label_path=label_path,
        image_count=image_count,
        label_count=label_count,
        rows=rows,
        cols=cols,
        label_min=label_min,
        label_max=label_max,
        unique_labels=unique_labels,
        label_histogram=tuple(int(v) for v in histogram),
        pixel_min=pixel_min,
        pixel_max=pixel_max,
        pixel_mean=pixel_mean,
        pixel_std=pixel_std,
        image_sha256=sha256_file(image_path),
        label_sha256=sha256_file(label_path),
        issues=tuple(issues),
    )


def load_mnist_images(image_path: Path, report: IdxSplitReport) -> np.ndarray:
    """Return a read-only memory-mapped view of MNIST image bytes."""
    return np.memmap(
        image_path,
        dtype=np.uint8,
        mode="r",
        offset=HEADER_BYTES_IMAGES,
        shape=(report.image_count, report.rows, report.cols),
    )


def mnist_manifest_records(report: IdxSplitReport, source_root: Path) -> list[dict[str, Any]]:
    """Build deterministic manifest records without copying image data."""
    labels = np.memmap(
        report.label_path, dtype=np.uint8, mode="r", offset=HEADER_BYTES_LABELS, shape=(report.label_count,)
    )
    image_rel = report.image_path.relative_to(source_root).as_posix()
    label_rel = report.label_path.relative_to(source_root).as_posix()
    return [
        {
            "id": f"{report.name}-{index:05d}",
            "split": report.name,
            "index": index,
            "image_path": image_rel,
            "label_path": label_rel,
            "label": int(labels[index]),
            "width": report.cols,
            "height": report.rows,
        }
        for index in range(report.image_count)
    ]
