"""IAM annotation parsing, hierarchy validation and split verification.

Only official annotation files are consumed. If the official writer-independent
partition files are absent, this module raises :class:`SplitUnavailableError`
instead of inventing a random split.
"""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import cv2

from dataset.idx import sha256_file


class SplitUnavailableError(FileNotFoundError):
    """Raised when the official IAM partition files cannot be found."""


@dataclass(frozen=True)
class LineRecord:
    line_id: str
    writer_id: str
    status: str
    transcription: str


@dataclass(frozen=True)
class FormRecord:
    form_id: str
    writer_id: str
    status: str
    line_ids: tuple[str, ...]


@dataclass(frozen=True)
class WordRecord:
    word_id: str
    writer_id: str
    status: str
    transcription: str


@dataclass(frozen=True)
class IamAnnotations:
    lines: dict[str, LineRecord]
    forms: dict[str, FormRecord]
    words: dict[str, WordRecord]
    writers: set[str]
    issues: tuple[str, ...]


def read_lines_file(path: Path) -> tuple[dict[str, LineRecord], list[str]]:
    """Parse the official tab-separated lines.txt annotation file."""
    records: dict[str, LineRecord] = {}
    issues: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for number, raw in enumerate(stream, start=1):
            text = raw.rstrip("\r\n")
            if not text.strip():
                continue
            fields = text.split("\t")
            if len(fields) < 4:
                issues.append(f"{path.name}:{number}: expected at least 4 tab-separated fields")
                continue
            line_id, writer_id, status = fields[0].strip(), fields[1].strip(), fields[2].strip()
            transcription = "\t".join(fields[3:]).strip()
            if line_id in records:
                issues.append(f"{path.name}:{number}: duplicate line id {line_id}")
                continue
            if not transcription:
                issues.append(f"{path.name}:{number}: empty transcription for {line_id}")
            records[line_id] = LineRecord(line_id, writer_id, status, transcription)
    return records, issues


def read_forms_file(path: Path) -> tuple[dict[str, FormRecord], list[str]]:
    """Parse forms.txt (whitespace-separated: id, writer, status, n, line ids...)."""
    records: dict[str, FormRecord] = {}
    issues: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for number, raw in enumerate(stream, start=1):
            parts = raw.split()
            if not parts:
                continue
            if len(parts) < 4:
                issues.append(f"{path.name}:{number}: expected at least 4 fields")
                continue
            form_id, writer_id, status = parts[0], parts[1], parts[2]
            try:
                declared = int(parts[3])
            except ValueError:
                issues.append(f"{path.name}:{number}: invalid line count {parts[3]!r}")
                continue
            line_ids = tuple(parts[4:])
            if len(line_ids) != declared:
                issues.append(f"{path.name}:{number}: declared {declared} lines, found {len(line_ids)}")
            if form_id in records:
                issues.append(f"{path.name}:{number}: duplicate form id {form_id}")
                continue
            records[form_id] = FormRecord(form_id, writer_id, status, line_ids)
    return records, issues


def read_words_file(path: Path) -> tuple[dict[str, WordRecord], list[str]]:
    """Parse words.txt; transcription is the final tab-separated field."""
    records: dict[str, WordRecord] = {}
    issues: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for number, raw in enumerate(stream, start=1):
            parts = raw.rstrip("\r\n").split("\t")
            if len(parts) < 4:
                issues.append(f"{path.name}:{number}: expected at least 4 tab-separated fields")
                continue
            word_id, writer_id, status = parts[0].strip(), parts[1].strip(), parts[2].strip()
            transcription = parts[-1].strip()
            if word_id in records:
                issues.append(f"{path.name}:{number}: duplicate word id {word_id}")
                continue
            if not transcription:
                issues.append(f"{path.name}:{number}: empty word transcription for {word_id}")
            records[word_id] = WordRecord(word_id, writer_id, status, transcription)
    return records, issues


def read_writers_file(path: Path) -> set[str]:
    """Collect writer ids from writers.txt (first token on each line)."""
    writers: set[str] = set()
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            parts = raw.split()
            if parts:
                writers.add(parts[0])
    return writers


def read_annotations(root: Path, annotation_cfg: Mapping[str, str]) -> IamAnnotations:
    """Read and cross-check all official IAM annotation files."""
    issues: list[str] = []
    lines_file = root / annotation_cfg["lines_file"]
    forms_file = root / annotation_cfg["forms_file"]
    words_file = root / annotation_cfg["words_file"]
    writers_file = root / annotation_cfg["writers_file"]

    lines, line_issues = read_lines_file(lines_file)
    forms, form_issues = read_forms_file(forms_file)
    words, word_issues = read_words_file(words_file)
    writers = read_writers_file(writers_file)
    issues.extend(line_issues + form_issues + word_issues)

    for line_id, line in lines.items():
        form_id = line_id.rsplit("-", 1)[0]
        form = forms.get(form_id)
        if form is None:
            issues.append(f"line {line_id}: missing form record {form_id}")
        elif form.writer_id != line.writer_id:
            issues.append(f"line {line_id}: writer mismatch with form {form_id}")
        if line.writer_id not in writers:
            issues.append(f"line {line_id}: unknown writer id {line.writer_id}")

    for word_id, word in words.items():
        line_id = word_id.rsplit("-", 1)[0]
        if line_id not in lines:
            issues.append(f"word {word_id}: missing parent line {line_id}")
        elif lines[line_id].writer_id != word.writer_id:
            issues.append(f"word {word_id}: writer mismatch with line {line_id}")

    return IamAnnotations(lines, forms, words, writers, tuple(issues))


def read_official_splits(root: Path, split_cfg: Mapping[str, str]) -> dict[str, set[str]]:
    """Read the official writer-independent partition files.

    Raises:
        SplitUnavailableError: If any expected split file is missing. No
            replacement split is generated.
    """
    split_dir = root / split_cfg["dir"]
    splits: dict[str, set[str]] = {}
    missing: list[str] = []
    for split_name in ("train", "val", "test"):
        path = split_dir / split_cfg[split_name]
        if not path.is_file():
            missing.append(str(path))
            continue
        ids: set[str] = set()
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            for raw in stream:
                line_id = raw.strip()
                if line_id:
                    ids.add(line_id)
        splits[split_name] = ids
    if missing:
        raise SplitUnavailableError("Missing official IAM split files: " + ", ".join(missing))
    return splits


def verify_split_integrity(
    splits: Mapping[str, set[str]], annotations: IamAnnotations
) -> tuple[list[str], dict[str, set[str]]]:
    """Check line membership and writer-level disjointness across splits."""
    issues: list[str] = []
    writers_by_split: dict[str, set[str]] = {}

    assigned: dict[str, list[str]] = defaultdict(list)
    for split_name, ids in splits.items():
        for line_id in ids:
            assigned[line_id].append(split_name)
            if line_id not in annotations.lines:
                issues.append(f"split {split_name}: line id {line_id} missing from lines.txt")

    for line_id, names in assigned.items():
        if len(names) > 1:
            issues.append(f"line {line_id} appears in multiple splits: {sorted(names)}")

    for split_name, ids in splits.items():
        writers_by_split[split_name] = {
            annotations.lines[line_id].writer_id for line_id in ids if line_id in annotations.lines
        }

    names = list(splits)
    for i, first in enumerate(names):
        for second in names[i + 1 :]:
            overlap = sorted(writers_by_split[first] & writers_by_split[second])
            if overlap:
                issues.append(f"writer overlap between {first} and {second}: {overlap[:10]}")

    unassigned = sorted(set(annotations.lines) - set(assigned))
    if unassigned:
        issues.append(f"{len(unassigned)} annotated lines are not assigned to any official split")
    return issues, writers_by_split


def build_iam_manifests(
    root: Path,
    split_cfg: Mapping[str, str],
    annotation_cfg: Mapping[str, str],
    lines_subdir: str,
    hash_images: bool,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], list[str]]:
    """Build IAM line manifests and statistics from official annotations."""
    annotations = read_annotations(root, annotation_cfg)
    splits = read_official_splits(root, split_cfg)
    split_issues, writers_by_split = verify_split_integrity(splits, annotations)
    issues = list(annotations.issues) + split_issues

    records_by_split: dict[str, list[dict[str, Any]]] = {}
    content_hashes: dict[str, str] = {}
    stats: dict[str, Any] = {
        "line_count": len(annotations.lines),
        "form_count": len(annotations.forms),
        "word_count": len(annotations.words),
        "writer_count": len(annotations.writers),
        "writers_by_split": {name: len(writers) for name, writers in writers_by_split.items()},
    }
    dimension_counts: Counter[tuple[int, int]] = Counter()
    text_lengths: list[int] = []
    writer_counts: Counter[str] = Counter()

    for split_name in ("train", "val", "test"):
        split_records: list[dict[str, Any]] = []
        for line_id in sorted(splits[split_name]):
            line = annotations.lines.get(line_id)
            if line is None:
                continue
            form_folder = line_id.split("-")[0]
            image_rel = (Path(lines_subdir) / form_folder / f"{line_id}.png").as_posix()
            image_path = root / image_rel
            record_issues: list[str] = []
            width = height = -1
            image_hash = ""

            if not image_path.is_file():
                record_issues.append("missing_image")
            else:
                image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
                if image is None:
                    record_issues.append("invalid_image")
                else:
                    height, width = image.shape
                    dimension_counts[(width, height)] += 1
                if hash_images:
                    image_hash = sha256_file(image_path)
                    if image_hash in content_hashes:
                        record_issues.append(f"duplicate_content_with:{content_hashes[image_hash]}")
                    else:
                        content_hashes[image_hash] = line_id

            if not line.transcription.strip():
                record_issues.append("empty_transcription")
            if line.status.strip().lower() != "ok":
                record_issues.append(f"status:{line.status}")
            if line.writer_id not in annotations.writers:
                record_issues.append("unknown_writer")

            text_lengths.append(len(line.transcription))
            writer_counts[line.writer_id] += 1
            split_records.append(
                {
                    "id": line_id,
                    "split": split_name,
                    "form_id": line_id.rsplit("-", 1)[0],
                    "writer_id": line.writer_id,
                    "image_path": image_rel,
                    "transcription": line.transcription,
                    "status": line.status,
                    "width": width,
                    "height": height,
                    "image_sha256": image_hash,
                    "usable": not record_issues,
                    "issues": record_issues,
                }
            )
            for issue in record_issues:
                issues.append(f"{split_name}/{line_id}: {issue}")

        records_by_split[split_name] = split_records

    stats["dimension_counts"] = {f"{w}x{h}": count for (w, h), count in sorted(dimension_counts.items())}
    stats["text_lengths"] = {
        "count": len(text_lengths),
        "min": min(text_lengths) if text_lengths else 0,
        "max": max(text_lengths) if text_lengths else 0,
        "mean": round(sum(text_lengths) / len(text_lengths), 2) if text_lengths else 0.0,
    }
    stats["writers_by_line_count_top10"] = writer_counts.most_common(10)
    stats["unusable_records"] = sum(
        1 for records in records_by_split.values() for record in records if not record["usable"]
    )
    return records_by_split, stats, issues
