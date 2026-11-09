# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
import os
"""Render every page of the seven sheets under two conditions used for dataset B."""
import glob, os, subprocess
import cv2
SRC = os.environ.get('AEGIS_SRC', 'source_documents')
HERE = os.environ.get('AEGIS_WORK', 'work')
CODE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'renders_b'); SCR = os.path.join(os.environ.get('AEGIS_WORK', 'work'), 'tmp_rb')
os.makedirs(SCR, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
DOCS = ['FE-0004', 'FE-0026', 'FE-0030', 'FE-0033', 'FE-0041', 'FE-0042', 'FE-0047']
for d in DOCS:
    for dpi in (100, 200):
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', f'{SRC}/{d}.pdf', f'{SCR}/{d}_{dpi}'], check=True)
        for f in sorted(glob.glob(f'{SCR}/{d}_{dpi}-*.png')):
            pg = int(f.rsplit('-', 1)[1][:-4])
            img = cv2.imread(f)
            if dpi == 200:
                cv2.imwrite(f'{OUT}/{d}_p{pg}_200_clean.png', img)
            else:
                ok, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 25])
                cv2.imwrite(f'{OUT}/{d}_p{pg}_100_jpeg.png', cv2.imdecode(buf, cv2.IMREAD_COLOR))
print(len(os.listdir(OUT)))
