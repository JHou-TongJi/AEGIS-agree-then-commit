"""Fig. 9 -- Self-confidence against corroboration: distributions, ROC, and the trivial-confident case.

Full-width composite (6.8 in), three panels.
"""
import json, os, sys
import matplotlib.pyplot as plt
import numpy as np
from _style import *
pro_style()
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts')); sys.path.insert(0, os.path.join(REPO, 'src'))
from common import load_a, auroc_np  # noqa
import a2_detectors as A2

R = os.path.join(REPO, 'results')
J = json.load(open(os.path.join(R, 'a2_detectors.json')))
d = load_a()

fig, axes = plt.subplots(1, 3, figsize=(6.80, 2.42),
                         gridspec_kw=dict(wspace=0.40, left=0.062, right=0.988,
                                          bottom=0.215, top=0.760))

# (a) EasyOCR confidence on the reads it committed: correct against wrong
ax = axes[0]
s = A2.signals(d, 'easy')
bins = np.linspace(0, 1, 26)
ax.hist(s.loc[s.wrong == 0, 'self'], bins=bins, color=EASY, alpha=0.85, edgecolor='white',
        linewidth=0.35, density=True, label='correct')
ax.hist(s.loc[s.wrong == 1, 'self'], bins=bins, color=TESS, alpha=0.85, edgecolor='white',
        linewidth=0.35, density=True, label='wrong')
ax.set_xlabel('EasyOCR confidence on the value it returned')
ax.set_ylabel('density (per committed value)')
ax.set_xlim(0, 1.0); ax.set_ylim(0, 17)
ax.annotate(f"AUROC {J['callouts']['easy']['auroc_self']:.2f}", xy=(0.055, 15.0), fontsize=7.0,
            color='0.25')
ax.annotate('wrong values are\nas confident as right ones', xy=(0.985, 13.2), xytext=(0.10, 12.6),
            fontsize=6.4, color='0.30', ha='left',
            arrowprops=dict(arrowstyle='-', color='0.55', linewidth=0.5,
                            connectionstyle='angle3,angleA=0,angleB=90'))
ygrid(ax); ptitle(ax, 'a', 'confidence does not separate')

# (b) ROC of own confidence against corroboration
ax = axes[1]
for k, col in [('easy', EASY), ('vlm', VLM)]:
    s2 = A2.signals(d, k)
    for colname, ls, lw in [('self', (0, (1, 1.6)), 1.1), ('agree', '-', 1.7)]:
        thr = np.unique(-s2[colname])
        if len(thr) > 200:
            thr = np.quantile(thr, np.linspace(0, 1, 200))
        y = s2.wrong.to_numpy()
        sc = -s2[colname].to_numpy()
        tpr = [(sc >= t).dot(y) / max(1, y.sum()) for t in thr]
        fpr = [(sc >= t).dot(1 - y) / max(1, (1 - y).sum()) for t in thr]
        ax.plot(fpr, tpr, linestyle=ls, color=col, linewidth=lw, label=f'{k} {colname}')
ax.plot([0, 1], [0, 1], color='0.65', linewidth=0.6, linestyle=(0, (4, 2)), label='chance')
ax.set_xlabel('false-flag rate'); ax.set_ylabel('share of silent errors caught')
ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)

ax.text(0.60, 0.93, 'corroboration', fontsize=6.4, color='0.25', va='top', ha='left')
ax.text(0.36, 0.10, 'own confidence', fontsize=6.4, color='0.25')
ygrid(ax); xgrid(ax, '0.93'); ptitle(ax, 'b', 'what catches them')

# (c) areas under the curve
ax = axes[2]
ks = ['easy', 'vlm']; labs = ['EasyOCR', 'SmolVLM']
xs = np.arange(2); w = 0.26
series = [('self', 'own confidence', '0.80'), ('agree', 'corroboration', ACC),
          ('agree_self', 'corroboration + confidence', '#b9a3d0')]
for j, (colname, tag, col) in enumerate(series):
    v = [J['callouts'][k]['auroc_' + colname] for k in ks]
    ax.bar(xs + (j - 1) * w, v, width=w, color=col, label=tag, zorder=3)
    for x, val in zip(xs + (j - 1) * w, v):
        ax.text(x, val + 0.022, f'{val:.2f}', ha='center', va='bottom', fontsize=6.4, color='0.2')
ax.axhline(0.5, color='0.45', linewidth=0.6, linestyle=(0, (4, 2)), label='chance')

ax.set_xticks(xs); ax.set_xticklabels(labs); ax.set_ylim(0, 1.24); ax.set_yticks([0, 0.5, 1.0])
ax.set_ylabel('AUROC for the silent error')
ygrid(ax); ptitle(ax, 'c', 'area under the curve')

figlegend(fig, [(EASY, 's', 'EasyOCR'), (VLM, '^', 'SmolVLM')], y=0.975)
from matplotlib.lines import Line2D
fig.legend(handles=[Line2D([], [], color=EASY, linestyle='-', linewidth=1.7, label='corroboration'),
                    Line2D([], [], color=EASY, linestyle=(0, (1, 1.6)), linewidth=1.1, label='own confidence'),
                    Line2D([], [], color='0.65', linestyle=(0, (4, 2)), linewidth=0.8, label='chance')],
           loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.035),
           handlelength=1.7, columnspacing=1.5, handletextpad=0.45)
save(fig, 'png/fig09_detection_full.png')
save(fig, 'png/fig09_detection.png')
