import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'src'))
DATA = os.path.join(REPO, 'data')
OUT = os.path.join(REPO, 'results')
os.makedirs(OUT, exist_ok=True)
LOCAL_B = os.environ.get('AEGIS_LOCAL_B', os.path.join(REPO, 'local', 'reads_b.csv'))

import numpy as np, pandas as pd
from aegis.canon import canon_numeric, canon_token, NUM_1DP, NUM_ANY

CHANNELS = ['tess', 'easy', 'vlm']
NAMES = {'tess': 'Tesseract 4.1', 'easy': 'EasyOCR 1.7', 'vlm': 'SmolVLM-256M'}


def load_a(fmt=NUM_1DP):
    d = pd.read_csv(os.path.join(DATA, 'callouts', 'channel_reads.csv'),
                    dtype={'gold': str, 'tess': str, 'easy': str, 'vlm': str}, keep_default_na=False)
    d['g'] = d.gold.astype(float)
    d['dpi'] = d.cond.str.split('_').str[0].astype(int)
    d['deg'] = d.cond.str.split('_').str[1]
    for k in CHANNELS:
        d[k + '_c'] = d[k].map(lambda s: canon_numeric(s, fmt))
        d[k + '_ok'] = d[k + '_c'] == d.g
        d[k + '_inv'] = d[k + '_c'].isna()
        d[k + '_silent'] = ~d[k + '_inv'] & ~d[k + '_ok']
    d['easy_conf'] = d.easy_conf.astype(float)
    d['vlm_logprob'] = d.vlm_logprob.astype(float)
    d['tess_conf'] = d.tess_conf.astype(float)
    return d


def load_b():
    if not os.path.exists(LOCAL_B):
        return None
    b = pd.read_csv(LOCAL_B, dtype=str, keep_default_na=False)
    b['ref_c'] = [canon_token(r, k) for r, k in zip(b.ref, b.kind)]
    for k in CHANNELS:
        b[k + '_c'] = [canon_token(r, kk) for r, kk in zip(b[k], b.kind)]
        b[k + '_ok'] = b[k + '_c'] == b.ref_c
        b[k + '_inv'] = b[k + '_c'].isna()
        b[k + '_silent'] = ~b[k + '_inv'] & ~b[k + '_ok']
    b['easy_conf'] = b.easy_conf.astype(float)
    b['vlm_logprob'] = b.vlm_logprob.astype(float)
    return b


def auroc_np(score, y):
    score = np.asarray(score, float); y = np.asarray(y, int)
    pos, neg = score[y == 1], score[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float('nan')
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind='mergesort')
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    # average ties
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, ranks); ranks = sums[inv] / cnt[inv]
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)
