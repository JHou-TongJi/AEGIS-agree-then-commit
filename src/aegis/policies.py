"""Commit/escalate policies replayed exactly on logged channel readings.

Each channel is deterministic (greedy decoding, fixed binaries), so a policy that calls a
subset of channels in some order can be evaluated *exactly* by replaying the logged outputs:
no channel is re-run and no counterfactual is estimated.

A policy returns, per item, (decision, value, cost) with decision in {'commit','escalate'}.
"""
from collections import Counter

import json as _json, os as _os
# measured mean wall-clock seconds per call on the reference CPU (2 threads); results/cost.json
_C = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
                   'results', 'cost.json')
COST = ({k: v['mean_s'] for k, v in _json.load(open(_C)).items() if isinstance(v, dict)}
        if _os.path.exists(_C) else {'tess': 0.49, 'easy': 0.13, 'vlm': 1.43, 'rerender': 0.07})


def single(item, ch):
    v = item[ch]
    return ('commit', v, COST[ch]) if v is not None else ('escalate', None, COST[ch])


def majority(item, chans=('tess', 'easy', 'vlm'), k=2):
    vals = [item[c] for c in chans if item[c] is not None]
    cost = sum(COST[c] for c in chans)
    if not vals:
        return ('escalate', None, cost)
    v, n = Counter(vals).most_common(1)[0]
    return ('commit', v, cost) if n >= k else ('escalate', None, cost)


def cascade(item, order=('easy', 'vlm', 'tess'), need=2, rerender=None):
    """Agentic cascade: call channels cheapest-first and stop as soon as `need` channels agree
    on a format-valid value.  If the channels are exhausted without agreement and a higher-
    resolution rendering of the same evidence is available (vector source), re-render once and
    repeat on it.  Otherwise escalate to a reviewer."""
    cost, seen = 0.0, Counter()
    for c in order:
        cost += COST[c]
        v = item[c]
        if v is not None:
            seen[v] += 1
            if seen[v] >= need:
                return ('commit', v, cost)
    if rerender is not None:
        d, v, c2 = cascade(rerender, order, need, None)
        return (d, v, cost + COST['rerender'] + c2)
    return ('escalate', None, cost)


def admissible(v, lo=None, hi=None):
    """Domain verifier: a format-valid value outside the physically plausible range of the field
    is treated as no reading.  The range is a property of the field (declared before any reading
    is seen), not of the data."""
    if v is None:
        return None
    if lo is not None and v < lo:
        return None
    if hi is not None and v > hi:
        return None
    return v


def with_domain(item, lo, hi):
    out = dict(item)
    for c in ('tess', 'easy', 'vlm'):
        out[c] = admissible(item[c], lo, hi)
    return out
