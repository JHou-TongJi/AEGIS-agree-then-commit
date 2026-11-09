#!/usr/bin/env bash
# Re-read the 54 callouts under the 16 rendering conditions with the three channels and rebuild
# data/callouts/channel_reads.csv.  Needs the confidential source PDFs (see DEPLOY.md, section 4).
#   export AEGIS_SRC=...  AEGIS_WORK=...  AEGIS_EASYOCR=...  [AEGIS_VLM=...]
#   bash acquisition/run_all.sh
set -euo pipefail
: "${AEGIS_SRC:?set AEGIS_SRC to the folder holding FE-0041.pdf}"
: "${AEGIS_WORK:?set AEGIS_WORK to a writable scratch folder}"
cd "$(dirname "$0")"
mkdir -p "$AEGIS_WORK"
python render.py
for dpi in 100 150 200 300; do
  for deg in clean jpeg blur skew; do
    python run_cond.py "${dpi}_${deg}"       # Tesseract + EasyOCR  -> $AEGIS_WORK/reads.csv
    python run_vlm.py  "${dpi}_${deg}"       # SmolVLM-256M         -> $AEGIS_WORK/vlm.csv
  done
done
python merge_reads.py
echo "done: data/callouts/channel_reads.csv rebuilt; run  bash reproduce.sh  next"
