"""Fig. 14 -- Transfer to the other digit tokens: accuracy by kind, committed error by policy, and the
dependence between channels that agreement has to survive.

Full-width composite (6.8 in), three panels.
"""
import json, os
import matplotlib.pyplot as plt
import numpy as np
from _style import *
pro_style()
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
B = json.load(open(os.path.join(R, 'a7_tokens.json')))
A1 = json.load(open(os.path.join(R, 'a1_summary.json')))

PY = os.path.join(R, 'a13_token_dependence.json')
DEP = json.load(open(PY)) if os.path.exists(PY) else None

fig, axes = plt.subplots(1, 3, figsize=(6.80, 2.52),
                         gridspec_kw=dict(width_ratios=[1.10, 1.0, 0.95], wspace=0.46,
                                          left=0.062, right=0.985, bottom=0.245, top=0.775))

KINDS = ['numeral', 'week_code', 'alnum']
KN = {'numeral': 'numeral', 'week_code': 'week code', 'alnum': 'alnum'}
KS = ['tess', 'easy', 'vlm']
NAMES = {'tess': 'Tesseract', 'easy': 'EasyOCR', 'vlm': 'SmolVLM'}
COL = {'tess': TESS, 'easy': EASY, 'vlm': VLM}

# (a) accuracy by kind, channels grouped
ax = axes[0]
w = 0.25
for j, k in enumerate(KS):
    v = [B[kk]['acc_' + k] for kk in KINDS]
    ax.bar(np.arange(3) + (j - 1) * w, v, width=w, color=COL[k], label=NAMES[k], zorder=3)
ax.set_xticks(np.arange(3)); ax.set_xticklabels([KN[kk] for kk in KINDS])
ax.set_ylim(0, 1.14); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_ylabel('exact-match accuracy')
ax.annotate('alphanumeric strings\nare the hard field', xy=(2, 0.56), xytext=(1.54, 0.86),
            fontsize=6.3, color='0.35', ha='center', va='bottom',
            arrowprops=dict(arrowstyle='-', color='0.55', linewidth=0.5))
ygrid(ax); ptitle(ax, 'a', 'accuracy by token kind')

# (b) committed error by policy and kind, linear axis so a zero is a zero
ax = axes[1]
pols = [('single-tess', 'Tess.'), ('single-easy', 'Easy'), ('single-vlm', 'VLM'),
        ('majority-2of3', '2-of-3')]
for kk, col, mk in [('numeral', EASY, 'o'), ('week_code', ACC, 's'), ('alnum', TESS, '^')]:
    v = [B[kk][p]['committed_error'] for p, _ in pols]
    ax.plot(np.arange(len(pols)), v, marker=mk, color=col, markeredgecolor='white',
            markeredgewidth=0.5, label=KN[kk], zorder=3)
ax.set_xticks(np.arange(len(pols))); ax.set_xticklabels([n for _, n in pols])
ax.set_ylim(0, 0.72); ax.set_yticks([0, 0.2, 0.4, 0.6])
ax.set_ylabel('committed error rate')
ygrid(ax); ptitle(ax, 'b', 'what voting removes')

# (c) dependence: observed joint error against the product of the marginals
ax = axes[2]
pr = A1['pairs']
keys = ['tess-easy', 'tess-vlm', 'easy-vlm']
labs = ['Tess.\nEasy', 'Tess.\nVLM', 'Easy\nVLM']
obs = [pr[k]['joint_error'] for k in keys]
ind = [pr[k]['independent'] for k in keys]
xs = np.arange(3); w = 0.34
ax.bar(xs - w / 2, ind, width=w, color='0.80', edgecolor='0.40', linewidth=0.5, zorder=3,
       label='if independent')
ax.bar(xs + w / 2, obs, width=w, color=TESS, edgecolor='0.25', linewidth=0.5, zorder=3,
       label='observed')
for x, o, i in zip(xs, obs, ind):
    ax.text(x + w / 2, o + 0.0012, f'{o / i:.1f}×', ha='center', va='bottom', fontsize=6.6,
            color=TESS)
ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=6.6)
ax.set_ylabel('joint error rate'); ax.set_ylim(0, 0.056)
ax.set_yticks([0, 0.02, 0.04])
ygrid(ax); ptitle(ax, 'c', 'errors travel together')

figlegend(fig, [(COL[k], MK[k], NAMES[k]) for k in KS], y=0.965)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(facecolor='0.80', edgecolor='0.40', label='if independent'),
                    Patch(facecolor=TESS, edgecolor='0.25', label='observed'),
                    plt.Line2D([], [], color='0.45', linewidth=0, marker='$×$', markersize=6,
                               label='observed / independent')],
           loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.035),
           handlelength=1.1, columnspacing=1.6, handletextpad=0.5)
save(fig, 'png/fig14_tokens_full.png')
save(fig, 'png/fig14_tokens.png')
