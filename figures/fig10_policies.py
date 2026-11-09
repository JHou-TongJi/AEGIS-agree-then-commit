"""Fig. 10 -- Policies replayed on the logged readings: coverage against committed error, measured
cost, and how many channel calls the cascade makes.

Full-width composite (6.8 in), three panels.
"""
import json, os
import matplotlib.pyplot as plt
import numpy as np
from _style import *
pro_style()
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
P = json.load(open(os.path.join(R, 'a3_policies.json')))
AG = json.load(open(os.path.join(R, 'a4_agent_range.json')))['3.0']

fig, axes = plt.subplots(1, 3, figsize=(6.80, 2.55), gridspec_kw=dict(
    width_ratios=[1.45, 1.0, 0.78], wspace=0.60, left=0.062, right=0.988,
    bottom=0.235, top=0.780))

# (a) coverage against committed error. The vote and the cascade land on the same point, so the
# labels sit in the empty left half and are joined to their markers by leaders.
ax = axes[0]
assert P['majority-2of3']['coverage'] == P['cascade(easy>tess>vlm)']['coverage']
LEAD = dict(arrowstyle='-', color='0.55', linewidth=0.55, shrinkA=2, shrinkB=3)
LX = 0.615
LAB = [('single-tess', 'Tesseract', (LX, 0.185)),
       ('single-easy', 'EasyOCR', (LX, 0.0330)),
       ('single-vlm', 'SmolVLM', (LX, 0.0125)),
       ('cascade+rerender', 'cascade + re-render', (LX, 0.0040)),
       ('majority-2of3', 'vote = cascade', (LX, 0.00132))]
for k, name, xyt in LAB:
    v = P[k]
    ax.scatter(v['coverage'], v['committed_error'], s=22, color=EASY, edgecolor='white',
               linewidth=0.5, zorder=4, clip_on=False)
    ax.annotate(name, (v['coverage'], v['committed_error']), xytext=xyt, fontsize=6.6,
                color='0.22', ha='left', va='center', arrowprops=LEAD)
v = P['unanimous-3of3']
ax.scatter(v['coverage'], 7e-5, s=22, color='0.55', edgecolor='white', linewidth=0.5, zorder=4)
ax.annotate('unanimous, no errors', (v['coverage'], 7e-5), xytext=(LX, 0.00052), fontsize=6.6,
            color='0.35', ha='left', va='center', arrowprops=dict(LEAD, color='0.7'))
v = AG['agent(cascade+domain+rerender)']
ax.scatter(v['coverage'], v['committed_error'], s=42, marker='D', color=VLM, edgecolor='white',
           linewidth=0.5, zorder=5)
ax.annotate('agent', (v['coverage'], v['committed_error']), xytext=(0.998, 0.00060), fontsize=6.8,
            color=VLM, ha='center', va='top', arrowprops=dict(LEAD, color=VLM,
                                                              shrinkA=3, shrinkB=5))
ax.set_yscale('log'); ax.set_xlim(0.60, 1.055); ax.set_ylim(6e-5, 0.55)
ax.set_xlabel('coverage (share of values committed)'); ax.set_ylabel('committed error rate')
ax.axhline(1e-2, color='0.65', linestyle=(0, (4, 2)), linewidth=0.6)
ax.text(1.050, 1.16e-2, '1 %', fontsize=6.2, color='0.45', va='bottom', ha='right')
ax.yaxis.grid(True, which='major', color='0.90', linewidth=0.5)
ptitle(ax, 'a', 'coverage bought with error')

# (b) seconds per value
ax = axes[1]
rows = [('EasyOCR only', P['single-easy']['cost_s'], 'single'),
        ('Tesseract only', P['single-tess']['cost_s'], 'single'),
        ('cascade', P['cascade(easy>tess>vlm)']['cost_s'], 'cascade'),
        ('agent', AG['agent(cascade+domain+rerender)']['cost_s'], 'agent'),
        ('SmolVLM only', P['single-vlm']['cost_s'], 'single'),
        ('cascade + re-render', P['cascade+rerender']['cost_s'], 'cascade'),
        ('2-of-3 vote', P['majority-2of3']['cost_s'], 'vote'),
        ('unanimous 3-of-3', P['unanimous-3of3']['cost_s'], 'vote')]
COLK = {'single': '0.72', 'cascade': EASY, 'agent': VLM, 'vote': ACC}
yy = np.arange(len(rows))
for i, (name, v, kind) in enumerate(rows):
    ax.barh(i, v, height=0.60, color=COLK[kind], zorder=3)
    ax.text(v + 0.045, i, f'{v:.2f}', va='center', fontsize=6.6, color='0.2')
ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows])
ax.invert_yaxis(); ax.set_xlabel('measured seconds per value'); ax.set_xlim(0, 2.42)
ax.set_ylim(len(rows) - 0.4, -0.6)
xgrid(ax); ptitle(ax, 'b', 'cost of the same decisions')

# (c) call histogram
ax = axes[2]
h = P['cascade_calls_histogram']
vals = [h[str(k)] / 864 for k in (1, 2, 3)]
ax.bar(np.arange(3), vals, width=0.52, color=EASY, zorder=3)
for x, v2 in enumerate(vals):
    ax.text(x, v2 + 0.022, f'{v2:.0%}', ha='center', va='bottom', fontsize=7.0, color='0.2')
ax.annotate('two readers settle\ntwo thirds of values', xy=(1, 0.70), xytext=(1.0, 0.94),
            fontsize=6.4, color='0.35', ha='center', va='top',
            arrowprops=dict(arrowstyle='-', color='0.55', linewidth=0.5))
ax.set_xticks(np.arange(3)); ax.set_xticklabels(['one', 'two', 'three'])
ax.set_xlabel('channel calls per value'); ax.set_ylim(0, 1.06); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_ylabel('share of values')
ygrid(ax); ptitle(ax, 'c', 'how often the third reader is called')

save(fig, 'png/fig10_policies_full.png')
save(fig, 'png/fig10_policies.png')
