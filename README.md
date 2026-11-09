# AEGIS — Agree, Then Commit

**Cross-Channel Verification with Distribution-Free Risk Control for Silent Extraction Errors in
New Energy Vehicle Production Quality Documents**

Jue Hou, Xinglong Liu, He Huang — submitted to *IEEE Access*.
Repository: <https://github.com/JHou-TongJi/AEGIS-agree-then-commit>

A battery-electric vehicle plant designs a body surface in CATIA, measures it on a coordinate
measuring machine, and records the deviation on a problem sheet that a clerk re-keys into SAP
Quality Management and the manufacturing execution system (MES). Automating that step creates a
failure of its own: a **silent error** is a read that returns a well-formed, plausible value that
is wrong — `1.4 mm` read as `14`, `-0.2` read as `0.2`. It passes every schema check and enters
the record with the same standing as a correct value.

This repository holds the decision layer, the derived readings it was measured on, every script
that turns those readings into a number or a figure of the paper, and the evidence needed to check
them. It deliberately does **not** hold the source documents — see
[What is not here](#what-is-not-here-and-why).

| | |
|---|---|
| **Test bed** | 54 real measurement callouts × 16 renderings × 3 independent channels = **2,592 reads** (864 per channel) |
| **Silent errors** | **101** of 2,592 reads are well-formed and wrong; 100 % of the vision-language model's errors are silent |
| **Why neither refusal nor confidence helps** | Tesseract refuses 18.1 % of reads and still emits 8.6 % silent errors; EasyOCR's own confidence separates its wrong values from its right ones with AUROC **0.42** (worse than chance) |
| **What does help** | agreement of an independent channel: AUROC **0.987** for the same EasyOCR errors |
| **Decision rule** | cascade EasyOCR > Tesseract > SmolVLM that stops at two agreeing reads: **96.3 %** committed at **0.24 %** committed error, **1.09 s** per value (2.05 s if all three are always called) |
| **With range guard + re-crop** | 99.65 % committed at 0.12 % committed error (1 wrong value in 861) |
| **Certified risk** | conformal risk control over exchangeable units; with *n* units no bound below 1/(*n*+1) can be certified — 1/91 = 1.1 % with the 90 calibration blocks of each fold |
| **Transfer** | 688 reads of 344 digit-bearing tokens on 17 pages of seven sheets: best single channel 27.9 % committed error → 2-of-3 vote 2.4 % |
| **Scope of the guarantee** | the *expected* committed-and-silent share of a fresh unit, under exchangeability of calibration and served units — not a per-document or per-value guarantee |

---

## What the method does

Three readers that share neither training data nor failure mode read the same evidence atom
(the crop of one field): **Tesseract 4.1** (LSTM on a binarised crop), **EasyOCR 1.7**
(CRAFT + CRNN) and **SmolVLM-256M** (a vision-language model). A silent error preserves the
surface form that a reader's confidence is computed from, but it does not preserve the *agreement
of an independent reader* — so agreement, not confidence, is the signal.

```text
page ─▶ evidence atoms ─┬─▶ Tesseract ─┐
                        ├─▶ EasyOCR  ──┼─▶ canonicalise ─▶ format guard ─▶ range guard ─▶ c(v)
                        └─▶ SmolVLM  ──┘                                                  │
        ▲                                                       c(v) ≥ λ̂ ──▶ commit + audit record
        └── no two channels agree: re-crop / re-render once      c(v) < λ̂ ──▶ escalate + reason code

 λ̂ = inf{ λ : n/(n+1) · R̂ₙ(λ) + 1/(n+1) ≤ α }      (conformal risk control, offline, once)
```

* **Corroboration** `c(v)` = number of channels that return the candidate `v`, plus the
  SmolVLM sequence probability when it returns `v` (a tie-breaker, never worth a whole channel).
  Committing iff `c(v) ≥ λ̂` is monotone in `λ̂`, which is what the risk calibration needs.
* **Cascade** — channels are called cheapest first and the loop stops at the first two agreeing
  reads. Every tool is deterministic, so a policy is *replayed* on logged readings rather than
  simulated.
* **Guards** — a format guard (the field grammar) and a declared plausible range turn illegal or
  implausible strings into visible refusals. The range is a declaration, not a fitted parameter:
  the decision is unchanged for every range between 1.6 mm and 6.9 mm.
* **Calibration** — the loss of a calibration unit is the share of its reads that are committed
  *and* silent; `λ̂` is the smallest threshold whose finite-sample-corrected risk is within the
  requested bound `α`.

Code: [`src/aegis/`](src/aegis) (`canon.py`, `policies.py`, `corroboration.py`, `crc.py`).

---

## Results

Every number below is read from [`results/`](results) by
[`scripts/make_readme_tables.py`](scripts/make_readme_tables.py); `tests/test_readme.py` fails if
this page and the result files disagree. Each table names the file it came from.

### Three channels, three failure profiles

<!-- table:channels -->
| Channel | Exact match | Refused | Silent wrong | Silent share of its errors |
|---|---:|---:|---:|---:|
| Tesseract 4.1 | 73.4 % | 18.1 % | 8.6 % | 32 % |
| EasyOCR 1.7 | 89.4 % | 8.4 % | 2.2 % | 21 % |
| SmolVLM-256M | 99.1 % | 0.0 % | 0.9 % | 100 % |
<!-- /table:channels -->

Source: [`results/a1_summary.json`](results/a1_summary.json). Accuracy and visibility work
against each other: the reader that refuses most has the lowest silent share of its errors, and the
reader that never refuses is silent on every error it makes.

### Detecting a channel's own silent errors

<!-- table:detectors -->
| Channel | Committed reads | Wrong | AUROC, own confidence | AUROC, corroboration by the others |
|---|---:|---:|---:|---:|
| Tesseract 4.1 | 708 | 74 | 0.45 | 0.999 |
| EasyOCR 1.7 | 791 | 19 | 0.42 | 0.987 |
| SmolVLM-256M | 864 | 8 | 0.93 | 0.984 |
<!-- /table:detectors -->

Source: [`results/a2_detectors.json`](results/a2_detectors.json). AUROC with the silent error as
the positive class; "corroboration" uses only the other two channels.

### Commit/escalate policies, replayed on the 864 logged reads

<!-- table:policies -->
| Policy | Committed | Committed error | Wrong committed (of 864) | Cost per value |
|---|---:|---:|---:|---:|
| Tesseract alone | 81.9 % | 10.45 % | 74 | 0.49 s |
| EasyOCR alone | 91.6 % | 2.40 % | 19 | 0.13 s |
| SmolVLM alone | 100.0 % | 0.93 % | 8 | 1.43 s |
| 2-of-3 vote, all channels called | 96.3 % | 0.24 % | 2 | 2.05 s |
| cascade EasyOCR > Tesseract > SmolVLM | 96.3 % | 0.24 % | 2 | 1.09 s |
| unanimity of three | 66.4 % | 0.00 % | 0 | 2.05 s |
| cascade + range guard (R = 3 mm) + re-crop | 99.65 % | 0.12 % | 1 | 1.17 s |
<!-- /table:policies -->

Sources: [`results/a3_policies.json`](results/a3_policies.json) and
[`results/a12_localisation.json`](results/a12_localisation.json) (last row). Costs are measured
seconds per value on two CPU threads ([`results/cost.json`](results/cost.json)).

### Risk control, leave-one-rendering-condition-out (callout page)

<!-- table:risk_control -->
| Requested bound α | Mean realised risk | Worst held-out block | Coverage | Infeasible folds |
|---:|---:|---:|---:|---:|
| 0.5 % | 0.00 % | 0.00 % | 0.0 % | 16 / 16 |
| 1.0 % | 0.00 % | 0.00 % | 0.0 % | 16 / 16 |
| 2.0 % | 0.46 % | 11.11 % | 100.0 % | 0 / 16 |
| 3.0 % | 0.46 % | 11.11 % | 100.0 % | 0 / 16 |
| 5.0 % | 0.46 % | 11.11 % | 100.0 % | 0 / 16 |
| 7.5 % | 0.46 % | 11.11 % | 100.0 % | 0 / 16 |
| 10.0 % | 0.46 % | 11.11 % | 100.0 % | 0 / 16 |
| 15.0 % | 0.46 % | 11.11 % | 100.0 % | 0 / 16 |
| 20.0 % | 0.46 % | 11.11 % | 100.0 % | 0 / 16 |
<!-- /table:risk_control -->

Source: [`results/a5_crc.json`](results/a5_crc.json). 16 folds, each calibrated on the 90 blocks of
the other 15 conditions. Below 1/91 = 1.1 % the requested bound cannot be certified with the units
available, and the method reports the fold as infeasible instead of returning a number.

### Transfer to the digit-bearing tokens of the seven sheets

<!-- table:tokens -->
| Token kind | Reads | EasyOCR alone: committed error | SmolVLM alone: committed error | 2-of-3 vote: committed | 2-of-3 vote: committed error |
|---|---:|---:|---:|---:|---:|
| numerals | 268 | 8.5 % | 0.5 % | 86.6 % | 2.16 % |
| calendar-week codes | 76 | 14.6 % | 5.0 % | 25.0 % | 0.00 % |
| alphanumeric strings | 344 | 43.6 % | 63.4 % | 45.9 % | 3.16 % |
| all tokens | 688 | 27.9 % | 37.8 % | 59.4 % | 2.44 % |
<!-- /table:tokens -->

Source: [`results/a7_tokens.json`](results/a7_tokens.json). This set is much harder than the
callout page: tokens are set in small type in table cells and body text, not framed in a callout,
and three in five are not pure numbers.

---

## Data

Everything under `data/` is derived from confidential production documents and contains no free
text of those documents and no partner identifier. File and column descriptions:
[`docs/DATA.md`](docs/DATA.md).

| File | Rows | Contents |
|---|---:|---|
| [`data/callouts/channel_reads.csv`](data/callouts/channel_reads.csv) | 864 | Reference value and the canonical value returned by each channel for each (rendering, callout), with EasyOCR confidence and SmolVLM log-probability |
| [`data/callouts/channel_reads_shifted.csv`](data/callouts/channel_reads_shifted.csv) | 864 | The same callouts re-read from crops shifted by 15 % of the width and 10 % of the height |
| [`data/callouts/boxes.json`](data/callouts/boxes.json) | 54 | Reference geometry of the callouts at 600 dpi |
| [`data/callouts/gold.py`](data/callouts/gold.py) | 54 | Reference values, transcribed by hand from a 600 dpi render and cross-checked |
| [`data/masterlist/issue_records_structural.csv`](data/masterlist/issue_records_structural.csv) | 122 | Structural columns of the issue master list (lengths, presence flags, calendar week, traffic light, status, zone); no wording |
| [`data/masked/`](data/masked) | 4 images | Real pages with plant mark, project and product names, person names, department codes and part numbers covered |
| [`data/crops/`](data/crops) | 8 images | The crops shown in the paper's figures |
| [`checksums.sha256`](checksums.sha256) | — | SHA-256 of every file in `data/` and `results/`; verify with `sha256sum -c checksums.sha256` |

The CSVs in [`results/`](results) are flat tables meant to be loaded directly; the JSON files hold
the aggregate records they were derived from.

### Documentation

| Document | Contents |
|---|---|
| [`DEPLOY.md`](DEPLOY.md) | Authoritative reproduction guide: environment, replay from released data, re-reading from source documents, verification |
| [`CODE_NOTES.md`](CODE_NOTES.md) | Code boundaries, interfaces, health check |
| [`docs/DATA.md`](docs/DATA.md) | Dictionary of every released data file and column |
| [`docs/reproduction-map.md`](docs/reproduction-map.md) | Which script produces which result file and which figure of the paper |
| [`docs/data-compliance.md`](docs/data-compliance.md) | What is released, what is withheld, and the conditions of use |
| [`third_party.md`](third_party.md) | Third-party software, models and licence boundaries |

---

## Repository layout

| Path | Contents |
|---|---|
| `src/aegis/` | The decision layer: canonicalisation, guards, policies, corroboration, risk control (no OCR dependency) |
| `scripts/a*.py` | One analysis per script; each reads `data/` and writes `results/` |
| `figures/fig*.py` | One script per figure of the paper, numbered as in the paper; reads `results/` and `data/` only |
| `acquisition/` | Scripts that produced `data/callouts/*.csv` from the confidential source documents |
| `data/`, `results/` | Released derived data and every reported number |
| `docs/` | Data dictionary, reproduction map, data-compliance statement |
| `tests/` | Unit tests, regression tests on the headline numbers, checksum and README consistency tests |
| `reproduce.sh` | Recomputes `results/` and `figures/png/` from the released data (about one minute, CPU only) |
| `env.example` | Template of the environment variables used by `acquisition/` |
| `Dockerfile` | Container that runs `reproduce.sh` and the tests |

---

## Install

Python 3.9–3.12. The replay needs only NumPy, pandas, Matplotlib, OpenCV (three figures) and Pillow.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Deploy and reproduce

[`DEPLOY.md`](DEPLOY.md) is the authoritative entry point. In outline:

```bash
bash reproduce.sh                    # recompute results/ and figures/png/ from data/
python -m pytest tests               # unit, regression, checksum and README tests
sha256sum -c checksums.sha256        # the shipped data and results are the ones the paper used
```

`git status --short results/` should print nothing after `reproduce.sh`: the result files are
reproduced byte for byte. Re-reading the documents with the three engines needs the confidential
source PDFs (`DEPLOY.md`, section 4).

---

## What is not here, and why

The source problem sheets and issue list belong to a vehicle plant and are used under a data-use
agreement. This repository therefore does **not** contain:

- the source PDFs, page renders, or crops other than the eight shown in the paper;
- the recognised text of the 344-token second set (`local/reads_b.csv`), which contains the
  documents' wording — the token-set parts of the analyses detect its absence and keep the
  shipped result files;
- model weights of Tesseract, EasyOCR or SmolVLM (obtain them from their own channels,
  [`third_party.md`](third_party.md)).

The masked pages are released for research and reproduction only; attempting to recover masked
content is not permitted ([`LICENSE-DATA`](LICENSE-DATA)).

## Licensing

Code and configuration: [MIT](LICENSE). Data under `data/` and images under `figures/png/`:
[CC BY-NC 4.0](LICENSE-DATA). Third-party components keep their own licences
([`third_party.md`](third_party.md)).

## Status and honest limits

The callout experiment is **one metrology page of one problem sheet** (54 values) read under 16
renderings of that page; the second set is seven sheets from the same plant. The three channels
are configured by us and the numbers move with other configurations — a larger vision-language
model would raise accuracy and lower the vote's marginal value. The claim is about the *shape* of
the result: agreement detects what confidence cannot, on this evidence. Channel errors are
positively dependent (phi 0.08–0.20 on the callout page, `results/a1_summary.json`), which the
two-parameter model in `results/a10_model.json` takes into account. On the token set the reference is the document's text layer,
which validates transcription fidelity, not the correctness of the source record. The risk
guarantee holds in expectation over exchangeable units and has a floor of 1/(*n*+1); seven
documents certify nothing below a few per cent.

## Citation

See [`CITATION.cff`](CITATION.cff).
