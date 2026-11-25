# Pen2Pixel — Product and System Requirements

**Version:** 1.0 (Milestone 1 — proposed, pending owner approval)
**Date:** 2026-11-25
**Basis:** `docs/REPOSITORY_AUDIT.md` (Milestone 0), confirmed technical decisions, and user-provided problem statement.
**Status:** All requirements below are **PROPOSED** until approved. No implementation existed at the time of writing; nothing in this document describes shipped behaviour.

---

## 1. Product Definition

### 1.1 Problem statement

Users who have handwritten notes in image form cannot edit, search, copy, or archive that text without manually retyping it. Manual transcription is slow and error-prone. Pen2Pixel must convert a **handwritten English text-line image** into editable digital text through a machine-learning recognition pipeline exposed via a simple web interface.

### 1.2 Objectives

| ID | Objective |
|---|---|
| O1 | Accept a single handwritten text-line image through a web UI and API. |
| O2 | Validate and preprocess the image deterministically and reproducibly. |
| O3 | Recognize the line with a CNN + BiLSTM + CTC model running CPU-first. |
| O4 | Present the recognized text in an editable form that can be copied or downloaded. |
| O5 | Keep training, evaluation, inference, API, and UI concerns separated and testable. |
| O6 | Establish a foundation that can later extend to full-page recognition without redesigning the API contract. |

### 1.3 Target users

| User | Need |
|---|---|
| Student / researcher | Quickly transcribe handwritten notes, annotations, or snippets. |
| Office / knowledge worker | Convert scanned handwritten lines into editable text for documents. |
| Developer / integrator | Call a simple HTTP API to add recognition to another tool. |
| Project owner / maintainer | Reproducible, testable code that can be trained and evaluated on commodity CPU hardware. |

### 1.4 Explicitly out of scope for the baseline

- Full-page, paragraph, or multi-line recognition (future extension only).
- Handwriting generation, signature verification, language translation.
- Multi-language recognition, PDF ingestion, OCR of printed text as a separate mode.
- Model training or dataset downloads triggered by end-user requests.
- Any claim of measured accuracy, latency, or GPU acceleration (none has been measured).

---

## 2. Core User Journey

| Step | Actor | Action | System response / requirement |
|---:|---|---|---|
| 1 | User | Opens Pen2Pixel | Frontend loads; displays supported formats, configurable size/dimension limits fetched from the API (or injected config), and an upload control. |
| 2 | User | Uploads a handwritten text-line image | Frontend performs basic client-side validation and shows a preview; server performs authoritative validation. |
| 3 | System | Validates the image | File type, size, dimensions, decodability, and non-empty content checked against configuration; structured error returned on failure. |
| 4 | System | Preprocesses the image | Grayscale conversion, denoising, binarization/thresholding, deskew (configurable), normalization to target height, aspect-ratio-preserving width scaling, padding/mask preparation. |
| 5 | System | Runs recognition | Loaded model produces frame-wise logits; configurable decoding yields text. |
| 6 | System | Displays result | Recognized text returned as JSON and rendered in an editable text area. |
| 7 | User | Edits the text | Frontend text area is fully editable; no server call required for editing. |
| 8 | User | Copies or downloads output | One-click copy to clipboard and download as a UTF-8 `.txt` file, entirely client-side. |

---

## 3. Functional Requirements

All numeric limits in this section are **configuration values with proposed starter defaults**, not measured service-level objectives. They must live in a configuration file and be validated against real data and hardware before being considered final.

### 3.1 Upload and input validation

| ID | Requirement | Config key | Proposed starter value (validate) |
|---|---|---|---|
| FR-01 | Accepted formats: PNG and JPEG in the baseline. Additional formats (BMP/TIFF/WebP) only via configuration after testing. | `upload.allowed_mime_types` | `["image/png", "image/jpeg"]` |
| FR-02 | Maximum upload size enforced by both client and server. | `upload.max_bytes` | 10 MiB |
| FR-03 | Decoded image dimensions bounded: minimum and maximum width and height. | `image.min_width_px`, `image.max_width_px`, `image.min_height_px`, `image.max_height_px` | 64 / 4096 / 16 / 1024 px |
| FR-04 | Reject files that cannot be decoded by Pillow/OpenCV, that are empty, or that exceed a configured pixel-count ceiling. | `image.max_pixels` | 4,000,000 px |
| FR-05 | Validate MIME type and content signature (not extension alone); reject polyglot/corrupt files. | — | Always on |
| FR-06 | Reject entirely blank or single-colour images using a configurable variance threshold. | `image.min_intensity_variance` | To be calibrated |
| FR-07 | Uploaded files are written to a configured temporary/upload directory with a server-generated name; original filename is never used as a path. | `paths.upload_dir` | `handwriting-recognition/uploads` |
| FR-08 | Uploaded files are removed after processing or after a configurable retention period. | `upload.retention_seconds` | To be decided with owner (privacy) |
| FR-09 | Limits are exposed to the frontend through config/API so client and server agree; client validation is advisory only. | `api.expose_limits` | `true` |

### 3.2 Preprocessing requirements

| ID | Requirement | Config key |
|---|---|---|
| FR-10 | Convert to grayscale deterministically. | `preprocessing.grayscale` |
| FR-11 | Denoise with a configurable method (e.g., median or bilateral filter). | `preprocessing.denoise.method`, `.kernel_size` |
| FR-12 | Binarize with a configurable method (Otsu or adaptive threshold). | `preprocessing.binarization.method`, `.block_size`, `.constant` |
| FR-13 | Optional deskew with a configurable enable flag and angle limit. | `preprocessing.deskew.enabled`, `.max_angle_degrees` |
| FR-14 | Normalize to a fixed target height while preserving aspect ratio; never stretch width. | `preprocessing.target_height_px` |
| FR-15 | Cap resulting width at a configured maximum; reject or clearly report over-long lines rather than silently truncating. | `preprocessing.max_output_width_px`, `preprocessing.on_overflow` |
| FR-16 | Normalize pixel values to a configured range and produce a binary padding mask. | `preprocessing.normalization_range` |
| FR-17 | The same preprocessing code path is used in training, evaluation, and inference (no train/serve skew). | — (architectural rule) |
| FR-18 | Preprocessing steps are individually configurable and unit-testable with synthetic images. | — |

### 3.3 Recognition workflow

| ID | Requirement |
|---|---|
| FR-19 | Recognize exactly **one handwritten English text line** per request in the baseline. |
| FR-20 | Model input is a greyscale, height-normalized, variable-width tensor with an explicit length/mask. |
| FR-21 | Output is text plus metadata (see FR-28); no side effects on the filesystem other than controlled upload handling. |
| FR-22 | Model and device selection are configuration-driven; default device is CPU with device-aware fallback. |
| FR-23 | If no trained checkpoint is available, the API must return an explicit, typed "model unavailable" error — never a fabricated prediction. |
| FR-24 | Inference must not trigger training or dataset downloads. |
| FR-25 | Multiple concurrent requests are handled without sharing mutable preprocessing/model state. |

### 3.4 Editable output, copy, and download

| ID | Requirement |
|---|---|
| FR-26 | Frontend displays recognized text in an editable text area; user edits are preserved during copy/download. |
| FR-27 | Copy uses the Clipboard API with a graceful fallback for insecure contexts. |
| FR-28 | Download writes the current edited text as UTF-8 `.txt` with a generated filename; no server round trip. |
| FR-29 | The UI clearly labels recognized text as machine-generated and may be incorrect. |

### 3.5 Error handling

| ID | Requirement |
|---|---|
| FR-30 | All errors return a consistent JSON envelope: `error.code`, `error.message`, `error.details` (optional), and `request_id`. |
| FR-31 | Client errors (invalid type/size/dimensions/blank image) map to 4xx; server/config/model faults map to 5xx. |
| FR-32 | Internal stack traces, paths, and secrets are never returned to clients; they are logged server-side with the request ID. |
| FR-33 | Client-side validation errors are shown inline before upload where possible; server errors are shown without losing the uploaded preview or edited text. |
| FR-34 | A typed exception hierarchy separates validation, preprocessing, model-loading, inference, and configuration errors. |

### 3.6 API requirements

| ID | Requirement |
|---|---|
| FR-35 | FastAPI application built via an app factory; routers live in the API layer, not in the model code. |
| FR-36 | `GET /health` — liveness plus loaded-model/config status; no dataset access. |
| FR-37 | `GET /api/v1/config` — returns non-sensitive, client-relevant limits (FR-09). |
| FR-38 | `POST /api/v1/recognize` — multipart form with one image file; returns recognized text and metadata. |
| FR-39 | Request/response schemas are explicit and versioned under `/api/v1`. |
| FR-40 | Recognition response fields: `text`, `request_id`, `model_id`, `elapsed_ms` (measured, not estimated), `warnings` (list). Any confidence field is included only if the model actually produces one. |
| FR-41 | API does not expose training endpoints, checkpoint paths, or dataset contents. |
| FR-42 | CORS, trusted-host, and upload limits are configuration-driven. |

### 3.7 Frontend requirements

| ID | Requirement |
|---|---|
| FR-43 | Plain HTML, CSS, and JavaScript in `frontend/`; no build step or framework dependency in the baseline. |
| FR-44 | Static files served by the same FastAPI application (single-origin deployment). |
| FR-45 | Shows upload control, image preview, validation messages, progress/disabled state during request, editable result, copy, and download controls. |
| FR-46 | Accessible basics: labelled controls, keyboard reachability, visible error text, alt text for preview. |
| FR-47 | No fake demo predictions or hard-coded sample results may be displayed as real model output. If no model is available, the UI shows the server's explicit error. |

---

## 4. Non-Functional Requirements

> **No numeric service-level objectives are asserted.** Every "target" below is a design intent that must be measured and agreed by the owner before becoming an SLO. No latency, accuracy, uptime, or throughput numbers are claimed.

| ID | Area | Requirement / target requiring measurement |
|---|---|---|
| NFR-01 | Reliability | Deterministic behaviour for a given config, seed, model checkpoint, and input; failures are explicit and typed; no silent fallbacks that fabricate results. |
| NFR-02 | Reliability | Target: acceptable error rate under valid inputs — **to be measured** on a held-out set before any claim. |
| NFR-03 | Maintainability | Modular boundaries (data, preprocessing, models, training, evaluation, inference, API, UI); type hints; docstrings for public functions; no duplicated responsibility between `api/` and `backend/`. |
| NFR-04 | Maintainability | All paths, limits, and hyperparameters from config; no hard-coded absolute paths. |
| NFR-05 | Performance | CPU-first execution with device-aware tensors; target inference latency and memory footprint **to be measured** on the audited hardware (2 cores, 7.65 GB RAM). |
| NFR-06 | Performance | Avoid unnecessary full-image copies; stream uploads to disk; batch size and worker count configurable. |
| NFR-07 | Security | Validate content type and size before decoding; cap pixel count to reduce decompression-bomb risk; never trust filenames or client-reported MIME types alone. |
| NFR-08 | Security | No path traversal (server-generated filenames only), no arbitrary file reads, no secrets in config responses or logs. |
| NFR-09 | Security | Dependency versions pinned and reviewed; unnecessary frameworks removed to reduce attack surface. |
| NFR-10 | Reproducibility | Single config file as source of truth; fixed seeds for Python, NumPy, and PyTorch; checkpoint records config hash and dependency versions. |
| NFR-11 | Reproducibility | Dataset splits recorded in a manifest; test set never used for tuning; no result reported without the exact config/checkpoint that produced it. |
| NFR-12 | Testability | pytest suites for validation, preprocessing, model shape/CTC behaviour, metrics, config loading, and API endpoints using synthetic data and a stub model. |
| NFR-13 | Testability | No test may require a network download, a GPU, or a real trained checkpoint. |
| NFR-14 | CPU compatibility | All code runs on CPU by default; CUDA used only when explicitly available and verified; no GPU-only ops. |
| NFR-15 | Privacy | Uploaded images are processed locally and not sent to third-party services; retention is configured and documented; no training on user uploads without explicit opt-in. |
| NFR-16 | Privacy | Logs contain request IDs and error classes, not image contents or recognized personal text by default. |
| NFR-17 | Scalability | Stateless API design so instances can be added later; model loaded once per process; upload storage abstracted behind configured directory. |
| NFR-18 | Scalability | Future full-page support must be additive (new pipeline mode), not a rewrite of the API contract. |
| NFR-19 | Compliance | Dataset licenses and attribution recorded before any dataset is acquired; IAM access follows its registration terms. |
| NFR-20 | Observability | Structured logs with request IDs and measured timings; health endpoint reports config/model state without exposing internals. |

---

## 5. ML Requirements

### 5.1 Recognition task

| ID | Requirement |
|---|---|
| MLR-01 | Primary task: **offline handwritten English text-line recognition** — one cropped line image → one text string. |
| MLR-02 | **Character recognition is distinct from line recognition.** Character-level classification (single glyph) is a supporting learning task, not the product output. |
| MLR-03 | Full-page recognition (layout analysis + line segmentation) is explicitly deferred. |
| MLR-04 | No acceptance metric may be reported until an actual trained checkpoint and held-out evaluation exist. |

### 5.2 Character vocabulary and CTC blank

| ID | Requirement |
|---|---|
| MLR-05 | Vocabulary is configuration-driven and derived from the licensed training transcripts before training; it is **not assumed** from memory. |
| MLR-06 | Proposed baseline vocabulary: uppercase `A–Z`, digits `0–9`, space, and a small punctuation set (`. , ' -`). Exact symbols and any lowercase handling must be verified against IAM transcripts and recorded in config. |
| MLR-07 | Baseline normalizes transcript case to a single configured case (uppercase proposed) to reduce class ambiguity; a config flag controls this. |
| MLR-08 | A dedicated **CTC blank token** is appended to the vocabulary and excluded from decoded text. Its index is configuration-derived, not hard-coded. |
| MLR-09 | Unknown/out-of-vocabulary characters are handled explicitly (configurable mapping or rejection); no silent substitution presented as exact recognition. |

### 5.3 Input representation and variable-width handling

| ID | Requirement |
|---|---|
| MLR-10 | Greyscale single-channel image, height normalized to a configured value, width scaled proportionally and capped. |
| MLR-11 | Variable-width sequences are supported by padding to the batch maximum and supplying true input lengths / padding masks to CTC and the BiLSTM. |
| MLR-12 | Padding values and masks are deterministic; padded columns never contribute to the loss or decoded output. |
| MLR-13 | Pixel normalization range is configured and identical across train/eval/inference. |

### 5.4 Model, output, and decoding

| ID | Requirement |
|---|---|
| MLR-14 | Proposed baseline: CNN feature extractor → bidirectional LSTM → linear projection to vocabulary + blank. |
| MLR-15 | Model output is a sequence of per-frame log probabilities over vocabulary + blank, plus the true input length. |
| MLR-16 | Baseline decoding: greedy CTC (best path, blank collapse). Beam search with configurable width is an optional later enhancement, not required for baseline. |
| MLR-17 | Decoded text is plain UTF-8; any confidence value must come from measured model output and be labelled as such. |
| MLR-18 | Model implementation is device-aware (`cpu`/`cuda` selected by config and availability); CUDA is never claimed unless verified. |

### 5.5 Training requirements

| ID | Requirement |
|---|---|
| MLR-19 | Training code is separate from inference and API code; it consumes prepared splits from a manifest. |
| MLR-20 | Seeds fixed for Python, NumPy, and PyTorch; seed recorded with each checkpoint. |
| MLR-21 | Dataset roles: **MNIST** = supporting character-level learning and pipeline validation (local IDX files already verified); **IAM** = primary line-recognition dataset (absent; license/access required); **EMNIST** = optional, only if justified by a documented need for a larger character set and after resource review. |
| MLR-22 | Train/validation/test splits defined at the **writer/line-group level** with no overlap; test set used only for final evaluation. |
| MLR-23 | Checkpoints store model state, config hash, vocabulary, seed, and dependency versions; resumable training required. |
| MLR-24 | Training on this machine is CPU-first with resource-aware batch sizes; no dataset download is implicit or silent. |
| MLR-25 | Augmentation is configured and applied only to training data. |

### 5.6 Evaluation metrics

| ID | Requirement |
|---|---|
| MLR-26 | Primary metric: **Character Error Rate (CER)** using edit distance over characters. |
| MLR-27 | Secondary metrics: **Word Error Rate (WER)** and exact-line accuracy. |
| MLR-28 | Metrics computed by shared, unit-tested utility code; no metric value is reported without the config, checkpoint, and split manifest that produced it. |
| MLR-29 | Evaluation report includes dataset split sizes and excludes test data from any tuning decision. |

### 5.7 Baseline limitations (documented, not defects to hide)

- CTC assumes monotonic alignment between image frames and transcript; overlapping/cursive strokes can violate this.
- Conditional independence between predictions limits linguistic correction; no language model is included in the baseline.
- Long lines increase sequence length, memory use, and error accumulation; a configured max width is required.
- Case and punctuation may be ambiguous in handwriting; baseline case folding reduces but does not eliminate this.
- Performance depends on the quantity and quality of licensed IAM line data, which is not yet present.
- CPU training on 2 cores / 7.65 GB RAM is expected to be slow; no speed or accuracy figure is claimed.
- The model recognizes lines, not pages; full-page support requires future layout segmentation.

---

## 6. Dataset Role Definition

| Dataset | Role | Current state (from M0 audit) | Action before use |
|---|---|---|---|
| MNIST | Supporting character-level learning; IDX parser/pipeline validation; smoke tests. | Present locally, 60k train / 10k test IDX files, structurally verified, gitignored. | Use existing local files; no download; record source/attribution. |
| IAM | Primary supervised source for text-line recognition. | Absent — only empty `dataset/iam/forms/` and `dataset/iam/lines/`. | Resolve license/registration, obtain data, record attribution and split manifest; explicit owner approval before acquisition. |
| EMNIST | Optional supporting character data. | Absent — directory does not exist; only downloader script present. | Justify need vs. CPU/RAM cost, add explicit opt-in and license note, fix memory usage and `.gitignore` gap before use. |

---

## 7. Acceptance Criteria Traceability

| Milestone 1 criterion | Covered by |
|---|---|
| Recognition scope explicitly defined | §1.4, §3.3, MLR-01–04 |
| Character vs line recognition distinguished | MLR-01–03, §6 |
| Dataset roles defined | §6, MLR-21 |
| API and UI responsibilities clear | §3.5–3.7, FR-35–47 |
| Architecture documented | `docs/ARCHITECTURE.md` |
| No implementation code added | This milestone produced documentation only; verified by git status. |
