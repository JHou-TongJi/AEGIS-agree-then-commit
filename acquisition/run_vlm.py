# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
import os
"""Third, independent reading channel: a small vision-language model (SmolVLM-256M-Instruct)
asked to read the number in each callout crop.  Greedy decoding; one call per crop; the
crop geometry is identical to run_cond.py.  Rows are appended to vlm.csv as produced."""
import csv, json, os, sys
import cv2, torch
from PIL import Image

torch.set_num_threads(2)
HERE = os.environ.get('AEGIS_WORK', 'work')
CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CODE, '..', 'data', 'callouts'))
from gold import GOLD  # noqa: E402

MODEL = os.environ.get('AEGIS_VLM', 'HuggingFaceTB/SmolVLM-256M-Instruct')
REF = json.load(open(os.path.join(CODE, '..', 'data', 'callouts', 'boxes.json')))
REF_W = 8001
OUT = os.path.join(HERE, 'vlm.csv')
PROMPT = 'Read the number in the box. Answer with the number only.'


def main(cond, start=0):
    from transformers import AutoProcessor, AutoModelForImageTextToText
    proc = AutoProcessor.from_pretrained(MODEL, do_image_splitting=False)
    m = AutoModelForImageTextToText.from_pretrained(MODEL, dtype=torch.float32).eval()
    img = cv2.imread(os.path.join(HERE, 'renders', 'FE41p2_' + cond + '.png'))
    s = img.shape[1] / REF_W
    H, W = img.shape[:2]
    new = not os.path.exists(OUT)
    msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": PROMPT}]}]
    prompt = proc.apply_chat_template(msgs, add_generation_prompt=True)
    with open(OUT, 'a', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['cond', 'idx', 'gold', 'vlm', 'vlm_logprob'])
        for i, box in enumerate(REF):
            if i < start:
                continue
            x, y, wd, ht = [int(round(v * s)) for v in box[:4]]
            px, py = int(wd * 0.10), int(ht * 0.10)
            c = img[max(0, y - py):min(H, y + ht + py), max(0, x - px):min(W, x + wd + px)]
            pil = Image.fromarray(cv2.cvtColor(c, cv2.COLOR_BGR2RGB))
            inp = proc(text=prompt, images=[pil], return_tensors='pt')
            with torch.no_grad():
                out = m.generate(**inp, max_new_tokens=6, do_sample=False,
                                 output_scores=True, return_dict_in_generate=True)
            seq = out.sequences[:, inp['input_ids'].shape[1]:]
            txt = proc.batch_decode(seq, skip_special_tokens=True)[0].strip()
            lp = 0.0
            for k, sc in enumerate(out.scores):
                tok = seq[0, k]
                lp += float(torch.log_softmax(sc[0], -1)[tok])
                if tok.item() == proc.tokenizer.eos_token_id:
                    break
            w.writerow([cond, i, GOLD[i], txt, round(lp, 4)])
            fh.flush()
    print('done', cond)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0)
