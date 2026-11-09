# Reproduction Guide

This repository supports two scopes of reproduction:

1. **Replaying the paper from the released data** (sections 1–3). Every number and figure of the
   paper is recomputed from `data/` on any machine, with no GPU and no OCR engine, in about one
   minute. This is the scope a reviewer needs.
2. **Re-reading the documents with the three engines** (section 4). This needs the confidential
   source PDFs, which are not distributed with this repository, plus Tesseract, EasyOCR and
   SmolVLM. It rebuilds `data/callouts/channel_reads.csv`; section 1 then rebuilds everything
   downstream of it.

## External projects, data and licences

| Component | Purpose | How to obtain |
| --- | --- | --- |
| [Tesseract OCR 4.1](https://github.com/tesseract-ocr/tesseract) | Channel 1: LSTM character recogniser | System package (`apt install tesseract-ocr`, or the Windows installer); observe its Apache-2.0 licence |
| [EasyOCR 1.7](https://github.com/JaidedAI/EasyOCR) | Channel 2: CRAFT detector + CRNN recogniser | `pip install easyocr==1.7.2`; downloads its models on first use |
| [SmolVLM-256M-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct) | Channel 3: vision-language model | Download the snapshot locally; observe the model card |
| Poppler (`pdftoppm`) | Rendering source PDFs at 100–300 dpi | `apt install poppler-utils`, or the Windows build |
| Source problem sheets `FE-00xx.pdf` | The documents that were read | **Not distributed** — governed by the plant's data-use agreement (`docs/data-compliance.md`) |

Sections 1–3 need none of these.

## Reference environment

| Category | Validated version / requirement |
| --- | --- |
| OS and Python | Linux, macOS or Windows; Python 3.9–3.12 (validated with 3.10) |
| Replay | `numpy>=1.24`, `pandas>=1.5`, `matplotlib>=3.7`, `opencv-python-headless>=4.8`, `pillow>=9`, `pytest>=7` (see `requirements.txt`) |
| Re-reading (section 4) | Tesseract 4.1, `easyocr==1.7.2`, `torch`, `transformers>=4.46`, `pytesseract`, `pdfplumber`, Poppler; CPU is enough (the paper's timings use two CPU threads) |

## 1. Replay from the released data

```bash
git clone https://github.com/JHou-TongJi/AEGIS-agree-then-commit.git
cd AEGIS-agree-then-commit
python -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
bash reproduce.sh                    # Windows: run it in Git Bash
python -m pytest tests               # expect all tests to pass
```

`reproduce.sh` runs the fifteen analysis scripts (`scripts/a*.py`, which write `results/`) and the
twelve figure scripts (`figures/fig*.py`, which write `figures/png/`). It does not touch `data/`.

Windows without Git Bash (PowerShell, from the repository root):

```powershell
cd scripts
foreach ($s in 'a1_channels','a1b_by_condition','a2_detectors','a3_policies','a4_agent','a5_crc','a6_consequence_ci','a7_tokens','a8_detection','a9_ablation','a10_model_and_curves','a11_record_constraints','a12_localisation','a13_tokens_cond_kind','a14_weight_and_list') { python "$s.py" | Out-Null }
cd ..\figures
Get-ChildItem fig*.py | ForEach-Object { python $_.Name | Out-Null }
```

The token-set parts of seven analyses (`a2`, `a5`, `a7`, `a10`, `a11`, `a13`, `a14`) use the
recognised text of the second token set, which is not released because it contains the documents'
wording. They detect its absence (`local/reads_b.csv`), print `SKIP` where nothing can be computed,
and keep the shipped result files for those parts — so a public run reproduces `results/` byte for
byte:

```bash
git status --short results/          # empty output = identical to the files the paper used
```

## 2. Verify the shipped files

```bash
sha256sum -c checksums.sha256        # macOS: shasum -a 256 -c checksums.sha256
```

This covers every file in `data/` and `results/`. Figure PNGs are not covered because their bytes
depend on the Matplotlib version; their inputs are.

## 3. Use the decision layer on your own readers

`src/aegis/` has no OCR dependency. Give it the canonical values your channels return:

```python
from aegis.canon import canon_numeric            # raw string -> canonical value or None
from aegis.policies import cascade, with_domain  # agree-then-commit on one item
from aegis.corroboration import candidate        # plurality value and its corroboration
from aegis.crc import calibrate, min_feasible_alpha
```

`tests/test_aegis.py` shows each function on small examples; `scripts/a3_policies.py` is the full
policy replay.

## 4. Re-reading the source documents (confidential input)

Prerequisites: the seven source PDFs (`FE-0004`, `FE-0026`, `FE-0030`, `FE-0033`, `FE-0041`,
`FE-0042`, `FE-0047`) in one folder, Tesseract and Poppler on `PATH`, and the Python packages of
the table above.

```bash
pip install easyocr==1.7.2 torch torchvision "transformers>=4.46" pytesseract pdfplumber
cp env.example env.local             # fill in the four paths, then:
source env.local
bash acquisition/run_all.sh          # callout page: 16 renderings x 3 channels -> data/callouts/channel_reads.csv
bash reproduce.sh                    # everything downstream
```

The stages of `acquisition/run_all.sh`:

1. `render.py` — page 2 of `FE-0041.pdf` at 100/150/200/300 dpi, each clean, JPEG q25, Gaussian
   blur or 0.7° skew (16 renderings) into `$AEGIS_WORK/renders`;
2. `run_cond.py <dpi>_<degradation>` — Tesseract and EasyOCR on the 54 callout crops (reference
   geometry `data/callouts/boxes.json`) → `$AEGIS_WORK/reads.csv`;
3. `run_vlm.py <dpi>_<degradation>` — SmolVLM-256M on the same crops → `$AEGIS_WORK/vlm.csv`;
4. `merge_reads.py` — joins the two logs by (condition, callout) into
   `data/callouts/channel_reads.csv`.

The other acquisition scripts feed the optional experiments:

| Script | Produces |
| --- | --- |
| `run_geom.py <variant> <classic\|vlm> <cond>` | readings from shifted/tight crops (localisation experiment, `channel_reads_shifted.csv`) |
| `render_b.py`, `tokens_b.py`, `run_b.py <cond> <start> <stop> <out>` | the 344-token second set (`local/reads_b.csv`, not released) |
| `detect.py` | the contour detector that located the 54 callouts at 600 dpi |

Reading is slow on CPU (SmolVLM costs about 1.4 s per crop); `run_cond.py` and `run_vlm.py`
append row by row, so an interrupted run can be resumed after removing the partial condition.

A repeat reading will not match the shipped one bit for bit if the engine versions or CPU differ;
`results/` is therefore always recomputed from the shipped `channel_reads.csv`, and the paper's
numbers refer to that file.

## Docker

```bash
docker build -t aegis .
docker run --rm aegis                # reproduce.sh + tests
```

## Verification checklist

| Check | Command | Expected |
| --- | --- | --- |
| Tests | `python -m pytest tests` | all pass |
| Results unchanged | `git status --short results/` after `reproduce.sh` | no output |
| Files intact | `sha256sum -c checksums.sha256` | every line `OK` |
| README current | `python scripts/make_readme_tables.py --write && git diff --stat README.md` | no change |
