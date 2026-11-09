"""Fig. 6 -- Where agree-then-commit sits in the plant's five-step document pipeline."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from _style import *

fig = plt.figure(figsize=(7.02, 2.35))
ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)


def box(x, y, w, h, t, col, a=0.13, fs=6.7):
    c = C(col)
    ax.add_patch(Rectangle((x, y), w, h, facecolor=c, alpha=a, edgecolor=c, linewidth=0.8))
    ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs, linespacing=1.3)


def ar(p, q, col='0.25', ls='-'):
    ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', mutation_scale=6.5,
                linewidth=0.7, color=col, linestyle=ls, shrinkA=1, shrinkB=1))


xs = [0.012, 0.207, 0.402, 0.597, 0.792]
names = ['1  file intake\nPDF, PPT, Excel,\nWord; pages and\nimages extracted',
         '2  standardisation\nunified page format,\nevidence atoms with\npositions',
         '3  extraction\nfield values read\nfrom atoms by the\nreaders',
         '4  storage\nrecord + audit trail\nin the quality\ndatabase',
         '5  automation\ncorrective workflow,\ndashboards,\nmaster list']
for i, (x, n) in enumerate(zip(xs, names)):
    box(x, 0.56, 0.180, 0.34, n, 7 if i != 2 else 0, 0.10 if i != 2 else 0.16)
    if i < 4:
        ar((x + 0.180, 0.73), (xs[i + 1], 0.73))
# the decision layer under step 3
box(0.330, 0.10, 0.325, 0.30,
    'agree-then-commit (this paper)\n\nthree readers  →  guards  →  corroboration\n'
    '→  calibrated threshold  →  commit | escalate', 2, 0.15, 6.6)
ar((0.492, 0.56), (0.492, 0.40))
ar((0.655, 0.30), (0.672, 0.56))
box(0.700, 0.10, 0.180, 0.26, 'review queue\nescalated values\nwith reason code\nand evidence', 3, 0.13, 6.5)
ar((0.655, 0.18), (0.700, 0.20))
ar((0.745, 0.36), (0.725, 0.56), col=C(3), ls=(0, (2, 1.4)))
ax.text(0.752, 0.46, 'reviewed value', fontsize=5.8, color=C(3), va='center')
ax.text(0.012, 0.955, 'Five-step pipeline of the plant\'s document programme; the decision layer replaces '
        'an unconditional commit inside step 3', fontsize=6.4, color='0.3')
save(fig, 'png/fig06_pipeline.png')
