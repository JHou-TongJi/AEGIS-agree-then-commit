"""Fig. 11 -- Where the errors are: per-callout wrong reads over the 16 conditions, by channel,
and the agent's outcome on each callout."""
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from _style import *
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
P = pd.read_csv(os.path.join(R, 'a9_per_callout.csv'), dtype={'gold': str}).sort_values('idx')

M = np.vstack([P.tess_wrong, P.easy_wrong, P.vlm_wrong]).astype(float)
fig = plt.figure(figsize=(7.02, 1.95))
ax = fig.add_axes([0.085, 0.36, 0.895, 0.50])
cm = LinearSegmentedColormap.from_list('w', ['#ffffff', C(3)])
im = ax.imshow(M, aspect='auto', cmap=cm, vmin=0, vmax=16, interpolation='nearest')
ax.set_yticks([0, 1, 2]); ax.set_yticklabels(['Tesseract', 'EasyOCR', 'SmolVLM'], fontsize=6.4)
ax.set_xticks(np.arange(54)); ax.set_xticklabels(P.gold.astype(str), rotation=90, fontsize=4.9)
for j in range(54):
    for i in range(3):
        if M[i, j] > 0:
            ax.text(j, i, int(M[i, j]), ha='center', va='center', fontsize=4.4,
                    color='white' if M[i, j] > 9 else '0.15')
for b in range(1, 6):
    ax.axvline(b * 9 - 0.5, color='0.25', linewidth=0.6)
for b, name in enumerate(['KW40/2', 'KW01', 'KW04/5', 'KW05/5', 'KW06/1', 'KW10/1']):
    ax.text(b * 9 + 4, -0.95, name, ha='center', fontsize=5.8, color='0.3')
ax.tick_params(length=0)
ax2 = fig.add_axes([0.085, 0.165, 0.895, 0.085])
outc = np.where(P.agent_wrong > 0, 2, np.where(P.agent_escalated > 0, 1, 0))
cm2 = LinearSegmentedColormap.from_list('o', ['#ffffff', C(1), C(3)], N=3)
ax2.imshow(outc[None, :], aspect='auto', cmap=cm2, vmin=0, vmax=2, interpolation='nearest')
ax2.set_yticks([0]); ax2.set_yticklabels(['agent'], fontsize=6.4); ax2.set_xticks([])
for j in range(54):
    if P.agent_escalated.iloc[j] > 0:
        ax2.text(j, 0, int(P.agent_escalated.iloc[j]), ha='center', va='center', fontsize=4.6)
    if P.agent_wrong.iloc[j] > 0:
        ax2.text(j, 0, '×', ha='center', va='center', fontsize=6.0, color='white')
for b in range(1, 6):
    ax2.axvline(b * 9 - 0.5, color='0.25', linewidth=0.6)
ax2.tick_params(length=0)
fig.text(0.085, 0.06, 'cell: number of the 16 renderings on which the channel misreads the callout;   '
         'agent row: orange = escalations (count), red × = a committed wrong value', fontsize=5.8,
         color='0.3')
save(fig, 'png/fig11_per_callout.png')
