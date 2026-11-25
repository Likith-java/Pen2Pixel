# IAM Handwriting Database — Acquisition and Licensing Checklist

**Status:** BLOCKED — dataset not present; owner action required.
**Date:** 2026-11-25
**Related:** `docs/DECISIONS.md` D-07/D-08, `docs/REQUIREMENTS.md` §6, `reports/data_quality_report.md`.

---

## 1. Verification Attempt (honest status)

An attempt was made to verify the official source from this environment:

- Canonical source identified from project documentation/domain knowledge:
  `https://www.iapr-tc11.org/mediawiki/index.php/IAM_Handwriting_Database_-_Database_v3.0`
- Live verification **failed**: `webfetch` returned a transport error and a direct HTTP request timed out.
- Therefore the source URL, current terms, exact archive filenames and checksums are **NOT verified** in this environment and must be confirmed by the owner before any download.

No dataset was downloaded, no authentication was attempted, and no licensing restriction was bypassed.

---

## 2. What Must Be Verified Before Download

| Item | Required action | Current state |
|---|---|---|
| Official source | Confirm the current IAPR TC11 / University of IAM database page and download links. | Unverified (network timeout) |
| Terms and conditions | Read the current license/terms on the official page and the `license.txt` inside the archive. Record usage restrictions and attribution requirements. | Unverified |
| Registration | Determine whether access requires registration, a request form, or acceptance of terms. Complete it personally if required. | Not done |
| Archive filenames/checksums | Record exact filenames and checksums from the official listing. | Unverified |
| Redistribution | Confirm whether extracted files may be shared in this repository (expected: **no**; they should stay gitignored). | Must confirm |

**Rule:** IAM files remain under `handwriting-recognition/dataset/iam/`, which is gitignored. Do not commit dataset images or annotations.

---

## 3. Expected Layout (to confirm against the official archive)

The pipeline expects these files after authorized extraction into `handwriting-recognition/dataset/iam/`:

```text
iam/
├── forms/                 form images, e.g. f01/f01-01.png
├── lines/                 line images, e.g. f01/f01-01-01.png
├── words/                 word images (parsed but not used by the line baseline)
├── forms.txt              form → writer/status/line hierarchy
├── lines.txt              line_id <tab> writer_id <tab> status <tab> transcription
├── words.txt              word annotations (transcription in final field)
├── writers.txt            writer identifiers
└── split/                 official writer-independent partition
    ├── train.txt
    ├── val.txt
    └── test.txt
```

If the official partition uses different filenames, set them in `configs/default.yaml` under `dataset.iam.split`. **Do not generate a random replacement split** — the parser raises `SplitUnavailableError` when official files are missing.

Typical distribution is via separate compressed archives (commonly `.tgz`) for lines, forms and words, plus annotation text files. Exact filenames must be confirmed from the official listing; they are **not** assumed here.

---

## 4. Storage Estimate (planning only)

An order-of-magnitude planning allowance is **low single-digit GB** for line/form images plus annotations, with additional temporary space for archives during extraction. This is **not a verified figure** — confirm exact archive sizes from the official listing before download. The machine currently has about 31 GB free on `C:`, so verify headroom before extraction.

---

## 5. Owner Checklist

1. [ ] Confirm the official IAM database URL is reachable and current.
2. [ ] Read and record the current license/terms and attribution requirements.
3. [ ] Complete any required registration or access request personally.
4. [ ] Download **only** from the official source using the approved mechanism.
5. [ ] Record archive filenames, sizes and checksums in this document.
6. [ ] Verify checksums before extraction.
7. [ ] Extract into `handwriting-recognition/dataset/iam/` (gitignored).
8. [ ] Confirm `lines.txt`, `forms.txt`, `words.txt`, `writers.txt`, image folders and official split files exist.
9. [ ] Update `configs/default.yaml` if official split filenames differ.
10. [ ] Run `.venv\Scripts\python.exe scripts/build_data_manifests.py`.
11. [ ] Review `reports/data_quality_report.md`, especially writer-disjointness and unusable-sample counts.
12. [ ] Record attribution/license details in project documentation.

Until these steps are complete, IAM train/val/test manifests are generated as **empty manifests with `status: blocked_source_unavailable`**, and no IAM statistics are reported.

---

## 6. EMNIST Note

EMNIST remains optional (decision D-07). Its existing downloader script must not be run implicitly, and `dataset/emnist/*.npz` is now gitignored to prevent accidental commits. Any future EMNIST use requires a documented technical justification and the same licensing review.
