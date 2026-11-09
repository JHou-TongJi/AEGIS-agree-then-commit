# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
import os
"""Dataset B: every ASCII token containing a digit on the 18 pages of the seven problem sheets,
with its text-layer string as reference and its bounding box in PDF points."""
import csv, os, re
import pdfplumber

SRC = os.environ.get('AEGIS_SRC', 'source_documents')
DOCS = ['FE-0004', 'FE-0026', 'FE-0030', 'FE-0033', 'FE-0041', 'FE-0042', 'FE-0047']
PURE = re.compile(r'^[-+]?(\d+([.,]\d+)?|\.\d+)$')
CW = re.compile(r'^\d{0,4}(CW|KW)\d', re.I)


def kind(t):
    if PURE.match(t):
        return 'numeral'
    if CW.match(t):
        return 'week_code'
    return 'alnum'


def main():
    rows = []
    for d in DOCS:
        pdf = pdfplumber.open(f'{SRC}/{d}.pdf')
        for pi, pg in enumerate(pdf.pages, 1):
            for w in pg.extract_words():
                t = w['text']
                if not re.search(r'\d', t) or not all(ord(c) < 128 for c in t):
                    continue
                rows.append(dict(doc=d, page=pi, ref=t, kind=kind(t), pw=float(pg.width),
                                 ph=float(pg.height), x0=w['x0'], x1=w['x1'], top=w['top'],
                                 bottom=w['bottom']))
    work = os.environ.get('AEGIS_WORK', 'work')
    os.makedirs(work, exist_ok=True)
    out = os.path.join(work, 'tokens_b.csv')          # run_b.py reads it from here
    with open(out, 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader(); wr.writerows(rows)
    import collections
    print(len(rows), collections.Counter(r['kind'] for r in rows),
          collections.Counter(r['doc'] for r in rows))


if __name__ == '__main__':
    main()
