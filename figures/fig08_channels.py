"""Fig. 8 -- Channel anatomy on the 864 reads: accuracy against resolution, accuracy against
degradation, and what happens to the reads a channel gets wrong.

Drawn as one full-width composite (6.8 in), three panels side by side, one type scale.
"""
import json, os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _style import *

pro_style()
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
S = json.load(open(os.path.join(R, 'a1_summary.json')))
D = pd.read_csv(os.path.join(R, 'a1_by_condition.csv'))
KS = ['tess', 'easy', 'vlm']
NAMES = {'tess': 'Tesseract', 'easy': 'EasyOCR', 'vlm': 'SmolVLM'}
COL = {'tess': TESS, 'easy': EASY, 'vlm': VLM}

fig, axes = plt.subplots(1, 3, figsize=(6.80, 2.42),
                         gridspec_kw=dict(wspace=0.40, left=0.062, right=0.988,
                                          bottom=0.215, top=0.760))

# (a) accuracy against resolution, averaged over the four degradations
ax = axes[0]
dpis = [100, 150, 200, 300]
for k in KS:
    v = [D[(D.channel == k) & (D.by == 'dpi') & (D.level == str(d))].acc.values[0] for d in dpis]
    ax.plot(dpis, v, marker=MK[k], color=COL[k], markeredgecolor='white', markeredgewidth=0.5,
            label=NAMES[k], clip_on=False, zorder=3)
    ax.annotate(NAMES[k], (dpis[-1], v[-1]), xytext=(5, 0), textcoords='offset points',
                fontsize=6.6, color=COL[k], va='center')
ax.set_xscale('log'); ax.set_xticks(dpis); ax.set_xticklabels([str(d) for d in dpis])
ax.set_xticks([], minor=True)
ax.set_xlim(88, 430); ax.set_ylim(0.55, 1.02)
ax.set_xlabel('render resolution (dpi)'); ax.set_ylabel('exact-match accuracy')
ygrid(ax); ptitle(ax, 'a', 'by resolution')

# (b) accuracy against degradation
ax = axes[1]
degs = ['clean', 'jpeg', 'blur', 'skew']
w = 0.25
for j, k in enumerate(KS):
    v = [D[(D.channel == k) & (D.by == 'deg') & (D.level == d)].acc.values[0] for d in degs]
    ax.bar(np.arange(4) + (j - 1) * w, v, width=w, color=COL[k], label=NAMES[k], zorder=3)
ax.set_xticks(np.arange(4)); ax.set_xticklabels(degs)
ax.set_ylim(0, 1.12); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_ylabel('exact-match accuracy')
ygrid(ax); ptitle(ax, 'b', 'by degradation')

# (c) what the wrong reads are
ax = axes[2]
sil = np.array([S[k]['silent'] for k in KS])
inv = np.array([S[k]['invalid'] for k in KS])
y = np.arange(3)[::-1]
ax.barh(y, inv, height=0.46, color='0.78', edgecolor='0.35', linewidth=0.6, zorder=3,
        label='format-rejected (refused)')
ax.barh(y, sil, left=inv, height=0.46, color=TESS, edgecolor='0.25', linewidth=0.5, zorder=3,
        label='silent (valid, wrong)')
for yi, k in zip(y, KS):
    i = KS.index(k)
    if inv[i] > 0.02:
        ax.text(inv[i] / 2, yi, f'{inv[i]:.0%}', ha='center', va='center', fontsize=6.5, color='0.15')
        ax.text(inv[i] + sil[i] + 0.008, yi, f'{sil[i]:.1%}', ha='left', va='center', fontsize=6.5,
                color=TESS)
    else:  # the fluent reader: nothing refused, every error silent
        ax.text(0.008, yi + 0.30, '0 % refused', ha='left', va='center', fontsize=6.4, color='0.45')
        ax.text(0.030, yi, f'{sil[i]:.1%} silent', ha='left', va='center', fontsize=6.5, color=TESS)
ax.set_yticks(y); ax.set_yticklabels([NAMES[k] for k in KS])
ax.set_xlim(0, 0.335); ax.set_ylim(-0.62, 2.62)
ax.set_xlabel('share of all 864 reads')
xgrid(ax); ptitle(ax, 'c', 'what a wrong read becomes')

figlegend(fig, [(COL[k], MK[k], NAMES[k]) for k in KS], y=0.975)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(facecolor='0.78', edgecolor='0.35', label='refused (sent to review)'),
                    Patch(facecolor=TESS, edgecolor='0.25', label='silent (admitted, wrong)')],
           loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.035),
           handlelength=1.1, columnspacing=1.6, handletextpad=0.5)
save(fig, 'png/fig08_channels_full.png')
save(fig, 'png/fig08_channels.png')
