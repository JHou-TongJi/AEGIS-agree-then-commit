#!/usr/bin/env bash
# Recompute every number and figure of the paper from the released derived data.
# Scripts that need the local-only token readings or page renders print SKIP and keep the
# shipped result file.
set -e
cd "$(dirname "$0")/scripts"
for s in a1_channels a1b_by_condition a2_detectors a3_policies a4_agent a5_crc a6_consequence_ci \
         a7_tokens a8_detection a9_ablation a10_model_and_curves a11_record_constraints \
         a12_localisation a13_tokens_cond_kind a14_weight_and_list; do
  echo "== $s"; python "$s.py" > /dev/null || { echo "FAILED: $s"; exit 1; }
done
cd ../figures
for f in fig01_architecture fig05_testbed fig06_pipeline fig07_crops fig08_channels fig09_detection \
         fig10_policies fig11_per_callout fig12_localisation fig13_guard_guarantee fig14_tokens \
         fig15_risk_coverage; do
  echo "== $f"; python "$f.py" > /dev/null
done
echo "done"
