# Code Notes

This is the code snapshot behind the paper. [`DEPLOY.md`](DEPLOY.md) is the authoritative
reproduction entry point; this file documents code boundaries and interfaces.

The snapshot contains the decision layer, the analysis and figure scripts and the acquisition
scripts. It does **not** contain the source documents, page renders, the recognised text of the
second token set, or any OCR model weights.

## Code scope

### Decision layer — `src/aegis/`

| Module | Contents |
| --- | --- |
| `canon.py` | Canonicalisation `κ`: one string → one value or *refusal*. `canon_numeric` implements the callout grammar (one decimal place, optional minus) and **never edits digits**: `07` stays `7.0` because a dropped separator is a legal value that only the range guard can catch. `canon_token` handles numerals, calendar-week codes and alphanumeric strings |
| `corroboration.py` | `candidate(item)` → (plurality value, corroboration `c`), with the SmolVLM sequence probability as a tie-breaker bounded by one |
| `policies.py` | `single`, `majority`, `cascade` (cheapest first, stop at two agreeing reads, optional re-render/re-crop), `with_domain` (range guard), measured per-call costs from `results/cost.json` |
| `crc.py` | `calibrate` (conformal risk control for a monotone commit rule) and `min_feasible_alpha` (`1/(n+1)`) |

Every tool is deterministic, so a policy is replayed on logged readings (`scripts/a3_policies.py`)
instead of being simulated: the comparison between policies is exact.

### Analyses — `scripts/`

One script per analysis, `a1` … `a14`; each reads `data/` (through `scripts/common.py`) and writes
`results/`. The map from script to result file to figure is in
[`docs/reproduction-map.md`](docs/reproduction-map.md).

### Figures — `figures/`

One script per figure of the paper, numbered as in the paper (`fig08_channels.py` is Fig. 8).
`_style.py` holds the shared typography; `fig01_architecture.py` draws the flow diagram in
Matplotlib with serif type and orthogonal connectors.

### Acquisition — `acquisition/`

Scripts that produced `data/callouts/*.csv` from the confidential documents (render → read with
three channels → merge). They are kept so that the measurement is auditable; they are not needed
to replay the paper. `AEGIS_SRC`, `AEGIS_WORK`, `AEGIS_EASYOCR` and `AEGIS_VLM` select the paths
(`env.example`).

## Directory structure

| Location | Contents |
| --- | --- |
| `src/aegis/` | The Python package (installed with `pip install -e .`) |
| `scripts/` | Analysis scripts and `make_readme_tables.py` |
| `figures/` | Figure scripts; PNG output in `figures/png/` |
| `acquisition/` | Reading scripts for the confidential documents |
| `data/`, `results/` | Released derived data; every reported number |
| `tests/` | `test_aegis.py` (units + headline numbers), `test_checksums.py`, `test_readme.py`, `test_merge_reads.py` |
| `pyproject.toml` | Package metadata and optional dependency groups |

## Installing

```bash
pip install -r requirements.txt && pip install -e .
```

Optional groups in `pyproject.toml`: `figures` (pandas, Matplotlib, OpenCV, Pillow), `readers`
(the OCR/VLM engines of `acquisition/`), `dev` (pytest).

## Minimal health check

```bash
python -m pytest -q tests
python scripts/a1_channels.py && python -c "import json; print(json.load(open('results/a1_summary.json'))['n_reads'])"   # 864
```

## Input and output semantics

* **Item** — one field value to decide on: a dict with the canonical value of each channel
  (`tess`, `easy`, `vlm`, `None` = refusal) and, for the vision-language model, its sequence
  log-probability (`vlm_lp`).
* **Unit** — the exchangeable group used for calibration: a (rendering condition, page panel)
  block on the callout page, a document on the token set. The loss of a unit at threshold `λ` is the
  share of its reads that are committed *and* wrong.
* **Committed error** — wrong committed values divided by committed values. **Residual risk** —
  wrong committed values divided by all values. Both appear in `results/a3_policies.json`.
* **Silent error** — a value that passes the format guard (and the range guard, if declared) and is
  not the reference value. A refusal is never silent.

## Licence and data boundaries

Read [`third_party.md`](third_party.md) and `docs/data-compliance.md` before using or
redistributing anything derived from this repository. The masked pages and derived readings are
for research and reproduction only.
