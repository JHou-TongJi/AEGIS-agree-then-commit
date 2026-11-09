"""Fig. 1 -- The agree-then-commit loop as a block diagram.

Online path (per field): page -> evidence localisation -> three independent channels ->
admission (canonicalise, format guard, range guard) -> corroboration -> decision.
A rejected value may trigger one re-render of the same evidence; otherwise it is escalated.
Offline path (once per deployment): conformal risk control on n exchangeable units yields
the threshold lambda-hat used by the decision node.

Monochrome, serif type, orthogonal connectors; coordinates in inches on a 7.0 x 3.4 in canvas.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

plt.rcParams.update({'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix',
                     'savefig.dpi': 400, 'pdf.fonttype': 42})

W, H = 7.0, 3.4
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off'); ax.set_xlim(0, W); ax.set_ylim(0, H)
K = 'black'
FS = 7.6
LW = 0.7
FILL = '0.93'          # light grey for the three channels, white elsewhere


def box(x, y, w, h, fill='white', lw=LW, ls='-'):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=K, linewidth=lw,
                           linestyle=ls, zorder=2))


def diamond(xc, yc, hw, hh):
    ax.add_patch(Polygon([(xc - hw, yc), (xc, yc + hh), (xc + hw, yc), (xc, yc - hh)],
                         closed=True, facecolor='white', edgecolor=K, linewidth=LW, zorder=2))


def text(x, y, s, fs=FS, **kw):
    kw.setdefault('ha', 'center'); kw.setdefault('va', 'center')
    return ax.text(x, y, s, fontsize=fs, color=K, zorder=4, linespacing=1.15, **kw)


def line(pts, ls='-'):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=K, linewidth=LW, linestyle=ls, zorder=3, solid_capstyle='butt',
            dash_capstyle='butt')


def arrow(p, q, ls='-'):
    ax.annotate('', xy=q, xytext=p, zorder=3,
                arrowprops=dict(arrowstyle='-|>', mutation_scale=7, linewidth=LW, color=K,
                                linestyle=ls, shrinkA=0, shrinkB=0))


def label(x, y, s, fs=6.9, **kw):
    """Edge label on a white ground so it can sit on a connector."""
    kw.setdefault('ha', 'center'); kw.setdefault('va', 'center'); kw.setdefault('style', 'italic')
    ax.text(x, y, s, fontsize=fs, color=K, zorder=5,
            bbox=dict(boxstyle='square,pad=0.12', facecolor='white', edgecolor='none'), **kw)


YC = 1.98                                    # main signal line

# ---- region frames -------------------------------------------------------------------------
box(0.04, 0.99, W - 0.08, 2.35, lw=0.5, ls=(0, (4, 2)))
text(0.12, 3.22, 'Online, per field', fs=7.2, ha='left', fontweight='bold')
box(0.04, 0.06, W - 0.08, 0.84, lw=0.5, ls=(0, (4, 2)))
text(0.12, 0.78, 'Offline, once per deployment', fs=7.2, ha='left', fontweight='bold')

# ---- input and localisation -----------------------------------------------------------------
box(0.16, YC - 0.30, 0.74, 0.60)
text(0.53, YC, 'Problem-sheet\npage\n(PDF or scan)')
box(1.10, YC - 0.36, 0.80, 0.72)
text(1.50, YC + 0.12, 'Evidence\nlocalisation')
text(1.50, YC - 0.20, r'$A=(p,\ell,s)$', fs=7.2)
arrow((0.90, YC), (1.10, YC))

# ---- three independent channels -------------------------------------------------------------
XC, WC, HC = 2.18, 0.98, 0.32
ych = [YC + 0.46, YC, YC - 0.46]
chans = [(r'$C_1$  Tesseract 4.1', 'LSTM, binarised input'),
         (r'$C_2$  EasyOCR 1.7', 'CRAFT + CRNN'),
         (r'$C_3$  SmolVLM-256M', 'vision-language model')]
xb = 2.04                                     # fan-out bus
line([(1.90, YC), (xb, YC)])
line([(xb, ych[2]), (xb, ych[0])])
for y, (t1, t2) in zip(ych, chans):
    box(XC, y - HC / 2, WC, HC, fill=FILL)
    text(XC + WC / 2, y + 0.063, t1, fs=7.2)
    text(XC + WC / 2, y - 0.080, t2, fs=6.4, style='italic')
    arrow((xb, y), (XC, y))

# ---- admission ------------------------------------------------------------------------------
XA, WA = 3.42, 0.98
YA0, YA1 = YC - 0.66, YC + 0.66
box(XA, YA0, WA, YA1 - YA0)
band = (YA1 - YA0) / 3
rows = [('Canonicalise', r'$\kappa$: string $\rightarrow$ value'),
        ('Format guard', r'field grammar $\Gamma$'),
        ('Range guard', r'$|v|\leq R$ (declared)')]
for i, (t1, t2) in enumerate(rows):
    yc = YA1 - band * (i + 0.5)
    text(XA + WA / 2, yc + 0.075, t1, fs=7.2)
    text(XA + WA / 2, yc - 0.085, t2, fs=6.6)
    if i:
        line([(XA, YA1 - band * i), (XA + WA, YA1 - band * i)])
for y in ych:
    arrow((XC + WC, y), (XA, y))
label(XA + WA / 2, YA0 - 0.11, r'invalid read $\rightarrow$ refusal', fs=6.3)
label(XC + WC / 2, ych[2] - HC / 2 - 0.10, r'called in cost order $C_2, C_1, C_3$;', fs=6.3)
label(XC + WC / 2, ych[2] - HC / 2 - 0.23, 'stop at two agreeing reads', fs=6.3)

# ---- corroboration --------------------------------------------------------------------------
XS, WS = 4.62, 0.86
box(XS, YC - 0.34, WS, 0.68)
text(XS + WS / 2, YC + 0.19, 'Corroboration')
text(XS + WS / 2, YC - 0.03, r'$c(v)=\sum_k \mathbb{1}[\hat v_k=v]$', fs=6.9)
text(XS + WS / 2, YC - 0.21, r'$+\,\pi_{C_3}(v)$', fs=6.9)
arrow((XA + WA, YC), (XS, YC))

# ---- decision nodes -------------------------------------------------------------------------
XD, DW, DH = 5.86, 0.30, 0.27
diamond(XD, YC, DW, DH)
text(XD, YC, r'$c(v)\geq\hat\lambda$?', fs=7.0)
arrow((XS + WS, YC), (XD - DW, YC))

YD2, DH2 = 2.80, 0.24
diamond(XD, YD2, DW, DH2)
text(XD, YD2, 'better\ncopy?', fs=6.6)
arrow((XD, YC + DH), (XD, YD2 - DH2))
label(XD + 0.07, (YC + DH + YD2 - DH2) / 2, 'no', ha='left')

XO, WO, HO = 6.34, 0.58, 0.40
box(XO, YC - HO / 2, WO, HO)
text(XO + WO / 2, YC + 0.07, 'Commit')
text(XO + WO / 2, YC - 0.09, '+ audit record', fs=6.3)
arrow((XD + DW, YC), (XO, YC))
label((XD + DW + XO) / 2, YC + 0.10, 'yes', fs=6.6)

box(XO, YD2 - HO / 2, WO, HO)
text(XO + WO / 2, YD2 + 0.07, 'Escalate')
text(XO + WO / 2, YD2 - 0.09, '+ reason code', fs=6.3)
arrow((XD + DW, YD2), (XO, YD2))
label((XD + DW + XO) / 2, YD2 + 0.10, 'no', fs=6.6)

# feedback: one re-render of the same evidence, dashed
DASH = (0, (3, 2))
line([(XD - DW, YD2), (1.50, YD2)], ls=DASH)
arrow((1.50, YD2), (1.50, YC + 0.36), ls=DASH)
label(3.60, YD2, r'yes: re-render the atoms at 300 dpi and repeat once', fs=6.6)

# ---- offline calibration --------------------------------------------------------------------
YB, HB = 0.16, 0.50
box(0.40, YB, 1.70, HB)
text(1.25, YB + 0.32, 'Calibration units')
text(1.25, YB + 0.13, r'$u_1,\dots,u_n$, exchangeable', fs=6.7)
box(2.42, YB, 1.70, HB)
text(3.27, YB + 0.32, 'Unit loss')
text(3.27, YB + 0.13, r'$L_i(\lambda)$: committed and silent', fs=6.7)
box(4.44, YB, 2.08, HB)
text(5.48, YB + 0.33, 'Conformal risk control', fs=7.4)
text(5.48, YB + 0.12,
     r'$\hat\lambda=\inf\{\lambda:\frac{n}{n+1}\hat R_n(\lambda)+\frac{1}{n+1}\leq\alpha\}$', fs=6.9)
arrow((2.10, YB + HB / 2), (2.42, YB + HB / 2))
arrow((4.12, YB + HB / 2), (4.44, YB + HB / 2))
arrow((XD, YB + HB), (XD, YC - DH))
label(XD + 0.07, 1.25, r'$\hat\lambda$', fs=7.4, ha='left', style='normal')

fig.savefig('png/fig01_architecture.png', dpi=400, bbox_inches='tight', pad_inches=0.02)
fig.savefig('png/fig01_architecture.pdf', bbox_inches='tight', pad_inches=0.02)
print('wrote png/fig01_architecture.png')
