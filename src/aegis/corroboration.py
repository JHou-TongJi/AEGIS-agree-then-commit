"""Corroboration score of a candidate value.

Given the canonical readings of K channels, the candidate is the plurality value (ties broken in
favour of the channel listed first in `prefer`).  Its corroboration is
    c = (#channels that return the candidate) + p_vlm * [VLM returns the candidate],
where p_vlm = exp(sequence log-probability) in (0, 1].  c is in {0} U [1, K + 1).  Committing iff
c >= lam is monotone in lam, which is what conformal risk control needs.
"""
from collections import Counter
import math


def candidate(item, chans=('tess', 'easy', 'vlm'), prefer=('vlm', 'easy', 'tess')):
    vals = [item[c] for c in chans if item.get(c) is not None]
    if not vals:
        return None, 0.0
    cnt = Counter(vals)
    top = max(cnt.values())
    tied = [v for v, n in cnt.items() if n == top]
    if len(tied) > 1:
        for p in prefer:
            if item.get(p) in tied:
                v = item[p]; break
    else:
        v = tied[0]
    c = float(cnt[v])
    if item.get('vlm') == v and item.get('vlm_lp') is not None:
        c += math.exp(item['vlm_lp'])
    return v, c
