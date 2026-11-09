# Reproduction map

How each result file and each figure of the paper is produced. All paths are relative to the
repository root; `reproduce.sh` runs every script below in the right order.

## Analyses → `results/`

Each analysis script reads the released data (through `scripts/common.py`) and writes the files in
its row. File names carry the script prefix (`a3_*` is written by `a3_policies.py`);
`results/cost.json` holds the measured per-call time of the three readers and is read by
`src/aegis/policies.py`.

| Script | Question it answers | Writes | Needs withheld input? |
|---|---|---|---|
| `scripts/a1_channels.py` | How do three independent reading channels fail on the 54 real callouts? | `results/a1_by_condition.csv`, `results/a1_silent_errors.csv`, `results/a1_summary.json` | no |
| `scripts/a1b_by_condition.py` | Accuracy, refusal and silent rate for every channel under every rendering condition | `results/a1_by_cond_detail.csv` | no |
| `scripts/a2_detectors.py` | Self-confidence versus cross-channel agreement as detectors of silent errors | `results/a2_detectors.json` | token-set text (`local/reads_b.csv`) for its token part |
| `scripts/a3_policies.py` | Commit/escalate policies replayed exactly on the logged channel outputs | `results/a3_policies.json`, `results/a3_policy_items.csv` | no |
| `scripts/a4_agent.py` | The agent: cascade + domain verifier + re-render, and its sensitivity to the declared range | `results/a4_agent_items.csv`, `results/a4_agent_range.json` | no |
| `scripts/a5_crc.py` | Distribution-free risk control on top of the agent | `results/a5_A_scores.csv`, `results/a5_crc.json` | token-set text (`local/reads_b.csv`) for its token part |
| `scripts/a6_consequence_ci.py` | Consequence of silent errors at the 0.5 mm tolerance; cluster-bootstrap confidence intervals | `results/a6_consequence_ci.json` | no |
| `scripts/a7_tokens.py` | Does the callout result transfer to the other digit-bearing tokens of the seven sheets? | `results/a7_tokens.json` | token-set text (`local/reads_b.csv`) for its token part |
| `scripts/a8_detection.py` | Is the callout *detector* or the *reader* the weak link at low resolution? | `results/a8_detection.csv`, `results/a8_detection.json` | page renders for its detector run |
| `scripts/a9_ablation.py` | Ablations replayed exactly: every channel pair, every cascade order, and per-callout difficulty | `results/a9_ablation.json`, `results/a9_per_callout.csv` | no |
| `scripts/a10_model_and_curves.py` | An analytical model of the 2-of-3 vote checked against the observed vote; risk-coverage curves of the corroboration threshold; the agent per rendering condition; the token set per document (aggregate only) | `results/a10_agent_by_cond.csv`, `results/a10_model.json`, `results/a10_tokens_by_doc.csv` | token-set text (`local/reads_b.csv`) for its token part |
| `scripts/a11_record_constraints.py` | Verifiers that live in the record rather than in the crop | `results/a11_record_constraints.json` | token-set text (`local/reads_b.csv`) for its token part |
| `scripts/a12_localisation.py` | Sensitivity to localisation error: every crop shifted by 15 % of the callout width and 10 % of its height, re-read by all three channels, and the re-crop tool | `results/a12_localisation.json` | no |
| `scripts/a13_tokens_cond_kind.py` | Token set by rendering and kind, and channel dependence (aggregate only) | `results/a13_token_dependence.json`, `results/a13_tokens_cond_kind.csv` | token-set text (`local/reads_b.csv`) for its token part |
| `scripts/a14_weight_and_list.py` | Sensitivity of the corroboration score to the weight on the vision-language probability; list of every committed-wrong value under every policy | `results/a14_weight.json`, `results/a14_wrong_commits.csv` | token-set text (`local/reads_b.csv`) for its token part |

Scripts in the last column marked "token-set text" keep their shipped result files when
`local/reads_b.csv` is absent (see `DEPLOY.md`, section 1), so the public run is byte-identical.

## Figures → scripts

Figure scripts read `results/` and `data/` only and write `figures/png/`. Figures 2–4 are masked
page images and need no script.

| Paper figure | Script or image | Inputs |
|---|---|---|
| Fig. 1 — the agree-then-commit loop | `figures/fig01_architecture.py` | none (drawn in Matplotlib) |
| Fig. 2 — a real problem sheet, front page | `data/masked/FE-0026_p1_masked.png` | — |
| Fig. 3 — the issue master list | `data/masked/masterlist_masked.png` | — |
| Fig. 4 — front page of the sheet with the callout page | `data/masked/FE-0041_p1_masked.png` | — |
| Fig. 5 — masked test bed and detection performance | `figures/fig05_testbed.py` | `data/masked/FE-0041_p2_masked.png`, `data/callouts/boxes.json`, `results/a8_detection.csv` |
| Fig. 6 — where the method sits in the pipeline | `figures/fig06_pipeline.py` | none |
| Fig. 7 — six real crops, each a silent error | `figures/fig07_crops.py` (+ `gallery_cases.py`) | `data/crops/` |
| Fig. 8 — channel anatomy over 864 reads | `figures/fig08_channels.py` | `results/a1_summary.json`, `results/a1_by_condition.csv` |
| Fig. 9 — detection of a channel's own silent errors | `figures/fig09_detection.py` | `results/a2_detectors.json` |
| Fig. 10 — policies replayed on the logged readings | `figures/fig10_policies.py` | `results/a3_policies.json`, `results/a4_agent_range.json` |
| Fig. 11 — where the errors are (per callout) | `figures/fig11_per_callout.py` | `results/a9_per_callout.csv` |
| Fig. 12 — localisation | `figures/fig12_localisation.py` | `data/callouts/boxes.json`, `data/crops/`, `results/a12_localisation.json` |
| Fig. 13 — the guard and the guarantee | `figures/fig13_guard_guarantee.py` | `results/a4_agent_range.json`, `results/a5_crc.json` |
| Fig. 14 — transfer to the digit-bearing tokens | `figures/fig14_tokens.py` | `results/a1_summary.json`, `results/a7_tokens.json`, `results/a13_token_dependence.json` |
| Fig. 15 — risk–coverage, agent per condition, weaker third reader | `figures/fig15_risk_coverage.py` | `results/a10_agent_by_cond.csv`, `results/a10_model.json` |

## Tables of the paper

The tables are built from the same result files: Table values come from `a1_summary.json`
(channels), `a2_detectors.json` (detectors), `a3_policies.json`, `a4_agent_range.json`,
`a9_ablation.json` (policies, pairs, orders), `a12_localisation.json` (localisation),
`a5_crc.json` (risk control), `a7_tokens.json`, `a13_*` (token set), `a11_record_constraints.json`
(verifiers in the record), `a10_model.json` (vote model) and `a6_consequence_ci.json`
(consequences and intervals). Rounded values in the paper are the files' six-decimal values
rounded once.
