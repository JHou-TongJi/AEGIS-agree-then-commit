"""Fig. 15 -- (a) risk-coverage of the corroboration threshold on both sets; (b) what the agent
escalates, by rendering condition; (c) the vote's committed-error share when the strongest reader is
replaced by a weaker one (independence model, results/a10_model.json).

Full-width composite (6.8 in), three panels.
"""
import json, os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _style import *
pro_style()
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
M = json.load(open(os.path.join(R, 'a10_model.json')))
P = pd.read_csv(os.path.join(R, 'a10_agent_by_cond.csv'))

fig, axes = plt.subplots(1, 3, figsize=(6.80, 2.62),
                         gridspec_kw=dict(width_ratios=[1.0, 1.25, 0.95], wspace=0.46,
                                          left=0.062, right=0.985, bottom=0.245, top=0.775))

# (a) risk against coverage as the threshold sweeps
ax = axes[0]
for key, col, mk, lab in [('A', EASY, 'o', 'callout page'), ('B', VLM, 's', 'digit tokens')]:
    c = M['curves'][key]
    cov = [r['coverage'] for r in c]; risk = [r['risk'] for r in c]
    ax.plot(cov, risk, color=col, marker=mk, markersize=2.4, markeredgewidth=0, label=lab, zorder=3)
ax.set_xlabel('coverage'); ax.set_ylabel('committed error rate')
ax.set_yscale('symlog', linthresh=1e-3); ax.set_ylim(0, 0.62); ax.set_xlim(0, 1.02)
ax.set_yticks([0, 1e-3, 1e-2, 1e-1])
ax.set_yticklabels(['0', '$10^{-3}$', '$10^{-2}$', '$10^{-1}$'])
ax.annotate('flat at zero,\nso it commits all', xy=(0.55, 3.0e-4), xytext=(0.03, 1.3e-3),
            fontsize=6.3, color='0.30', ha='left', va='top',
            arrowprops=dict(arrowstyle='-', color='0.55', linewidth=0.5))
ax.annotate('rises, so the calibration\nmust choose a threshold', xy=(0.60, 0.035),
            xytext=(0.03, 0.0065), fontsize=6.3, color='0.30', ha='left', va='top',
            arrowprops=dict(arrowstyle='-', color='0.55', linewidth=0.5))
ygrid(ax); ptitle(ax, 'a', 'threshold $\\lambda$ sweeps')

# (b) the agent per rendering: horizontal stacked bars, grouped by resolution
ax = axes[1]
order = ['100_clean', '100_jpeg', '100_blur', '100_skew', '150_clean', '150_jpeg', '150_blur',
         '150_skew', '200_clean', '200_jpeg', '200_blur', '200_skew', '300_clean', '300_jpeg',
         '300_blur', '300_skew']
P = P.set_index('cond').loc[order]
yy = np.arange(16)[::-1]
ax.barh(yy, P.escalated, height=0.66, color='0.80', edgecolor='0.45', linewidth=0.5, zorder=3,
        label='escalated to review')
ax.barh(yy, P.wrong, left=P.escalated, height=0.66, color=TESS, edgecolor='0.25', linewidth=0.5,
        zorder=3, label='wrong value committed')
ax.set_yticks(yy); ax.set_yticklabels([o.split('_')[1] for o in order], fontsize=6.4)
ax.set_ylim(-0.7, 16.4)
for i in range(4):
    ymid = 15 - (i * 4 + 1.5)
    ax.text(3.70, ymid, ['100', '150', '200', '300'][i], fontsize=6.4, color='0.35',
            va='center', ha='left')
    if i:
        ax.axhline(15 - i * 4 + 0.5, color='0.85', linewidth=0.6)
ax.set_xlim(0, 3.95); ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(['0', '1', '2', '3'])
ax.text(3.70, 16.1, 'dpi', fontsize=6.4, color='0.35', va='bottom', ha='left')
ax.set_xlabel('values of the 54 on that rendering')
xgrid(ax); ptitle(ax, 'b', 'what the agent escalates')

# (c) a weaker third reader
ax = axes[2]
sw = M['sweep']
ax.plot([s['e_vlm'] for s in sw], [100 * s['wrong_commit_indep'] for s in sw], marker='o',
        color=EASY, markeredgecolor='white', markeredgewidth=0.5, zorder=3)
obs = 100 * M['model']['observed_wrong_commit_share']
ax.axhline(obs, color=VLM, linestyle=(0, (4, 2)), linewidth=0.9, zorder=2)
ax.text(0.30, obs + 0.02, 'as measured\nwith SmolVLM', fontsize=6.4, color=VLM, va='bottom',
        ha='right')
ax.annotate('one value in four', xy=(0.25, 100 * sw[-1]['wrong_commit_indep']),
            xytext=(0.135, 0.80), fontsize=6.4, color='0.30', ha='center', va='bottom',
            arrowprops=dict(arrowstyle='-', color='0.55', linewidth=0.5))
ax.set_xlabel('error rate of the third reader'); ax.set_ylabel('wrong commits (% of values)')
ax.set_xlim(-0.005, 0.305); ax.set_ylim(0, 1.06)
ax.set_xticks([0, 0.1, 0.2, 0.3])
ygrid(ax); ptitle(ax, 'c', 'when the third reader weakens')

figlegend(fig, [(EASY, 'o', 'callout page'), (VLM, 's', 'digit tokens')], y=0.965)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(facecolor='0.80', edgecolor='0.45', label='escalated to review'),
                    Patch(facecolor=TESS, edgecolor='0.25', label='wrong value committed')],
           loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.035),
           handlelength=1.1, columnspacing=1.6, handletextpad=0.5)
save(fig, 'png/fig15_risk_coverage_full.png')
save(fig, 'png/fig15_risk_coverage.png')
