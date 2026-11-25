# Pen2Pixel — Project Status

**Last updated:** 2026-11-25
**Status values:** NOT STARTED · IN PROGRESS · COMPLETED · BLOCKED

This document tracks milestones against their acceptance criteria. A milestone is marked COMPLETED only when its stated acceptance criteria have been verified. Milestone numbering and scope beyond M0 are proposals and require owner approval.

---

## Milestone Tracker

| ID | Milestone | Status | Acceptance criteria | Notes |
|---|---|---|---|---|
| M0 | Complete repository reconnaissance and technical audit | **COMPLETED** (awaiting owner approval to proceed) | Files inspected; no implementation overwritten; dataset presence verified; environment facts verified; documentation gaps identified; tracked git state unchanged; audit report generated | Report: `docs/REPOSITORY_AUDIT.md`. No commits made. New `docs/` files are untracked deliverables. |
| M1 | Requirements engineering and system architecture | **COMPLETED** (awaiting owner approval to proceed) | Recognition scope defined; character vs line distinguished; dataset roles defined; API/UI responsibilities clear; architecture documented; no implementation code added | Docs: `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`. |
| M2 | Development environment and project foundation | **COMPLETED** (awaiting owner approval to proceed) | Fresh setup works; dependencies install without conflicts; PyTorch CPU works; smoke tests pass; no premature dataset/model code | Docs: `docs/ENVIRONMENT_SETUP.md`. Final `pytest -q`: 7 passed. Python 3.13.2 used (3.11 absent); legacy venv left untouched. |
| M3 | Dataset engineering and data quality validation | **COMPLETED / APPROVED** (IAM acquisition BLOCKED pending owner) | Loaders work; integrity checks pass or report exceptions; IAM split integrity logic verified with synthetic fixtures; manifests reproducible; no leakage introduced; no fabricated statistics | MNIST real data validated (60k/10k); IAM manifests generated as blocked/empty; report at `reports/data_quality_report.md`. |
| M4 | Preprocessing pipeline and CRNN-CTC model architecture | **COMPLETED** (pending owner approval) | Shared deterministic preprocessing; variable-width padded batches; CNN+BiLSTM+CTC device-aware model; greedy CTC decode; no training | 22 tests passing; manifests regenerated with updated config hash. No dataset download or model training. |
| M5+ | Implementation milestones *(not yet defined)* | NOT STARTED | To be defined | — |

---

## M0 Verification Summary

- **Objective completed:** Full read-only audit of repository structure, implementation, datasets, environment, documentation, and git state.
- **Files created:** `docs/REPOSITORY_AUDIT.md`, `docs/PROJECT_STATUS.md`.
- **Files modified:** None (no pre-existing file was written).
- **Git state:** `main` at `c1a5d30`, clean tracked tree, synced with `origin/main`; no commit/reset/push; only new untracked `docs/` directory.
- **Environment facts:** Windows 11 (build 26200), i3-1115G4 (2C/4T), 7.65 GB RAM, 31.12 GB free disk, system Python 3.13.2, project venv broken (missing Python 3.11), PyTorch absent, CUDA unverified.
- **Datasets:** MNIST 4 IDX files present and structurally valid; IAM empty (`forms/`, `lines/`); EMNIST absent.
- **Key finding:** All application source files are 0 bytes; only `dataset/download_emnist.py` contains code.
- **Known limitations:** No dependency installation or dataset download was permitted, so no runtime verification of the ML stack was possible; CUDA status cannot be confirmed without PyTorch; dataset provenance/licensing not independently verified.
- **Remaining issues:** See §9 (Technical Risks) in the audit report.
- **Next action:** Await owner review and the Milestone 1 prompt.

---

## M1 Verification Summary

- **Objective completed:** Product definition, functional and non-functional requirements, ML requirements, dataset roles, system architecture (including Mermaid diagrams), and a technical decision log.
- **Files created:** `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`.
- **Files modified:** `docs/PROJECT_STATUS.md` only (this tracker).
- **Implementation code:** None added. No source, config, requirement, or test file was created or edited.
- **Git state:** `main` at `c1a5d30`; no commit/reset/push; tracked tree unchanged; all `docs/` files remain untracked deliverables.
- **Requirements decisions:** Text-line recognition baseline; character recognition distinct; MNIST supporting / IAM primary / EMNIST optional; FastAPI + plain HTML/CSS/JS; config-driven limits; CER primary metric; no invented SLOs or measured results.
- **Known limitations:** All decisions are PROPOSED pending approval; IAM/EMNIST data remain absent; vocabulary must be derived from licensed IAM transcripts; no performance figures are claimed.
- **Remaining issues:** See M0 audit §9 risks and the deferred-capability register in `docs/DECISIONS.md` (D-21).
- **Next action:** Await owner approval; do not start M2 automatically.

---

## M2 Verification Summary

- **Objective completed:** Working Python environment, pinned/split dependencies, YAML configuration with env overrides, package initialization, logging, pytest/Ruff configuration, updated `.gitignore`, and environment smoke tests.
- **Files created:** `configs/default.yaml`, `pyproject.toml`, `handwriting-recognition/requirements-dev.txt`, `handwriting-recognition/requirements-optional.txt`, `handwriting-recognition/config/{__init__.py,loader.py}`, `handwriting-recognition/utils/{__init__.py,logging_config.py}`, `handwriting-recognition/tests/{__init__.py,test_environment.py}`, package `__init__.py` files for `api`, `backend`, `dataset`, `models`, `preprocessing`, and `docs/ENVIRONMENT_SETUP.md`.
- **Files modified:** `handwriting-recognition/requirements.txt`, `.gitignore`, `docs/PROJECT_STATUS.md`.
- **Environment decision:** Python 3.11 absent; used available Python 3.13.2 in a new root `.venv`. PyTorch 2.15.0 cp313 Windows wheel verified. Broken legacy `handwriting-recognition/venv` left untouched and ignored.
- **Commands/results:** `pip install` succeeded; `pip check` → no broken requirements; `pytest --collect-only` → 7 collected; first `pytest -q` → 3 passed / 4 failed (config validation bug); bug fixed; final `pytest -q` → **7 passed in 2.43s**.
- **Actual verification:** torch 2.15.0+cpu, numpy 2.3.3, cv2 5.1.0, Pillow 13.0.0; `cuda_available False` — no GPU claim.
- **Known limitations:** Python 3.11 unavailable; no dataset/model implementation; no CPU performance benchmark; optional dependencies not installed.
- **Remaining issues:** M0/M1 risks still open; IAM/EMNIST data absent; Milestone 3 blocked until M2 approval.
- **Next action:** Await owner approval before starting Milestone 3.

---

## M3 Verification Summary

- **Objective completed:** MNIST IDX loading/validation, IAM annotation parsing with official-partition enforcement, validation reporting, deterministic manifests, and a data quality report. No dataset download, no model training.
- **Files created:** `handwriting-recognition/dataset/{idx.py,iam.py,manifest.py,pipeline.py}`, `scripts/build_data_manifests.py`, `handwriting-recognition/tests/{test_mnist.py,test_iam.py}`, `docs/IAM_ACQUISITION.md`, `reports/data_quality_report.md`, `reports/manifests/*.jsonl`.
- **Files modified:** `configs/default.yaml` (dataset section), `handwriting-recognition/config/loader.py` (new required section), `.gitignore` unchanged this milestone, `docs/PROJECT_STATUS.md`.
- **Real MNIST results:** train 60,000 images/labels; test 10,000 images/labels; 28x28 unsigned-byte; labels 0–9 with real histograms; magic/size/count/range checks PASS; split files distinct by SHA-256.
- **IAM status:** BLOCKED — `lines.txt` and split files absent; official host verification timed out. Empty blocked manifests generated; no statistics fabricated. Parser and writer-disjointness checks verified with synthetic fixtures.
- **Commands/results:** `pytest -q` → 15 passed; first pipeline run produced 5 manifests + report; second run produced byte-identical outputs (all 6 files reproducible).
- **Bugs found and fixed during testing:** truncated IDX file raised uncaught memmap error — loader now guards memmapping; synthetic fixtures corrected (distinct images, valid size assertion).
- **Known limitations:** real IAM split integrity cannot be confirmed until licensed data is supplied; duplicate detection is exact-byte SHA-256 only; no model or accuracy work performed.
- **Remaining issues:** Owner must complete `docs/IAM_ACQUISITION.md` checklist; EMNIST remains optional and absent.
- **Next action:** Await owner approval; do not start model training without a new milestone prompt.

---

## M4 Verification Summary

- **Objective completed:** Implemented the shared preprocessing pipeline and the device-aware CNN + BiLSTM + CTC model architecture. No training loop, API, frontend, dataset download, or model checkpoint was introduced.
- **Files created:** `handwriting-recognition/preprocessing/preprocess.py`, `handwriting-recognition/models/{cnn_model.py,crnn_ctc_model.py,decoding.py}`, `handwriting-recognition/tests/{test_preprocessing.py,test_models.py}`.
- **Files modified:** `configs/default.yaml` (model vocabulary, blank token, CNN/LSTM settings), `handwriting-recognition/config/loader.py` (model config validation), `docs/PROJECT_STATUS.md`; manifests/report regenerated with the new config hash.
- **Commands/results:** `pytest -q` → **22 passed**. First runs exposed real config issues (unquoted YAML digits parsed as integers; one incorrect test shape assertion) — all corrected without weakening checks.
- **Verified behaviour:** deterministic grayscale/denoise/binarize/deskew/normalize/resize; aspect-ratio-preserving height normalization with configurable width cap; padded batches with true lengths; CRNN forward on variable widths with packed BiLSTM; log-probability outputs summing to 1; greedy CTC blank/repeat collapse; CPU-only execution.
- **Known limitations:** No trained weights, no accuracy figures, no CUDA claim (`cuda_available False` from M2); case-folded uppercase vocabulary is provisional per D-04 until licensed IAM transcripts are available; augmentation remains deferred to the training milestone.
- **Remaining issues:** IAM acquisition still BLOCKED; training/evaluation/inference/API/frontend still unimplemented.
- **Next action:** Await owner approval before starting training/inference work.

---

## Change Log

| Date | Change |
|---|---|
| 2026-11-25 | Initial status file created for Milestone 0 audit. |
| 2026-11-25 | Milestone 1 requirements and architecture documentation added; M1 marked COMPLETED pending approval. |
| 2026-11-25 | Milestone 2 environment and foundation implemented; 7 smoke tests passing; M2 marked COMPLETED pending approval. |
| 2026-11-25 | Milestone 3 dataset pipeline implemented; 15 tests passing; deterministic manifests and data quality report generated; IAM acquisition blocked pending owner. |
| 2026-11-25 | Owner approved Milestone 3; IAM acquisition remains BLOCKED; awaiting next milestone prompt. |
| 2026-11-25 | Milestone 4 preprocessing and CRNN-CTC architecture implemented; 22 tests passing; pending approval. |
