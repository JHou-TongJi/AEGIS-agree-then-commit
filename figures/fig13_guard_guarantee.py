"""Fig. 13 -- The guard and the guarantee: (a) sensitivity of the agent to the declared plausible
range; (b) the calibration floor 1/(n+1); (c) realised risk against the requested bound.

Full-width composite (6.8 in), three panels.
"""
import json, os
import matplotlib.pyplot as plt
import numpy as np
from _style import *
pro_style()
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
G = json.load(open(os.path.join(R, 'a4_agent_range.json')))
C5 = json.load(open(os.path.join(R, 'a5_crc.json')))

fig, axes = plt.subplots(1, 3, figsize=(6.80, 2.52),
                         gridspec_kw=dict(width_ratios=[1.12, 1.0, 1.0], wspace=0.62,
                                          left=0.062, right=0.972, bottom=0.225, top=0.775))

# (a) range sensitivity: coverage on the left axis, escalations on the right
ax = axes[0]
keys = ['1.0', '1.5', '1.6', '1.7', '2.0', '3.0', '5.0', '6.9', '7.0', '10.0']
xs = np.array([float(k) for k in keys])
cov = np.array([G[k]['agent(cascade+domain+rerender)']['coverage'] for k in keys])
esc = np.array([G[k]['agent(cascade+domain+rerender)']['escalated'] for k in keys])
ax.axvspan(1.6, 6.9, color='0.92', zorder=0)
ax.plot(xs, cov, marker='o', color=VLM, markeredgecolor='white', markeredgewidth=0.5, zorder=4,
        label='coverage')
ax.set_xscale('log'); ax.set_xlabel('declared plausible range $R$ (mm)')
ax.set_ylabel('coverage', color=VLM); ax.set_ylim(0.954, 1.014)
ax.set_xticks([1, 2, 3, 5, 7, 10]); ax.set_xticklabels(['1', '2', '3', '5', '7', '10'])
ax.set_xticks([], minor=True)
ax.tick_params(axis='y', colors=VLM)
ax.text(3.2, 0.9650, 'decision unchanged\nfor $1.6\\leq R\\leq 6.9$', fontsize=6.2,
        color='0.32', ha='center', va='bottom',
        bbox=dict(boxstyle='square,pad=0.25', facecolor='white', edgecolor='none', alpha=0.9))
ax2 = ax.twinx()
ax2.plot(xs, esc, marker='s', markersize=3.2, color=TESS, linestyle=(0, (3, 1.6)), linewidth=1.1,
         label='escalations', zorder=4)
ax2.set_ylabel('escalated', color=TESS); ax2.set_ylim(0, 92); ax2.set_yticks([0, 20, 40, 60, 80])
ax2.tick_params(axis='y', colors=TESS)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(True); ax2.spines['right'].set_color(TESS)
ax2.spines['right'].set_linewidth(0.75)
ptitle(ax, 'a', 'the range is a policy')

# (b) the calibration floor
ax = axes[1]
n = np.arange(4, 200)
ax.plot(n, 1 / (n + 1), color='0.35', linewidth=1.2, label='$1/(n+1)$')
for lev, lab in [(0.10, '10 %'), (0.05, '5 %'), (0.02, '2 %')]:
    ax.axhline(lev, color='0.72', linestyle=(0, (4, 2)), linewidth=0.6)
    ax.text(225, lev * 1.10, lab, fontsize=6.2, color='0.45', ha='right', va='bottom')
for nn, lab, dy in [(90, 'A: 90 units', (7, 4)), (6, 'one condition', (9, 2))]:
    ax.scatter([nn], [1 / (nn + 1)], s=26, color=EASY, edgecolor='white', linewidth=0.5, zorder=4)
    ax.annotate(lab, (nn, 1 / (nn + 1)), fontsize=6.4, color=EASY, xytext=dy,
                textcoords='offset points', ha='left', va='bottom')
nb = np.arange(26, 33)
ax.plot(nb, 1 / (nb + 1), color=VLM, linewidth=3.0, solid_capstyle='butt', zorder=4)
ax.annotate('B: 26-32 units', (26, 1 / 27), fontsize=6.4, color=VLM, xytext=(-7, -6),
            textcoords='offset points', va='top', ha='right')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('calibration units $n$'); ax.set_ylabel('smallest certifiable risk')
ax.set_ylim(4e-3, 0.30); ax.set_xlim(4, 240)
ptitle(ax, 'b', 'the floor is $1/(n+1)$')

# (c) realised risk against the requested bound
ax = axes[2]
ax.plot([0, 0.22], [0, 0.22], color='0.65', linestyle=(0, (4, 2)), linewidth=0.7, zorder=1)
for key, col, mk, lab in [('A', EASY, 'o', 'callout page (A)'),
                          ('B', VLM, 's', 'digit tokens (B)')]:
    rows = [r for r in C5[key] if r['mean_risk'] is not None]
    a = [r['alpha'] for r in rows]; m = [r['mean_risk'] for r in rows]
    ax.plot(a, m, marker=mk, color=col, markeredgecolor='white', markeredgewidth=0.5,
            label=lab, zorder=3)
    # mark the bounds that could not be certified at all
    nf = [r for r in rows if r['infeasible_folds'] == r['n_folds']]
    if nf:
        ax.scatter([r['alpha'] for r in nf], [3.5e-3] * len(nf), marker='x', s=14, color=col,
                   linewidth=0.9, zorder=3, clip_on=False)
ax.set_xlabel('requested bound $\\alpha$'); ax.set_ylabel('realised committed risk')
ax.set_xlim(0, 0.215); ax.set_ylim(0, 0.215)
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])
ax.text(0.155, 0.172, 'risk $=\\alpha$', fontsize=6.3, color='0.45', rotation=39,
        rotation_mode='anchor', ha='left', va='bottom')
ax.annotate('infeasible in every fold', xy=(0.035, 3.5e-3), xytext=(0.088, 0.014), fontsize=6.3,
            color='0.4', ha='left', va='center',
            arrowprops=dict(arrowstyle='-', color='0.6', linewidth=0.5))
ygrid(ax); ptitle(ax, 'c', 'realised against requested')

figlegend(fig, [(EASY, 'o', 'callout page (A), leave-one-regime-out'),
                (VLM, 's', 'digit tokens (B), leave-one-document-out')], y=0.965)
save(fig, 'png/fig13_guard_guarantee_full.png')
save(fig, 'png/fig13_guard_guarantee.png')
