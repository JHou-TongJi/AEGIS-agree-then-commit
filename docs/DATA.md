# Released data

Everything under `data/` is derived from confidential production documents of a vehicle plant and
is released under CC BY-NC 4.0 (`LICENSE-DATA`). Nothing here contains free text from the
documents, person names, part numbers or the plant identity.

| File | Rows | Content |
|---|---|---|
| `data/callouts/channel_reads.csv` | 864 | One row per (rendering condition, callout): reference value and the canonical value returned by each channel, with EasyOCR confidence and SmolVLM log-probability |
| `data/callouts/channel_reads_shifted.csv` | 864 | Same callouts re-read after shifting each crop by 15 % of its width and 10 % of its height |
| `data/callouts/boxes.json` | 54 | Reference geometry of the callouts at 600 dpi: `[x, y, w, h, panel]` |
| `data/callouts/gold.py` | 54 | Reference values, transcribed by hand from a 600 dpi render |
| `data/masterlist/issue_records_structural.csv` | 122 | Structural columns of the issue master list: field lengths, presence flags, calendar week, traffic light, status, zone; no wording |
| `data/masked/*.png` | 4 | Real pages with identity masked (two problem-sheet front pages, the callout page, the master list) |
| `data/crops/*.png` | 8 | The crops shown in Figs. 7 and 12 of the paper (numeric callouts only) |

## Columns of `channel_reads.csv`

| Column | Meaning |
|---|---|
| `cond` | Rendering condition, `<dpi>_<degradation>`; dpi ∈ {100, 150, 200, 300}, degradation ∈ {clean, jpeg, blur, skew} |
| `idx` | Callout index 0–53, order of `boxes.json` |
| `panel` | Build stage p1–p6 |
| `gold` | Reference value in mm |
| `tess`, `easy`, `vlm` | Canonical string returned by Tesseract 4.1, EasyOCR 1.7, SmolVLM-256M; empty = no read |
| `tess_conf` | Tesseract mean word confidence / 100 (0 on most reads under a character whitelist) |
| `easy_conf` | EasyOCR confidence |
| `vlm_logprob` | Sum of token log-probabilities of the SmolVLM answer |

## Not released

The source PDFs, the page renders, and `local/reads_b.csv` (recognised text of the 344-token
second set, which contains document wording). Scripts that need `local/` print `SKIP` and keep the
shipped result files, so a public run reproduces `results/` unchanged.
