"""House style: flat Matplotlib schematics, tab10 at low alpha, 400 dpi."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 7.4, 'axes.titlesize': 8.0,
    'axes.labelsize': 7.6, 'xtick.labelsize': 7.0, 'ytick.labelsize': 7.0,
    'legend.fontsize': 6.8, 'axes.linewidth': 0.7, 'xtick.major.width': 0.6,
    'ytick.major.width': 0.6, 'lines.linewidth': 1.1, 'lines.markersize': 3.2,
    'axes.spines.top': False, 'axes.spines.right': False, 'figure.dpi': 400,
    'savefig.dpi': 400, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.03,
    'mathtext.default': 'regular', 'axes.grid': False, 'pdf.fonttype': 42,
})
_cm = plt.get_cmap('tab10')
C = lambda i: _cm(i)[:3]

# print palette: one fixed colour per channel, used by every figure of the paper
PAL = {'tess': '#a63a2e', 'easy': '#1f5f99', 'vlm': '#2c7a4b', 'acc': '#6b4f9e',
       'grey': '#9a9a9a', 'ink': '#333333'}
TESS, EASY, VLM, ACC, GREY = PAL['tess'], PAL['easy'], PAL['vlm'], PAL['acc'], PAL['grey']
MK = {'tess': 'o', 'easy': 's', 'vlm': '^'}


def pro_style():
    """Typography and line weights for the full-width (6.8 in) composite figures."""
    plt.rcParams.update({
        'font.size': 7.4, 'axes.titlesize': 7.9, 'axes.labelsize': 7.4,
        'xtick.labelsize': 6.9, 'ytick.labelsize': 6.9, 'legend.fontsize': 6.9,
        'axes.linewidth': 0.75, 'xtick.major.width': 0.7, 'ytick.major.width': 0.7,
        'xtick.major.size': 2.6, 'ytick.major.size': 2.6,
        'xtick.minor.size': 1.4, 'ytick.minor.size': 1.4,
        'lines.linewidth': 1.25, 'lines.markersize': 3.5,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.axisbelow': True,
        'patch.linewidth': 0.6,
    })


def ygrid(ax, color='0.90'):
    ax.yaxis.grid(True, color=color, linewidth=0.5)
    ax.set_axisbelow(True)


def xgrid(ax, color='0.90'):
    ax.xaxis.grid(True, color=color, linewidth=0.5)
    ax.set_axisbelow(True)


def ptitle(ax, letter, text):
    """Panel label and title on one line, flush with the left spine."""
    ax.set_title(f'({letter}) {text}', loc='left', pad=5, fontsize=7.9, color='black')


def figlegend(fig, entries, ncol=None, y=1.0, handlelength=1.7):
    """One legend for the whole figure, from (colour, marker, label) triples."""
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=c, marker=m, markersize=3.4, markeredgecolor='white',
                markeredgewidth=0.45, linewidth=1.25 if m else 0, label=lab)
         for c, m, lab in entries]
    fig.legend(handles=h, loc='upper center', ncol=ncol or len(entries), frameon=False,
               bbox_to_anchor=(0.5, y), handlelength=handlelength, columnspacing=1.5,
               handletextpad=0.5, borderaxespad=0.1)


def panel(ax, letter, dx=-0.13, dy=1.05):
    ax.text(dx, dy, f'({letter})', transform=ax.transAxes, fontsize=8, va='top', ha='left')


def save(fig, path):
    fig.savefig(path)
    plt.close(fig)
    print('wrote', path)


def save_panels(fig, groups, stem):
    """Save each group of axes (one panel, possibly with a twin axis) as its own image,
    named <stem>_a.png, _b.png, ... so each can be placed at column width."""
    from matplotlib.transforms import Bbox
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    every = list(fig.axes)
    boxes = [Bbox.union([a.get_tightbbox(r) for a in axs]) for axs in groups]
    for letter, axs, bb in zip('abcdef', groups, boxes):
        bb = bb.transformed(fig.dpi_scale_trans.inverted()).padded(0.04)
        # hide the other panels so text that spills across panel borders is not cropped in
        for a in every:
            a.set_visible(a in axs)
        fig.savefig(f'{stem}_{letter}.png', bbox_inches=bb)
        print('wrote', f'{stem}_{letter}.png')
    for a in every:
        a.set_visible(True)
