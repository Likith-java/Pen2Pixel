# Pen2Pixel — Technical Decision Log

**Version:** 1.0 (Milestone 1 — proposed, pending owner approval)
**Date:** 2026-11-25
**Basis:** `docs/REPOSITORY_AUDIT.md` (Milestone 0) and confirmed project constraints.

All decisions below are **PROPOSED** and require explicit owner approval before implementation. Status values: PROPOSED · ACCEPTED · REJECTED · DEFERRED.

---

## Decision Summary

| ID | Decision | Status |
|---|---|---|
| D-01 | Text-line recognition first; full-page deferred | PROPOSED |
| D-02 | PyTorch only; CPU-first, device-aware | PROPOSED |
| D-03 | CNN + BiLSTM + CTC baseline | PROPOSED |
| D-04 | Config-derived, case-normalized vocabulary + CTC blank | PROPOSED |
| D-05 | Fixed height, variable width with padding/length masks | PROPOSED |
| D-06 | One shared preprocessing path for train/eval/inference | PROPOSED |
| D-07 | Dataset roles: MNIST supporting, IAM primary, EMNIST optional | PROPOSED |
| D-08 | No implicit dataset downloads; explicit opt-in | PROPOSED |
| D-09 | YAML config + typed settings as source of truth | PROPOSED |
| D-10 | Fixed seeds and checkpoint provenance | PROPOSED |
| D-11 | Writer/group-level split manifests to prevent leakage | PROPOSED |
| D-12 | FastAPI + plain HTML/CSS/JS, same-origin | PROPOSED |
| D-13 | API boundary: app factory / routers / inference facade | PROPOSED |
| D-14 | Uniform typed error envelope with request IDs | PROPOSED |
| D-15 | CER primary, WER secondary; no fabricated metrics | PROPOSED |
| D-16 | pytest with synthetic data and stub model | PROPOSED |
| D-17 | Pinned and split dependencies; remove unnecessary packages | PROPOSED |
| D-18 | No GPU or performance claims without measurement | PROPOSED |
| D-19 | Local ephemeral uploads; privacy defaults | PROPOSED |
| D-20 | Greedy CTC decoding baseline | PROPOSED |
| D-21 | Deferred capabilities register | PROPOSED |

---

## D-01 — Recognition scope

- **Context:** The product problem mentions handwritten text, which could mean a character, a line, a paragraph, or a full page. The M0 audit shows no implementation and a documentation mismatch.
- **Decision:** Baseline recognizes **one handwritten English text line per image**. Character recognition is a supporting learning task; full-page recognition is a future extension.
- **Justification:** Matches the confirmed primary task, keeps evaluation well-defined, and avoids inventing layout-segmentation capability that does not exist.
- **Alternatives considered:** Full-page first (rejected: requires layout analysis and unavailable data); single-character product (rejected: not the stated task).
- **Consequences:** Users must supply cropped lines; future full-page mode must be additive to the API contract.

## D-02 — Framework and hardware posture

- **Context:** Confirmed decisions specify Python + PyTorch; audit found PyTorch absent, broken venv, 2-core CPU, 7.65 GB RAM, and no evidence of CUDA.
- **Decision:** PyTorch only. All code is device-aware with CPU as the default and only verified target.
- **Justification:** Avoids duplicate ML frameworks; hardware facts do not support GPU claims.
- **Alternatives considered:** TensorFlow/Keras (rejected by confirmed decision); unconditional CUDA use (rejected as unverifiable).
- **Consequences:** Training may be slow; performance targets must be measured, not promised.

## D-03 — Model architecture

- **Context:** Confirmed main architecture is CNN + Bidirectional LSTM + CTC.
- **Decision:** Adopt this as the baseline: CNN feature extractor → BiLSTM → projection to vocab + blank → CTC loss.
- **Justification:** Suitable for variable-width sequence transcription and compatible with CPU inference.
- **Alternatives considered:** Attention encoder–decoder and Transformer OCR (deferred: higher data/compute needs); pure CNN classifier (insufficient for text lines).
- **Consequences:** CTC's monotonic-alignment and conditional-independence limits are documented in `docs/REQUIREMENTS.md` §5.7.

## D-04 — Vocabulary and blank token

- **Context:** IAM vocabulary cannot be assumed; M0 confirmed IAM data is absent.
- **Decision:** Vocabulary derived from licensed transcripts and stored in config. Proposed baseline: uppercase `A–Z`, digits `0–9`, space, `. , ' -`, plus a dedicated CTC blank index; case folding controlled by config.
- **Justification:** Reduces class count and case ambiguity; keeps behaviour explicit and reproducible.
- **Alternatives considered:** Full mixed-case vocabulary (rejected for baseline: more classes and ambiguous labels); fixed hard-coded alphabet (rejected: dataset mismatch risk).
- **Consequences:** Lowercase input text will be normalized; out-of-vocabulary behaviour must be explicit.

## D-05 — Image geometry and variable width

- **Context:** CTC needs a time sequence; text-line widths vary.
- **Decision:** Normalize height to a configured value; scale width proportionally; pad batches to max width and pass true lengths/masks to BiLSTM and CTC. No width stretching.
- **Justification:** Preserves glyph shape and supports variable-length output.
- **Alternatives considered:** Fixed square resize (rejected: distorts handwriting); per-line cropping without batching (deferred: inefficient).
- **Consequences:** Need a configured maximum width and explicit overflow handling.

## D-06 — Shared preprocessing

- **Context:** M0 shows separate `preprocessing/` placeholders and risks of train/serve skew.
- **Decision:** A single preprocessing implementation is called by training, evaluation, and inference; augmentation is training-only and separately located.
- **Justification:** Prevents silent quality differences between offline and online paths.
- **Consequences:** Preprocessing changes require re-training/re-evaluation records.

## D-07 — Dataset roles

- **Context:** MNIST files are present and verified; IAM directories are empty; EMNIST is absent; only a downloader script exists.
- **Decision:** MNIST = supporting character learning and pipeline validation; IAM = primary line-recognition dataset; EMNIST = optional, only with documented justification.
- **Justification:** Aligns data roles with the product task and with what is actually available.
- **Alternatives considered:** Train the line model on MNIST alone (rejected: no line transcripts); enable EMNIST by default (rejected: resource and licensing concerns).
- **Consequences:** IAM acquisition/licensing is a blocking dependency for real line recognition.

## D-08 — No implicit downloads

- **Context:** The existing EMNIST script calls `download=True` and would silently fetch a large dataset if run; `.gitignore` does not cover its `.npz` output.
- **Decision:** All dataset acquisition requires explicit owner opt-in, a documented purpose, license/attribution record, and disk/RAM check. Downloads are never part of import, test, or app startup.
- **Justification:** Compliance, reproducibility, and the audited 31 GB free disk / low free RAM.
- **Consequences:** Some milestones will remain blocked until data is approved and supplied.

## D-09 — Configuration

- **Context:** M0 found hard-coded values in the only real script and no config files.
- **Decision:** YAML config with typed settings; all paths, limits, hyperparameters, device, seed, and vocabulary keys are config-driven. Proposed starter values are explicitly non-final and require validation.
- **Justification:** Reproducibility and avoiding arbitrary magic numbers.
- **Alternatives considered:** Environment variables only (rejected: poor for nested ML config); hard-coded Python constants (rejected by project rule).
- **Consequences:** Adds PyYAML as a declared dependency; config validation tests needed.

## D-10 — Seeds and provenance

- **Context:** No reproducibility infrastructure exists.
- **Decision:** Fixed seeds for Python, NumPy, and PyTorch; each checkpoint records seed, config hash, vocabulary, and dependency versions.
- **Justification:** Required to reproduce any result and to prevent unverifiable claims.
- **Consequences:** Some nondeterminism may remain from CPU threading; must be documented if observed.

## D-11 — Leakage prevention

- **Context:** IAM data will include multiple lines per writer; random line-level splitting risks leakage.
- **Decision:** Maintain a manifest with writer/line-group identity; split at group level into train/validation/test; test used only for final evaluation.
- **Justification:** Prevents inflated metrics and respects project rule 9.
- **Consequences:** Requires manifest support before IAM training; MNIST's provided train/test split is used as-is.

## D-12 — Web stack

- **Context:** README claims React + Node/Express, but confirmed decisions and empty placeholders are Python/FastAPI/plain HTML/CSS/JS.
- **Decision:** FastAPI serves a same-origin static plain-JS frontend; no build step in baseline.
- **Justification:** Matches confirmed decisions and existing files; avoids introducing unnecessary technology.
- **Consequences:** README must be corrected later; UI features remain simple.

## D-13 — API/inference boundaries

- **Context:** M0 identified overlapping `api/routes.py`, `backend/app.py`, and `backend/inference.py`.
- **Decision:** `backend/app.py` = app factory and middleware/static mounting; `api/routes.py` = routers and schemas; `backend/inference.py` = model/preprocessing facade. No new duplicate API module.
- **Justification:** Resolves ambiguity without renaming or deleting existing tracked files.
- **Consequences:** Three small modules; clear one-way dependency (routes → inference → preprocessing/models).

## D-14 — Error handling

- **Context:** Requirement FR-30–34 and audit risk of unclear failures.
- **Decision:** Typed exception hierarchy and one JSON error envelope with `error.code`, `error.message`, optional `error.details`, and `request_id`; no stack traces to clients.
- **Justification:** Debuggable, secure, and testable.
- **Consequences:** Error codes must be documented and covered by API tests.

## D-15 — Metrics

- **Context:** Requirement MLR-26–29; no metrics or models exist.
- **Decision:** CER primary, WER and exact-line accuracy secondary, computed by shared tested utilities. No metric is reported without config, checkpoint, and split manifest.
- **Justification:** Standard for sequence transcription; prevents fabricated results.
- **Consequences:** Evaluation milestone cannot be marked complete without a real checkpoint and held-out data.

## D-16 — Testing strategy

- **Context:** No tests and pytest missing from requirements; global pytest exists but venv is broken.
- **Decision:** pytest with synthetic images, config fixtures, shape/logic tests for CTC and metrics, and API tests using a stub inference object. No test requires network, GPU, or trained weights.
- **Justification:** Fast, deterministic, hardware-independent verification.
- **Consequences:** A future integration test may be added later with a locally trained toy checkpoint.

## D-17 — Dependencies

- **Context:** `requirements.txt` is unpinned and includes `tensorflow-datasets` and `torchaudio`.
- **Decision:** Pin runtime versions; separate dev/test requirements; remove unnecessary packages; declare pytest and PyYAML.
- **Justification:** Reproducible installs and reduced surface area.
- **Consequences:** Requires a working environment rebuild (blocked until interpreter issue resolved).

## D-18 — No unverified claims

- **Context:** No PyTorch installation, no CUDA evidence, no benchmarks.
- **Decision:** Do not claim GPU acceleration, accuracy, latency, or "working model" until measured and evidenced.
- **Justification:** Engineering rule 19 and factual honesty.
- **Consequences:** Documentation must label all numeric targets as measurements pending.

## D-19 — Uploads and privacy

- **Context:** `uploads/` exists with tracked `.gitkeep`; no retention policy defined.
- **Decision:** Server-generated filenames, local ephemeral storage, configurable retention, no third-party transmission, no training on uploads without opt-in, logs exclude image/text content by default.
- **Justification:** Privacy and security requirements.
- **Consequences:** Retention value must be decided by owner; cleanup mechanism needed in implementation.

## D-20 — Decoding

- **Context:** CTC output can be decoded greedily or with beam search.
- **Decision:** Greedy best-path decoding for baseline; beam search configurable and deferred.
- **Justification:** Deterministic, simple, CPU-friendly, easy to test.
- **Consequences:** Slightly lower accuracy potential on ambiguous lines.

## D-21 — Deferred capabilities

- **Context:** README and future-enhancement list mention several features.
- **Decision:** Defer full-page recognition, PDF support, multi-language support, mobile app, cloud deployment, attention/Transformer models, ONNX export, beam search/language model, and multi-instance scaling. Each requires a new approved milestone.
- **Justification:** Keeps scope bounded and avoids unimplemented claims.
- **Consequences:** No pre-built abstractions for these features will be added speculatively.

---

## Decision Change Log

| Date | Change |
|---|---|
| 2026-11-25 | Initial decision log created for Milestone 1; all entries PROPOSED pending owner approval. |
