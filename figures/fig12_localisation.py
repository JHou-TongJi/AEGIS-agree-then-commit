"""Fig. 12 -- Localisation: the same callout cropped on the reference frame and shifted; channel
accuracy and silent rate under both crops; the agent with re-render versus re-crop."""
import json, os
import cv2
import matplotlib.pyplot as plt
import numpy as np
from _style import *
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = json.load(open(os.path.join(REPO, 'results', 'a12_localisation.json')))
B = json.load(open(os.path.join(REPO, 'data', 'callouts', 'boxes.json')))
CROPS = os.path.join(REPO, 'data', 'crops')

fig = plt.figure(figsize=(7.02, 2.25))
for j, name in enumerate(['ref', 'shift']):
    c = cv2.imread(os.path.join(CROPS, f'callout01_200_clean_{name}.png'))[:, :, ::-1]
    ax = fig.add_axes([0.01 + j * 0.135, 0.30, 0.125, 0.50]); ax.imshow(c); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(['reference crop', 'shifted crop'][j], fontsize=6.6)
    ax.text(0.5, -0.30, '200 dpi, clean', transform=ax.transAxes, ha='center', va='top', fontsize=5.4, color='0.4')
    ax.text(0.5, -0.12, ['Tesseract reads 4.3', 'Tesseract reads 1.3'][j], transform=ax.transAxes,
            ha='center', va='top', fontsize=6.2, color=C(3) if j == 0 else C(2))
fig.text(0.01, 0.92, '(a)', fontsize=8)

ax = fig.add_axes([0.355, 0.24, 0.28, 0.58])
ks = ['tess', 'easy', 'vlm']; xs = np.arange(3); w = 0.36
ax.bar(xs - w / 2, [J['reference'][k]['acc'] for k in ks], width=w, color='0.65', edgecolor='0.45',
       linewidth=0.5, label='reference crop')
ax.bar(xs + w / 2, [J['shifted'][k]['acc'] for k in ks], width=w, color=C(0), alpha=0.65,
       edgecolor=C(0), linewidth=0.5, label='shifted crop')
for x, k in zip(xs, ks):
    ax.text(x + w / 2, J['shifted'][k]['acc'] + 0.01, f"silent {100*J['shifted'][k]['silent']:.1f}%",
            ha='center', fontsize=5.0, rotation=90, va='bottom')
ax.set_xticks(xs); ax.set_xticklabels(['Tesseract', 'EasyOCR', 'SmolVLM'], fontsize=6.2)
ax.set_ylim(0.5, 1.30); ax.set_ylabel('accuracy')
ax.legend(frameon=False, fontsize=5.6, loc='upper left', ncol=1)
fig.text(0.30, 0.92, '(b)', fontsize=8)

ax = fig.add_axes([0.725, 0.24, 0.265, 0.58])
names = [('cascade|R=3', 'cascade'), ('cascade+rerender|R=3', '+ re-render'), ('cascade+recrop|R=3', '+ re-crop')]
v = [J['recrop'][k]['escalated'] for k, _ in names]
ax.bar(np.arange(3), v, color=[C(7), C(4), C(2)], alpha=0.65, edgecolor=[C(7), C(4), C(2)], linewidth=0.5)
for x, (k, _) in enumerate(names):
    ax.text(x, v[x] + 0.8, f"{v[x]}", ha='center', fontsize=6.2)
    ax.text(x, v[x] + 4.2, f"{J['recrop'][k]['cost_s']:.2f} s/value", ha='center', fontsize=5.4, color='0.35')
ax.set_xticks(np.arange(3)); ax.set_xticklabels([n for _, n in names], fontsize=6.2)
ax.set_ylabel('escalations of 864'); ax.set_ylim(0, 44)
fig.text(0.67, 0.92, '(c)', fontsize=8)
save(fig, 'png/fig12_localisation.png')
