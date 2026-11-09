"""Fig. 5(a) -- The measurement page as the agent sees it: masked document + detected callouts + stat."""
import json, os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image
from _style import *

R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
img = Image.open(os.path.join(D, 'masked', 'FE-0041_p2_masked.png'))
boxes = json.load(open(os.path.join(D, 'callouts', 'boxes.json')))
det = __import__('pandas').read_csv(os.path.join(R, 'a8_detection.csv'))

fig = plt.figure(figsize=(7.02, 3.55))
ax = fig.add_axes([0.005, 0.40, 0.985, 0.585])
ax.imshow(img); ax.axis('off')
sx = img.width / 8001.0
for x, y, w, h, p in boxes:
    ax.add_patch(Rectangle((x * sx, y * sx), w * sx, h * sx, fill=False, edgecolor=C(0),
                           linewidth=0.55, alpha=0.85))
ax.text(0.004, 1.005, '54 detected callouts, reference geometry at 600 dpi', transform=ax.transAxes,
        fontsize=6.4, color=C(0), va='bottom')

ax2 = fig.add_axes([0.075, 0.085, 0.355, 0.215])
order = ['100_clean', '100_jpeg', '100_blur', '100_skew', '150_clean', '150_jpeg', '150_blur',
         '150_skew', '200_clean', '200_jpeg', '200_blur', '200_skew', '300_clean', '300_jpeg',
         '300_blur', '300_skew']
v = [det.loc[det.cond == c, 'recall_ref'].values[0] for c in order]
xs = np.arange(len(order))
cols = [C(3) if c.startswith('100') else (C(4) if c.startswith('150') else (C(0) if c.startswith('200') else C(7)))
        for c in order]
ax2.bar(xs, v, color=cols, alpha=0.55, edgecolor=cols, linewidth=0.5, width=0.72)
ax2.set_xticks(xs); ax2.set_xticklabels([c.split('_')[1][:2] for c in order], rotation=90, fontsize=5.6)
ax2.set_ylim(0, 1.05); ax2.set_ylabel('callouts found')
ax2.axhline(1.0, color='0.4', linewidth=0.5, linestyle=':')
for i in range(4):
    ax2.annotate('', xy=(i * 4 + 3.55, 1.02), xytext=(i * 4 - 0.55, 1.02),
                 arrowprops=dict(arrowstyle='-', linewidth=0.6, color='0.45'))
    ax2.text(i * 4 + 1.5, 1.045, ['100 dpi', '150', '200', '300'][i], ha='center', fontsize=5.8,
             color='0.35')
ax2.set_ylim(0, 1.13)
panel(ax2, 'b', dx=-0.24, dy=1.20)
for xi, (c, val) in enumerate(zip(order, v)):
    if val < 0.995:
        ax2.text(xi, val + 0.02, f'{val:.2f}', ha='center', fontsize=5.0, rotation=90, va='bottom')

ax3 = fig.add_axes([0.575, 0.075, 0.415, 0.225])
ax3.axis('off')
ax3.text(0.005, 0.99, 'Why the callout page is the right test bed', fontsize=7.0, va='top')
lines = [
 '54 values, one per callout; 16 distinct values;',
 'six build stages, one panel each;',
 'text layer reproduces all 54 values exactly,',
 '   so the reference is machine-checkable;',
 'values are decimal with 0–1 places and a sign,',
 '   so a one-character error stays a valid number;',
 'the page is also what a plant actually files:',
 '   a CMM result pasted into a problem sheet.',
]
for i, t in enumerate(lines):
    ax3.text(0.005, 0.865 - 0.098 * i, t, fontsize=6.0, va='top')
panel(ax3, 'c', dx=-0.06, dy=1.10)
save(fig, 'png/fig05_testbed.png')
