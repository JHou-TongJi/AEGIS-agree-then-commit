# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
import os
"""Read every digit token of dataset B with three channels (Tesseract, EasyOCR, SmolVLM).
Usage: python run_b.py <cond> <start> <stop> <outfile>"""
import csv, os, subprocess, sys
import cv2, numpy as np, pandas as pd, torch
from PIL import Image
torch.set_num_threads(2)
HERE = os.environ.get('AEGIS_WORK', 'work')
CODE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(os.environ.get('AEGIS_WORK', 'work'), 'tmp_tb_%d.png' % os.getpid())
MODEL = os.environ.get('AEGIS_VLM', 'HuggingFaceTB/SmolVLM-256M-Instruct')
PROMPT = 'Read the text in the image exactly. Answer with the text only.'


def tess(path):
    best = ''
    for psm in ('7', '8'):
        t = subprocess.run(['tesseract', path, '-', '--psm', psm], capture_output=True, text=True).stdout
        t = ''.join(t.split())
        if len(t) > len(best):
            best = t
    return best


def main(cond, a, b, out):
    import easyocr
    from transformers import AutoProcessor, AutoModelForImageTextToText
    rd = easyocr.Reader(['en'], gpu=False, verbose=False,
                        model_storage_directory=os.environ.get('AEGIS_EASYOCR', 'models'))
    proc = AutoProcessor.from_pretrained(MODEL, do_image_splitting=False)
    m = AutoModelForImageTextToText.from_pretrained(MODEL, dtype=torch.float32).eval()
    prompt = proc.apply_chat_template([{"role": "user", "content": [{"type": "image"},
                                        {"type": "text", "text": PROMPT}]}], add_generation_prompt=True)
    T = pd.read_csv(os.path.join(HERE, 'tokens_b.csv'))
    cache = {}
    new = not os.path.exists(out)
    with open(out, 'a', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['cond', 'tid', 'doc', 'page', 'kind', 'ref', 'tess', 'easy', 'easy_conf', 'vlm', 'vlm_logprob'])
        for tid in range(a, min(b, len(T))):
            r = T.iloc[tid]
            key = (r.doc, r.page)
            if key not in cache:
                cache[key] = cv2.imread(os.path.join(HERE, 'renders_b', f'{r.doc}_p{r.page}_{cond}.png'))
            img = cache[key]
            s = img.shape[1] / r.pw
            H, W = img.shape[:2]
            ph = (r.bottom - r.top) * s
            x0, x1 = int(r.x0 * s - 0.3 * ph), int(r.x1 * s + 0.3 * ph)
            y0, y1 = int(r.top * s - 0.25 * ph), int(r.bottom * s + 0.25 * ph)
            c = img[max(0, y0):min(H, y1), max(0, x0):min(W, x1)]
            if c.size == 0 or c.shape[0] < 3 or c.shape[1] < 3:
                w.writerow([cond, tid, r.doc, r.page, r.kind, r.ref, '', '', 0, '', 0]); continue
            f = max(1.0, 64.0 / c.shape[0])
            big = cv2.resize(c, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(TMP, big)
            tt = tess(TMP)
            res = rd.readtext(big, detail=1, paragraph=False)
            et = ''.join(t for _, t, _ in res); ec = float(np.mean([q for _, _, q in res])) if res else 0.0
            pil = Image.fromarray(cv2.cvtColor(big, cv2.COLOR_BGR2RGB))
            inp = proc(text=prompt, images=[pil], return_tensors='pt')
            with torch.no_grad():
                o = m.generate(**inp, max_new_tokens=16, do_sample=False,
                               output_scores=True, return_dict_in_generate=True)
            seq = o.sequences[:, inp['input_ids'].shape[1]:]
            vt = proc.batch_decode(seq, skip_special_tokens=True)[0].strip()
            lp = 0.0
            for k, sc in enumerate(o.scores):
                tok = seq[0, k]; lp += float(torch.log_softmax(sc[0], -1)[tok])
                if tok.item() == proc.tokenizer.eos_token_id:
                    break
            w.writerow([cond, tid, r.doc, r.page, r.kind, r.ref, tt, et, round(ec, 3), vt, round(lp, 4)])
            fh.flush()
    print('done', cond, a, b)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
