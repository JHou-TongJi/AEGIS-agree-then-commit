# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
import os
"""Read the 54 callouts of one render condition; append each row to reads.csv as it is produced."""
import csv, json, os, subprocess, sys
import numpy as np, cv2

HERE = os.environ.get('AEGIS_WORK', 'work')
CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CODE, '..', 'data', 'callouts'))
from gold import GOLD

REF = json.load(open(os.path.join(CODE, '..', 'data', 'callouts', 'boxes.json')))
REF_W = 8001
WL = '0123456789.-'
OUT = os.path.join(HERE, 'reads.csv')
TMP = os.path.join(os.environ.get('AEGIS_WORK', 'work'), 'tmp_t.png')


def tesseract_png(path):
    best = ''
    for psm in ('7', '8'):
        t = subprocess.run(['tesseract', path, '-', '--psm', psm,
                            '-c', 'tessedit_char_whitelist=' + WL],
                           capture_output=True, text=True).stdout
        t = ''.join(t.split())
        if len(t) > len(best) and any(ch.isdigit() for ch in t):
            best = t
    if not best:
        for psm in ('7', '8'):
            t = subprocess.run(['tesseract', path, '-', '--psm', psm],
                               capture_output=True, text=True).stdout
            t = ''.join(t.split())
            if len(t) > len(best) and any(ch.isdigit() for ch in t):
                best = t
    r = subprocess.run(['tesseract', path, '-', '--psm', '7', 'tsv',
                        '-c', 'tessedit_char_whitelist=' + WL],
                       capture_output=True, text=True).stdout
    confs = []
    for line in r.strip().split('\n')[1:]:
        p = line.split('\t')
        if len(p) >= 12 and p[11].strip():
            try:
                confs.append(float(p[10]))
            except ValueError:
                pass
    return best, (float(np.mean(confs)) / 100.0 if confs else 0.0)


def main(cond):
    import easyocr
    rd = easyocr.Reader(['en'], gpu=False, verbose=False,
                        model_storage_directory=os.environ.get('AEGIS_EASYOCR', 'models'))
    img = cv2.imread(os.path.join(HERE, 'renders', 'FE41p2_' + cond + '.png'))
    s = img.shape[1] / REF_W
    new = not os.path.exists(OUT)
    with open(OUT, 'a', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['cond', 'idx', 'panel', 'gold', 'tess', 'tess_conf', 'easy', 'easy_conf'])
        for i, box in enumerate(REF):
            x, y, wd, ht = [int(round(v * s)) for v in box[:4]]
            px, py = int(wd * 0.10), int(ht * 0.10)
            H, W = img.shape[:2]
            c = img[max(0, y - py):min(H, y + ht + py), max(0, x - px):min(W, x + wd + px)]
            big = cv2.resize(c, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            ok, buf = cv2.imencode('.png', big)
            open(TMP, 'wb').write(buf.tobytes())
            tt, tc = tesseract_png(TMP)
            res = rd.readtext(big, detail=1, allowlist=WL, paragraph=False)
            et = ''.join(t for _, t, _ in res); ec = float(np.mean([c2 for _, _, c2 in res])) if res else 0.0
            w.writerow([cond, i, box[4], GOLD[i], tt, round(tc, 3), et, round(ec, 3)])
            fh.flush()
    print('done', cond)


if __name__ == '__main__':
    main(sys.argv[1])
