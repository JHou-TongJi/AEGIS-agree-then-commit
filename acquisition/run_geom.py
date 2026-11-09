# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
import os
"""Localisation sensitivity: re-read every callout with a perturbed crop.
variant 'tight': no padding around the reference box; 'shift': box shifted right by 15 % of its
width and down by 10 % of its height, 10 % padding (a typical detector error).
Usage: python run_geom.py <variant> <channel: classic|vlm> <cond> ; appends to geom_<variant>_<channel>.csv"""
import csv, json, os, subprocess, sys
import cv2, numpy as np
HERE = os.environ.get('AEGIS_WORK', 'work')
CODE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(CODE, '..', 'data', 'callouts'))
from gold import GOLD
REF = json.load(open(os.path.join(CODE, '..', 'data', 'callouts', 'boxes.json'))); REF_W = 8001
TMP = os.path.join(os.environ.get('AEGIS_WORK', 'work'), 'tmp_g_%d.png' % os.getpid())
WL = '0123456789.-'


def crop(img, box, s, variant):
    x, y, w, h = [v * s for v in box[:4]]
    if variant == 'tight':
        pad_x = pad_y = 0.0
    else:
        x += 0.15 * w; y += 0.10 * h; pad_x, pad_y = 0.10 * w, 0.10 * h
    H, W = img.shape[:2]
    x0, y0 = int(max(0, x - pad_x)), int(max(0, y - pad_y))
    x1, y1 = int(min(W, x + w + pad_x)), int(min(H, y + h + pad_y))
    return img[y0:y1, x0:x1]


def tess(p):
    best = ''
    for psm in ('7', '8'):
        t = ''.join(subprocess.run(['tesseract', p, '-', '--psm', psm, '-c', 'tessedit_char_whitelist=' + WL],
                                   capture_output=True, text=True).stdout.split())
        if len(t) > len(best) and any(ch.isdigit() for ch in t):
            best = t
    return best


def main(variant, chan, cond):
    img = cv2.imread(os.path.join(HERE, 'renders', f'FE41p2_{cond}.png')); s = img.shape[1] / REF_W
    out = os.path.join(HERE, f'geom_{variant}_{chan}.csv'); new = not os.path.exists(out)
    if chan == 'classic':
        import easyocr
        rd = easyocr.Reader(['en'], gpu=False, verbose=False, model_storage_directory=os.environ.get('AEGIS_EASYOCR', 'models'))
    else:
        import torch
        from PIL import Image
        from transformers import AutoProcessor, AutoModelForImageTextToText
        torch.set_num_threads(2)
        P = os.environ.get('AEGIS_VLM', 'HuggingFaceTB/SmolVLM-256M-Instruct')
        proc = AutoProcessor.from_pretrained(P, do_image_splitting=False)
        m = AutoModelForImageTextToText.from_pretrained(P, dtype=torch.float32).eval()
        prompt = proc.apply_chat_template([{"role": "user", "content": [{"type": "image"}, {"type": "text",
                 "text": "Read the number in the box. Answer with the number only."}]}], add_generation_prompt=True)
    with open(out, 'a', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['cond', 'idx', 'gold', 'tess', 'easy', 'easy_conf'] if chan == 'classic' else ['cond', 'idx', 'gold', 'vlm', 'vlm_logprob'])
        for i, box in enumerate(REF):
            c = crop(img, box, s, variant)
            if chan == 'classic':
                big = cv2.resize(c, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC); cv2.imwrite(TMP, big)
                res = rd.readtext(big, detail=1, allowlist=WL, paragraph=False)
                w.writerow([cond, i, GOLD[i], tess(TMP), ''.join(t for _, t, _ in res),
                            round(float(np.mean([q for _, _, q in res])), 3) if res else 0.0])
            else:
                import torch
                from PIL import Image
                inp = proc(text=prompt, images=[Image.fromarray(cv2.cvtColor(c, cv2.COLOR_BGR2RGB))], return_tensors='pt')
                with torch.no_grad():
                    o = m.generate(**inp, max_new_tokens=6, do_sample=False, output_scores=True, return_dict_in_generate=True)
                seq = o.sequences[:, inp['input_ids'].shape[1]:]
                txt = proc.batch_decode(seq, skip_special_tokens=True)[0].strip(); lp = 0.0
                for k, sc in enumerate(o.scores):
                    tok = seq[0, k]; lp += float(torch.log_softmax(sc[0], -1)[tok])
                    if tok.item() == proc.tokenizer.eos_token_id: break
                w.writerow([cond, i, GOLD[i], txt, round(lp, 4)])
            fh.flush()
    print('done', variant, chan, cond)


if __name__ == '__main__':
    main(*sys.argv[1:4])
