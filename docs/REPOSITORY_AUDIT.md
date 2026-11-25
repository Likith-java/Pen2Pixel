# Pen2Pixel — Milestone 0 Repository Audit

**Date:** 2026-11-25
**Scope:** Complete read-only reconnaissance of `C:\Users\likit\OneDrive\Desktop\Pen2Pixel`
**Role:** Senior Software Engineer / ML Architect / Technical Project Manager
**Constraint:** Inspection only. No features implemented, no dependencies installed, no datasets downloaded, no existing files modified/renamed/deleted, no commits or pushes.

---

## 1. Current Repository Structure

```text
Pen2Pixel/                                      (git root, branch main, clean)
├── .git/                                       Git metadata (not inspected in detail)
├── .gitignore                                  705 bytes — ignore rules (audited)
├── LICENSE                                     1,093 bytes — MIT, © 2026 Likith V Shetty
├── README.md                                   4,862 bytes — main documentation (audited)
├── Handwriting Prediction Using Machine Learning.pdf   4,158,533 bytes — IGNORED, local only
├── Handwriting_Recognition_Project_Report.docx            45,715 bytes — IGNORED, local only
├── docs/                                       NEW — deliverables of this milestone (untracked)
│   ├── REPOSITORY_AUDIT.md                     this report
│   └── PROJECT_STATUS.md                       milestone tracker
└── handwriting-recognition/                    code root (note: NOT named pen2pixel)
    ├── README.md                               140 bytes — 3-line project note
    ├── requirements.txt                        128 bytes — 12 unpinned packages
    ├── api/routes.py                           0 bytes — empty placeholder
    ├── backend/app.py                          0 bytes — empty placeholder
    ├── backend/inference.py                    0 bytes — empty placeholder
    ├── dataset/
    │   ├── download_emnist.py                  1,432 bytes — only real Python implementation
    │   ├── mnist/                              IGNORED — 4 verified IDX files (54,950,048 bytes)
    │   ├── iam/forms/                          empty directory
    │   └── iam/lines/                          empty directory
    ├── frontend/index.html                     0 bytes — empty placeholder
    ├── frontend/script.js                      0 bytes — empty placeholder
    ├── frontend/style.css                      0 bytes — empty placeholder
    ├── models/cnn_model.py                     0 bytes — empty placeholder
    ├── models/crnn_ctc_model.py                0 bytes — empty placeholder
    ├── models/saved/                           empty directory (IGNORED)
    ├── notebooks/                              empty directory
    ├── outputs/                                empty directory
    ├── preprocessing/augment.py                0 bytes — empty placeholder
    ├── preprocessing/preprocess.py             0 bytes — empty placeholder
    ├── reports/                                empty directory
    ├── static/                                 empty directory
    ├── templates/                              empty directory
    ├── uploads/.gitkeep                        0 bytes — tracked; other uploads ignored
    ├── utils/metrics.py                        0 bytes — empty placeholder
    └── venv/                                   1,497 files / ~23.4 MB — IGNORED, BROKEN (see §3)
```

Counts by area (excluding `.git/`): project files 19 / ~4.21 MB (dominated by the two ignored report documents), dataset files 5 / ~54.95 MB, venv files 1,497 / ~23.43 MB.

**No test directory, no tests, no `conftest.py`, no `pytest.ini` / `pyproject.toml` / `setup.cfg` / `tox.ini`, no YAML/JSON/TOML configuration, no CI configuration, and no Python package markers (`__init__.py`) exist anywhere in the project.**

---

## 2. Existing Implementation Inventory

Every source file was checked by byte length and file hash; none was assumed empty from its name.

| File | Size | Implementation? | Intended responsibility (from name/docs) | Assessment |
|---|---:|---|---|---|
| `handwriting-recognition/dataset/download_emnist.py` | 1,432 B | **Yes** | Download EMNIST `balanced` via torchvision, save train/test `.npz` | Only real code. Correct path resolution (`parent.parent/dataset/emnist`). Hard-coded: `split="balanced"`, `ToTensor()` transform, output filenames, 47-class claim in docstring. No seed, no error handling, no download confirmation/license note, no memory guard; materializes the entire dataset into Python lists then NumPy arrays. Starts a large download when executed (must not be run implicitly). Output `.npz` files are **not** covered by `.gitignore` (only `dataset/emnist/raw/` is). |
| `handwriting-recognition/backend/app.py` | 0 B | No | FastAPI application entrypoint | Empty. No routes, settings, or app object. |
| `handwriting-recognition/backend/inference.py` | 0 B | No | Model loading + prediction | Empty. Overlaps conceptually with `api/routes.py` and `models/*`. |
| `handwriting-recognition/api/routes.py` | 0 B | No | Python inference API routes | Empty. Overlaps with `backend/app.py`; unclear which layer owns HTTP routing. |
| `handwriting-recognition/models/cnn_model.py` | 0 B | No | CNN model definition | Empty. No architecture, no device handling. |
| `handwriting-recognition/models/crnn_ctc_model.py` | 0 B | No | CNN+BiLSTM+CTC model | Empty. Core requested architecture absent. |
| `handwriting-recognition/preprocessing/preprocess.py` | 0 B | No | Grayscale, threshold, denoise, normalize | Empty. |
| `handwriting-recognition/preprocessing/augment.py` | 0 B | No | Training augmentation | Empty. |
| `handwriting-recognition/utils/metrics.py` | 0 B | No | Metrics (e.g., CER/WER) | Empty. |
| `handwriting-recognition/frontend/index.html` | 0 B | No | Web UI markup | Empty. |
| `handwriting-recognition/frontend/style.css` | 0 B | No | Styling | Empty. |
| `handwriting-recognition/frontend/script.js` | 0 B | No | Upload/prediction client logic | Empty. No `package.json`; not a React app. |
| `handwriting-recognition/requirements.txt` | 128 B | Config | Dependency declaration | Unpinned; contains unnecessary/conflicting packages (§5). |
| `handwriting-recognition/README.md` | 140 B | Docs | Short project note | Minimal, no setup or architecture detail. |
| `handwriting-recognition/uploads/.gitkeep` | 0 B | Placeholder | Keeps uploads directory in git | Correct and intentional. |

**Conclusion:** there is effectively no application implementation. The repository is a documented scaffold with one utility script. No bugs can be attributed to source code that does not exist; the concrete design issues found are in the EMNIST script, dependency list, and documentation.

---

## 3. Environment Report

All values below were read from the live machine at audit time; nothing is inferred as verified where unavailable.

| Item | Observation |
|---|---|
| Working directory / repo root | `C:\Users\likit\OneDrive\Desktop\Pen2Pixel` |
| OS | Microsoft Windows 11 Home Single Language, version 10.0.26200, build 26200, 64-bit |
| CPU | 11th Gen Intel Core i3-1115G4 @ 3.00 GHz — 2 physical cores, 4 logical processors |
| RAM | 7.65 GB total; 0.65 GB free at time of measurement |
| Disk C: | 206.01 GB used, 31.12 GB free |
| System Python | 3.13.2 at `C:\Users\likit\AppData\Local\Programs\Python\Python313\python.exe` |
| Project virtualenv | `handwriting-recognition\venv\`, declares Python 3.11.9, `home = ...\Python311` |
| **Virtualenv health** | **BROKEN / unusable:** `C:\Users\likit\AppData\Local\Programs\Python\Python311\python.exe` does not exist; invoking the venv's `python.exe` fails with `No Python at ...Python311\python.exe`. `include-system-site-packages = false`. |
| Packages actually in venv | pip 24.0 and setuptools 65.5.0 only (two `dist-info` directories). No ML packages. |
| System-site relevant packages (global, not project venv) | fastapi 0.156.8, uvicorn 0.54.0, numpy 2.2.3, pandas 3.1.1, matplotlib 3.11.2, Pillow 13.0.0, pytest 9.1.1, pytest-asyncio 1.4.0, pytest-cov 7.1.0, PyYAML 6.0.2, jupyter_core 5.9.1, jupyter_client 8.10.0 |
| PyTorch | Not importable in system Python (`importlib.util.find_spec("torch")` → `False`); not present in venv. **Not installed anywhere checked.** |
| CUDA / GPU | `nvidia-smi` not found on PATH; no `CUDA*` / `NVIDIA*` environment variables. Because PyTorch is absent, CUDA capability is **not verified and cannot be claimed**. CPU-only operation is the only supportable assumption. |
| Python packaging | No `__init__.py`, no packaging metadata; modules are not an installable package (namespace imports would be incidental, not designed). |

Risk implication: with ~0.65 GB free RAM at measurement time and 31 GB free disk, large dataset downloads and model training on this machine are constrained; the broken venv must be resolved before any reproducible work.

---

## 4. Dataset Inventory

### MNIST — `handwriting-recognition/dataset/mnist/` (present locally, gitignored)

| File | Bytes | Magic (big-endian) | Dimensions / count | Structural check |
|---|---:|---|---|---|
| `train-images.idx3-ubyte` | 47,040,016 | 2051 (3-D images) | 60,000 × 28 × 28 | Expected `16 + 60000·28·28 = 47,040,016` — exact match |
| `train-labels.idx1-ubyte` | 60,008 | 2049 (1-D labels) | 60,000 | Expected `8 + 60000 = 60,008` — exact match; labels ∈ [0,9], all digits 0–9 present |
| `t10k-images.idx3-ubyte` | 7,840,016 | 2051 | 10,000 × 28 × 28 | Expected `16 + 10000·28·28 = 7,840,016` — exact match |
| `t10k-labels.idx1-ubyte` | 10,008 | 2049 | 10,000 | Expected `8 + 10000 = 10,008` — exact match; labels ∈ [0,9], all digits 0–9 present |

- Files are **uncompressed/extracted IDX**, not gzip archives (no `.gz` extension; headers parsed successfully).
- Both training (60,000) and test (10,000) splits are present and separately stored — no evidence of split commingling.
- No checksums, provenance manifest, or license/attribution file accompanies the data. README points to a Kaggle MNIST source; that claim is documentation only and was not independently verified (no network access used).
- These files are ignored by git and therefore are **not** part of the repository clone.

### IAM — `handwriting-recognition/dataset/iam/`

Only two empty directories exist: `forms/` and `lines/`. **No IAM data, annotations, license file, or split definitions are present.** Nothing was downloaded.

### EMNIST — `handwriting-recognition/dataset/emnist/`

**Directory does not exist.** Only the downloader script is tracked. No EMNIST data or `.npz` arrays are present. Nothing was downloaded.

---

## 5. Dependency Assessment

Declared in `handwriting-recognition/requirements.txt` (12 lines, no version pins):

`torch`, `torchvision`, `torchaudio`, `tensorflow-datasets`, `opencv-python`, `numpy`, `pandas`, `matplotlib`, `jupyter`, `fastapi`, `uvicorn`, `Pillow`

| Category | Packages | Assessment |
|---|---|---|
| Required for confirmed stack | torch, torchvision, opencv-python, numpy, Pillow, fastapi, uvicorn | Appropriate to the confirmed decisions (PyTorch, OpenCV/Pillow/NumPy, FastAPI). |
| Plausible but must be justified | pandas, matplotlib, jupyter | Useful for data analysis/experimentation; dev-only tooling should be separated from runtime requirements. |
| Unnecessary / conflicting | **tensorflow-datasets**, **torchaudio** | `tensorflow-datasets` pulls in TensorFlow-family dependencies and contradicts the confirmed PyTorch-only ML framework decision and CPU/RAM constraints. `torchaudio` has no role in handwriting recognition. |
| Missing | **pytest** (confirmed testing tool), config support (e.g., PyYAML if YAML configs are adopted), `python-multipart` (FastAPI upload handling), `pydantic`/schema tooling as needed | `pytest` is installed globally on this machine but is not declared in project requirements; a fresh venv would lack it. |
| Reproducibility | None pinned | No versions or ranges → non-reproducible installs; already visible as drift between declared PyTorch stack (absent) and globally installed packages. |
| Location | `handwriting-recognition/requirements.txt` | README instructs `pip install -r requirements.txt` from the repository root, where no such file exists. |

No installation was performed. No version conflict can be empirically confirmed because the declared packages are not installed in the project environment.

---

## 6. Documentation Inconsistencies

Source: root `README.md` (236 lines), `handwriting-recognition/README.md` (3 lines), `.gitignore`, `requirements.txt`, `LICENSE`.

1. **Wrong stack described.** README says React frontend + Node.js/Express backend + Multer; confirmed decisions and scaffold are Python + FastAPI + plain HTML/CSS/JS. `npm install` / `npm run dev` / `npm start` instructions in README cannot work (no `package.json` anywhere).
2. **Malformed clone URL.** `git clone [https://github.com/Likith-java/Pen2Pixel.git]]` is invalid syntax.
3. **Wrong directory names.** README says `cd pen2pixel` and shows a `pen2pixel/` tree, but the folder is `Pen2Pixel/` and code lives in `handwriting-recognition/`.
4. **Wrong requirements path.** README's `pip install -r requirements.txt` assumes root-level requirements; the file is inside `handwriting-recognition/`.
5. **Project structure drift.** README lists `dataset/emnist/` implicitly nowhere in the tree but references it in dataset instructions; lists `frontend/index.html` etc. as if implemented; omits `LICENSE`, `.gitignore`, `venv`, `reports/`, `outputs/`, `static/`, `templates/`.
6. **Implementation claims unsupported.** Model architectures, preprocessing pipeline, features ("upload", "real-time prediction", "copy/download text"), and training commands are documented as present; all corresponding source files are 0 bytes. No model checkpoints exist.
7. **README internal contradiction.** Overview says "TensorFlow/PyTorch"; confirmed decision is PyTorch only, and `tensorflow-datasets` in requirements reinforces the ambiguity.
8. **Dataset licensing/attribution absent.** MNIST source link is given, but no license/attribution notes for MNIST, IAM (registration/license required), or EMNIST; EMNIST script downloads silently with no consent step.
9. **Project README is a stub**, giving no setup, architecture, testing, or dataset guidance.
10. **Report documents** (PDF/DOCX) remain locally but were deleted from git; README does not reference them consistently.

No documentation was rewritten during this milestone.

---

## 7. Git Health Assessment

- **Branch:** `main`, tracking `origin/main`, no ahead/behind divergence reported; `HEAD = c1a5d30c936...`.
- **Status at start of audit:** clean — `git status --porcelain=v1 --untracked-files=all` produced no output.
- **Status at end of audit:** no tracked file changed; no commit, reset, stash, fetch, pull, or push performed. The only new paths are the two untracked deliverables in `docs/`, which necessarily appear as `?? docs/`. The commit graph and tracked bytes are unchanged.
- **History:** 12 commits, 22–24 July 2026; authors Likith V Shetty (10) and Preetham V K (2). Work to date is scaffolding, cleanup, and README iterations.
- **Tracked files (18):** `.gitignore`, `LICENSE`, `README.md`, `handwriting-recognition/README.md`, `requirements.txt`, `dataset/download_emnist.py`, `uploads/.gitkeep`, and the 10 empty source/placeholder files.
- **Largest tracked file:** `README.md` (4,862 bytes). **No large file or dataset is tracked** — MNIST IDX files and the venv are correctly ignored.
- **`.gitignore` review:** ignores PDF/DOCX/ODT, `__pycache__`, byte-compiled and shared-object files, `venv/`/`.venv/`/`env/` and `.env`, IDE and OS files, `dataset/mnist/`, `dataset/iam/`, `dataset/emnist/raw/`, `models/saved/`, notebook checkpoints, and `uploads/*` with `!uploads/.gitkeep`.
  - **Gap:** `dataset/emnist/*.npz` produced by `download_emnist.py` is **not** ignored; a future run could stage large generated arrays accidentally.
  - Historical note: the deleted PDF and DOCX remain in git history; deletion from HEAD does not purge history.
- **Licensing:** `LICENSE` is MIT, copyright Likith V Shetty (2026). Third-party dataset terms are not documented in-repo.

---

## 8. Missing Components

1. All application implementation: preprocessing, CNN, CRNN+CTC, metrics, API, inference, frontend.
2. Configuration system: no YAML/TOML/JSON config, no settings class, no seed configuration.
3. Reproducibility: no random-seed utility, no dependency pins, no provenance/checksum manifest for datasets.
4. Testing: no tests, no test directory, no pytest configuration.
5. Packaging: no `__init__.py`, no `pyproject.toml`, no installable package, no CLI entry points.
6. Model artifacts: no checkpoints in `models/saved/`; no training/inference separation implemented.
7. Datasets: IAM absent (only empty dirs), EMNIST absent, no data license/attribution files, no train/val/test split manifests for IAM.
8. Frontend toolchain: no `package.json`/build config; no React project despite documentation.
9. Operational: no dev/test requirements split, no CI, no logging setup, no error-handling conventions, no API schemas, no `.gitattributes` for large/binary files.
10. Working environment: functional project virtualenv with the declared dependencies.

---

## 9. Technical Risks (prioritized)

| Priority | Risk | Impact |
|---|---|---|
| P0 | Broken virtualenv (missing Python 3.11 interpreter) and no PyTorch installed | No reproducible development or training is possible until fixed. |
| P0 | Zero implemented source code despite extensive documentation | Every downstream milestone depends on foundation work that does not exist; doc claims are misleading. |
| P0 | No tests and no pytest declared in requirements | Regressions and correctness cannot be verified. |
| P1 | No config/seed/pinned dependencies | Results and environments are not reproducible; hard-coded values will proliferate as code is added. |
| P1 | Hardware limits: 2 cores, 7.65 GB RAM (0.65 GB free observed), 31 GB free disk, no verified CUDA | CPU-first training must be carefully scoped; full EMNIST materialization (~hundreds of MB in RAM) and IAM downloads may fail or be slow. |
| P1 | Dataset licensing/attribution and silent large downloads (EMNIST script) | Compliance and consent concerns; unbounded, unconfirmed network usage. |
| P1 | `.gitignore` gap for `dataset/emnist/*.npz` | Generated multi-hundred-MB arrays could be committed accidentally. |
| P1 | Ambiguous API layer (`api/routes.py` vs `backend/app.py`) and contradictory frontend stack docs | Architectural confusion and duplicated responsibilities in upcoming milestones. |
| P2 | IAM/EMNIST absent; no split manifests | Primary sequence-recognition dataset work is blocked until acquisition and licensing are resolved. |
| P2 | Unpinned/unnecessary dependencies (`tensorflow-datasets`, `torchaudio`) | Install fragility, longer setup, conflicting framework expectations. |
| P2 | Deleted report documents remain in git history and locally | Potential stale/duplicated documentation; history cleanup requires explicit approval. |

---

## 10. Prioritized Recommendations

1. **(P0, next milestone)** Establish the foundation: recreate a working Python environment compatible with the available interpreter, pin dependencies, split runtime/dev requirements, add pytest, add a minimal config module and seed utility, and add package markers — with no dataset downloads.
2. **(P0)** Define and agree the module boundaries (`config/`, `data/`, `preprocessing/`, `models/`, `inference/`, `api/`) and settle the API-layer duplication before implementing features.
3. **(P0)** Add the first smoke tests (config loading, seed determinism, IDX parser) and run them in the next milestone before any model code.
4. **(P1)** Fix `.gitignore` to cover `dataset/emnist/*.npz` and all generated outputs; add attribution/license notes for each dataset before acquisition.
5. **(P1)** Write an IDX/MNIST dataset loader with explicit split handling and a leakage guard, using the already-present local MNIST files (no downloads).
6. **(P1)** Resolve the IAM acquisition/licensing question with the project owner; treat EMNIST as optional and justify it against CPU/RAM limits before enabling its downloader.
7. **(P1)** Reconcile README with the confirmed Python/FastAPI/plain-JS stack and actual paths; document missing functionality honestly rather than as shipped.
8. **(P2)** Remove unnecessary dependencies (`tensorflow-datasets`, `torchaudio`) and dev-only tools from runtime requirements; add CI only after tests exist.
9. **(P2)** Decide explicitly whether to purge historical report documents (requires approval; rewrites history).

---

## Acceptance Criteria Status

| Criterion | Status | Evidence |
|---|---|---|
| Existing files inspected | PASS | All root and project files listed; every source file checked by size/hash; root README, project README, `.gitignore`, `LICENSE`, requirements, and EMNIST script read in full. |
| No existing implementation overwritten | PASS | Only two new files created under `docs/`; no existing file written. |
| Dataset presence verified, not assumed | PASS | IDX magic numbers, dimensions, byte lengths, and label ranges verified; IAM dirs checked empty; EMNIST directory confirmed absent. |
| Environment details factual | PASS | Values read from OS/CIM, `python --version`, `pip list`, `find_spec`, venv `pyvenv.cfg`; CUDA explicitly reported as unverified. |
| Documentation gaps identified | PASS | 10 inconsistencies documented in §6. |
| Git status remains unchanged | PASS (with note) | Tracked tree and commit graph unchanged; no git write operations. New untracked `docs/` deliverables are required by this milestone and are disclosed. |
| Audit report generated successfully | PASS | `docs/REPOSITORY_AUDIT.md` and `docs/PROJECT_STATUS.md` created. |

**Milestone 0 is complete pending your review and approval. Milestone 1 has not been started.**

---

## Appendix — Commands Executed (read-only)

- `git status --short --branch`, `git status --porcelain=v1 --untracked-files=all`, `git status --ignored --short`
- `git log --oneline --decorate -20`, `git log --format=... --reverse`, `git log -1 --format=...`, `git branch -vv`, `git remote -v`, `git ls-files`, `git ls-files -s`
- `Get-ChildItem` recursive listings (files, directories, sizes, hidden files); `Get-FileHash` on source files; `Get-Content` on README files, `.gitignore`, `LICENSE`, `requirements.txt`, `download_emnist.py`, `pyvenv.cfg`
- Python standard-library IDX parser (`struct`, `os`) validating headers/lengths/label ranges; `importlib.util.find_spec` for torch/numpy/pytest
- CIM/OS queries for OS, CPU, RAM, disk; `Get-Command nvidia-smi`; environment-variable scan for CUDA/NVIDIA
- Two `write` operations creating `docs/REPOSITORY_AUDIT.md` and `docs/PROJECT_STATUS.md` (new files only)
