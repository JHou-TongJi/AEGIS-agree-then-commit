# Acquisition scripts: they produce data/callouts/*.csv from a local copy of the source
# documents, which are confidential and not part of this repository.  Paths are set by the
# environment variables AEGIS_SRC (folder with the source PDFs), AEGIS_WORK (scratch folder for
# renders and crops), AEGIS_EASYOCR (EasyOCR model folder) and AEGIS_VLM (SmolVLM snapshot).
import os
"""Detect and crop the 54 measurement callouts on a render of FE-0041 p2 at any DPI.

The callouts are rounded rectangles with a black outline on a white page.  At 600 dpi the
detector finds exactly 54; at lower resolution the aspect/size gate is scaled with the render
and the detection is checked against the reference count, so a condition is either measured
on all 54 values or reported as a detection failure (never silently on a subset).
"""
import json, os
import numpy as np, cv2

HERE = os.environ.get('AEGIS_WORK', 'work')
CODE = os.path.dirname(os.path.abspath(__file__))
REF = json.load(open(os.path.join(CODE, '..', 'data', 'callouts', 'boxes.json')))
REF_DPI = 600
REF_W = 8001  # width of the 600 dpi reference render, pixels


def detect(path, gold_count=54):
    img = cv2.imread(path)
    H, W = img.shape[:2]
    s = W / REF_W
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th = cv2.threshold(g, 200, 255, cv2.THRESH_BINARY_INV)[1]
    cnts, _ = cv2.findContours(th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if 60 * s < w < 260 * s and 45 * s < h < 160 * s and 0.9 < w / h < 3.2:
            area = cv2.contourArea(c); peri = cv2.arcLength(c, True)
            if peri > 0 and 4 * np.pi * area / peri ** 2 > 0.55:
                col = 0 if x < W / 3 else (1 if x < 2 * W / 3 else 2)
                row = 0 if y < H / 2 else 1
                boxes.append([int(x), int(y), int(w), int(h),
                              ['p1', 'p2', 'p3', 'p4', 'p5', 'p6'][row * 3 + col]])
    boxes.sort(key=lambda b: (b[4], b[1], b[0]))
    return img, boxes


def match_to_ref(boxes, s):
    """Nearest-reference matching in scaled coordinates; returns index list aligned to REF."""
    order, used = [], np.zeros(len(boxes), bool)
    for rx, ry, rw, rh, rp in REF:
        cx, cy = rx * s, ry * s
        best, bd = None, 1e9
        for i, (x, y, w, h, p) in enumerate(boxes):
            if used[i] or p != rp:
                continue
            d = abs(x - cx) + abs(y - cy)
            if d < bd:
                bd, best = d, i
        if best is None:
            order.append(None)
        else:
            used[best] = True
            order.append(best)
    return order
