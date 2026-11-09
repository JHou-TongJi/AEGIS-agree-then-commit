"""A8 -- Is the callout *detector* or the *reader* the weak link at low resolution?

The detector is the same contour rule at every resolution (area/aspect/corner-roundness), scaled
with the render.  We report how many of the 54 callouts it finds per condition.  All readings in
A1-A7 use reference geometry, so they measure reading and not detection; this script measures the
part that reference geometry hides.
"""
import json, os, sys
import cv2
from common import *  # noqa

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(HERE, '..', 'work')
sys.path.insert(0, os.path.join(HERE, 'acquisition'))

CONDS = ['100_clean', '100_jpeg', '100_blur', '100_skew', '150_clean', '150_jpeg', '150_blur',
         '150_skew', '200_clean', '200_jpeg', '200_blur', '200_skew', '300_clean', '300_jpeg',
         '300_blur', '300_skew']


def main():
    if not os.path.isdir(os.path.join(WORK, 'renders')):
        print('SKIP: page renders are local-only; results/a8_detection.csv is shipped'); return
    rows = []
    for c in CONDS:
        p = os.path.join(WORK, 'renders', f'FE41p2_{c}.png')
        import detect
        img, b = detect.detect(p)
        n = sum(1 for x in b)
        s = img.shape[1] / 8001
        # coverage of the reference boxes by the nearest detection
        cov = 0
        for rx, ry, rw, rh, rp in detect.REF:
            hit = any(abs(x - rx * s) < 0.5 * rw * s and abs(y - ry * s) < 0.5 * rh * s
                      for x, y, w, h, pp in b)
            cov += hit
        rows.append(dict(cond=c, detected=n, recall_ref=cov / 54, false=n - cov))
        print(c, n, round(cov / 54, 3))
    D = pd.DataFrame(rows)
    D.to_csv(os.path.join(OUT, 'a8_detection.csv'), index=False)
    json.dump(dict(at_600='54/54 by construction (reference)', rows=rows),
              open(os.path.join(OUT, 'a8_detection.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
