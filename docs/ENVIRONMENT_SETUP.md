# Pen2Pixel — Environment Setup and Project Foundation

**Version:** 1.0 (Milestone 2)
**Date:** 2026-11-25
**Status:** Implementation complete; verification results appended after execution.

---

## 1. Python Version Decision

| Item | Finding |
|---|---|
| Preferred version | Python 3.11 (from milestone instructions) |
| Installed interpreters | Only CPython **3.13.2** at `C:\Users\likit\AppData\Local\Programs\Python\Python313\python.exe` (`py --list-paths` shows only `-V:3.13`) |
| Python 3.11 locations checked | `C:\Python311\python.exe`, `C:\Program Files\Python311\python.exe`, `C:\Users\likit\AppData\Local\Programs\Python\Python311\python.exe` — **all absent** |
| Legacy project venv | `handwriting-recognition\venv\` declares Python 3.11.9 but its interpreter path does not exist; the venv is **broken**, not working |
| PyTorch compatibility | PyPI metadata confirms `torch==2.15.0` has a `cp313` Windows wheel and declares `Requires-Python >=3.11` |

**Decision:** Use the available **Python 3.13.2** in a **new root-level `.venv`**. There is no working environment to preserve, installing a second Python version would be a large, unjustified system change, and the required ML stack has verified cp313 Windows wheels. The broken legacy venv is left untouched and remains gitignored; it must not be used.

If Python 3.11 is later installed by the owner, the pinned versions can be re-resolved and the same setup commands reused with that interpreter.

---

## 2. Dependency Strategy

Versions were checked against PyPI metadata for Python 3.13 / Windows before pinning. Runtime, development, and optional dependencies are separated.

### 2.1 Runtime — `handwriting-recognition/requirements.txt`

| Package | Version | Why included |
|---|---|---|
| torch | 2.15.0 | Confirmed ML framework; cp313 Windows wheel verified. |
| numpy | 2.3.3 | Required by PyTorch/OpenCV/preprocessing; cp313 wheel verified. |
| Pillow | 13.0.0 | Image decoding/encoding. |
| opencv-python-headless | 5.1.0.95 | Image processing without GUI dependencies; `cp37-abi3` wheel covers cp313. |
| PyYAML | 6.0.3 | YAML configuration loading; cp313 wheel verified. |
| fastapi | 0.156.8 | Confirmed backend framework. |
| uvicorn | 0.54.0 | ASGI server for FastAPI. |
| python-multipart | 0.0.22 | Multipart file uploads. |
| pydantic | 2.12.5 | FastAPI schemas; pydantic-core has cp313 wheels. |
| tqdm | 4.67.3 | Training progress reporting in later milestones. |

### 2.2 Development / test — `handwriting-recognition/requirements-dev.txt`

| Package | Version | Why included |
|---|---|---|
| pytest | 9.1.1 | Confirmed testing framework; configured in `pyproject.toml`. |
| httpx | 0.28.1 | Required by FastAPI's `TestClient` for later API tests. |

### 2.3 Optional — `handwriting-recognition/requirements-optional.txt`

| Package | Version | Why not installed by default |
|---|---|---|
| torchvision | 0.29.2 | Only needed by the optional EMNIST downloader; EMNIST is optional per decision D-07. Verified compatible with torch>=2.14 and has a Windows wheel. |
| pandas | 3.0.3 | Offline data analysis only, not needed for the running app or smoke tests. |
| matplotlib | 3.11.2 | Report/experiment plotting only. |
| scikit-learn | 1.8.0 | Deferred; baseline metrics are implemented directly without it (decision D-17). |

### 2.4 Explicitly excluded

`tensorflow-datasets`, `tensorflow`, `torchaudio`, `jupyter` — contradict the PyTorch-only decision, are unnecessary for handwriting line recognition, or belong to later optional workflows. This resolves the dependency inconsistency found in Milestone 0.

---

## 3. Fresh Setup Instructions (Windows PowerShell)

Run from the repository root (`Pen2Pixel`):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r handwriting-recognition/requirements.txt -r handwriting-recognition/requirements-dev.txt
```

Run the environment smoke tests:

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m pytest --collect-only -q
```

Optional extras, only when a later milestone needs them:

```powershell
.venv\Scripts\python.exe -m pip install -r handwriting-recognition/requirements-optional.txt
```

Do **not** use `handwriting-recognition\venv`; it points to a missing Python 3.11 installation.

---

## 4. Configuration Management

- Source of truth: `configs/default.yaml`.
- Loader: `handwriting-recognition/config/loader.py`.
- All paths are **relative to the repository root**; no machine-specific absolute paths are committed.
- `get_path(config, "paths.<key>")` resolves configured paths to absolute paths.
- Configuration is validated at load time (`ConfigError` on missing sections or invalid values).

### Configuration groups

| Group | Keys |
|---|---|
| `random` | `seed` |
| `device` | `auto` / `cpu` / `cuda` |
| `paths` | dataset, MNIST/IAM/EMNIST, model/checkpoint, upload, output and log directories |
| `logging` | level, format, console/file handlers, file name |
| `api` | host, port, config exposure, CORS origins, request timeout |
| `upload` | max bytes, allowed MIME types, max pixels, intensity variance, retention |
| `image` | min/max width and height |
| `preprocessing` | grayscale, denoise, binarization, deskew, target height, width cap, overflow policy, normalization range |
| `training` | batch size, learning rate, epochs, validation/checkpoint intervals, workers |
| `model` | architecture, vocabulary path, blank index |

### Environment variables

| Variable | Purpose |
|---|---|
| `PEN2PIXEL_CONFIG` | Path to an alternative YAML config file (relative to repo root or absolute). |
| `PEN2PIXEL__SECTION__KEY` | Override one nested key, e.g. `PEN2PIXEL__TRAINING__BATCH_SIZE=16`, `PEN2PIXEL__LOGGING__LEVEL=DEBUG`. Values are YAML-parsed so numbers/booleans/lists are typed correctly. |

`.env` files are deliberately **ignored and not auto-loaded**; setting variables in the shell avoids adding a dotenv dependency. Machine-specific overrides should use environment variables or an ignored `configs/*.local.yaml` file.

---

## 5. Project Structure Added

```text
Pen2Pixel/
├── .venv/                                  (ignored; new working environment)
├── .gitignore                              (updated)
├── pyproject.toml                          (pytest + ruff configuration)
├── configs/default.yaml                    (new)
├── docs/ENVIRONMENT_SETUP.md               (this file)
└── handwriting-recognition/
    ├── requirements.txt                    (updated: pinned runtime)
    ├── requirements-dev.txt                (new)
    ├── requirements-optional.txt           (new)
    ├── config/{__init__.py,loader.py}       (new package)
    ├── utils/{__init__.py,logging_config.py}(updated/new)
    ├── api/__init__.py                     (new)
    ├── backend/__init__.py                 (new)
    ├── dataset/__init__.py                 (new)
    ├── models/__init__.py                  (new)
    ├── preprocessing/__init__.py           (new)
    └── tests/{__init__.py,test_environment.py} (new)
```

All previously existing source placeholders were preserved unchanged. No dataset loader, model, training loop, API route, or frontend implementation was introduced in this milestone.

---

## 6. Development Standards

- **Type hints:** All new Python functions are annotated; `from __future__ import annotations` is used where needed.
- **Logging:** `utils.configure_logging(config)` creates an idempotent logger named `pen2pixel`; console/file output and level are config-driven.
- **Formatting/linting:** `pyproject.toml` contains Ruff settings (line length 100, `E`/`F`/`I` rules, Python 3.13 target). Ruff is not installed by default to avoid an unnecessary dependency; install it separately if desired.
- **pytest:** `pyproject.toml` sets `testpaths`, `pythonpath`, `addopts = "-ra --strict-markers"` and `minversion = "9.0"`.
- **.gitignore:** adds pytest/Ruff/mypy/coverage caches, logs, generated outputs, local config overrides, and `dataset/emnist/*.npz` (closing the gap found in M0).
- **No Docker, cloud, or CI infrastructure** was added.

---

## 7. Smoke Test Coverage

`handwriting-recognition/tests/test_environment.py` verifies:

1. All foundation packages import.
2. PyTorch CPU tensor arithmetic works.
3. A generated PNG is written by Pillow and decoded by OpenCV.
4. Default configuration loads and resolves paths.
5. Nested environment overrides are applied with correct types.
6. Invalid configuration raises `ConfigError`.
7. Logging initializes from config and is idempotent.

No test uses network access, a GPU, a dataset download, or a trained checkpoint.

---

## 8. Verification Results

All commands were run from the repository root with the new `.venv`.

| Command | Actual result |
|---|---|
| `python -m venv .venv` | Created successfully. `.venv\Scripts\python.exe --version` → `Python 3.13.2`; pip → `24.3.1`. |
| `.venv\Scripts\python.exe -m pip install -r handwriting-recognition/requirements.txt -r handwriting-recognition/requirements-dev.txt` | `Successfully installed` all pinned packages and their transitive dependencies (torch 2.15.0, numpy 2.3.3, opencv-python-headless 5.1.0.95, PyYAML 6.0.3, fastapi 0.156.8, uvicorn 0.54.0, python-multipart 0.0.22, pydantic 2.12.5, tqdm 4.67.3, pytest 9.1.1, httpx 0.28.1, plus dependencies). No unresolved conflicts. |
| `.venv\Scripts\python.exe -m pip check` | `No broken requirements found.` |
| Version/CUDA probe | `python 3.13.2`, `torch 2.15.0+cpu`, `numpy 2.3.3`, `cv2 5.1.0`, `Pillow 13.0.0`, `cuda_available False`. |
| `.venv\Scripts\python.exe -m pytest --collect-only -q` | `7 tests collected in 6.35s` — test discovery works. |
| `.venv\Scripts\python.exe -m pytest -q` (first run) | `3 passed, 4 failed` — a genuine bug in `validate_config`: scalar sections `version` and `device` were incorrectly required to be mappings. |
| Fix | Added `SCALAR_SECTIONS = {"version", "device"}` and restricted the mapping check to non-scalar sections. No test was weakened or removed. |
| `.venv\Scripts\python.exe -m pytest -q` (final run) | **`7 passed in 2.43s`** — full green suite. |

Verified smoke coverage: all foundation packages import; PyTorch CPU tensor arithmetic works; Pillow writes and OpenCV reads a generated PNG; default config loads and resolves paths; nested environment overrides apply with correct types; invalid config raises `ConfigError`; logging initializes and is idempotent.

No GPU acceleration is claimed: `torch.cuda.is_available()` returned `False`, and only CPU tensor operations were exercised. No dataset download, model code, or training was performed.

---

## 9. Known Limitations

- Python 3.11 was unavailable; the environment uses Python 3.13.2. If a dependency later lacks cp313 support, re-resolution with Python 3.11 will be required.
- `torch` on Windows may bundle CUDA libraries, but **no GPU acceleration is claimed or verified**; only CPU tensor operations are tested.
- Installed versions are pinned for this machine; fresh installs on another OS/architecture must re-check wheel availability.
- No dataset or model code exists yet; those remain later milestones.
