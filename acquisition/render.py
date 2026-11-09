# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
"""Render FE-0041 p2 (and the other sheets) at several DPI under several degradations.
Conditions mirror what a plant actually has in its document store: born-digital PDFs
re-exported as scans at low resolution, JPEG-compressed attachments, and phone photos."""
import os, subprocess, glob
import numpy as np, cv2

SRC = os.environ.get('AEGIS_SRC', 'source_documents')
OUT = os.path.join(os.environ.get('AEGIS_WORK', 'work'), 'renders')   # run_cond.py / run_vlm.py read from here
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(os.environ.get('AEGIS_WORK', 'work'), 'tmp'), exist_ok=True)

DPI = [100, 150, 200, 300]
CONDS = ['clean', 'jpeg', 'blur', 'skew']

def degrade(img, cond, rng):
    if cond == 'clean':
        return img
    if cond == 'jpeg':
        q = 25
        ok, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, q])
        return cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if cond == 'blur':
        return cv2.GaussianBlur(img, (0, 0), 0.8)
    if cond == 'skew':
        h, w = img.shape[:2]
        ang = 0.7
        M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
        return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    raise ValueError(cond)

def main():
    rng = np.random.default_rng(0)
    for dpi in DPI:
        tmp = os.path.join(os.path.join(os.environ.get('AEGIS_WORK', 'work'), 'tmp'), f'_t{dpi}')
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-f', '2', '-l', '2',
                        f'{SRC}/FE-0041.pdf', tmp], check=True)
        f = sorted(glob.glob(tmp + '*.png'))[0]
        img = cv2.imread(f)
        for cond in CONDS:
            out = os.path.join(OUT, f'FE41p2_{dpi}_{cond}.png')
            cv2.imwrite(out, degrade(img, cond, rng))
            print(out, img.shape)

if __name__ == '__main__':
    main()
