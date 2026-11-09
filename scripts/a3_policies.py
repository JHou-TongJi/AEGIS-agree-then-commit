"""A3 -- Commit/escalate policies replayed exactly on the logged channel outputs.

Policies (all on the 864 callout reads; rerender = the same callout read from the 300 dpi
rendering of the same degradation, i.e. the agent requests a higher-resolution copy):
  single-<ch>      commit every format-valid value of one channel
  majority         commit the 2-of-3 majority value, all channels always called
  cascade          cheapest-first; stop at the first 2 agreeing channels; else escalate
  cascade+rr       as cascade, plus one re-render at 300 dpi before escalating
Reported: coverage (share committed), committed error (share of committed that are wrong),
residual risk (share of all items committed and wrong), mean cost (s/item, measured), escalations.
"""
import json, os
from common import *  # noqa
from aegis.policies import single, majority, cascade, COST


def items(d):
    it = {}
    for _, r in d.iterrows():
        it[(r.cond, r.idx)] = dict(tess=r.tess_c, easy=r.easy_c, vlm=r.vlm_c, gold=r.g,
                                   tess_v=None if pd.isna(r.tess_c) else r.tess_c)
    for v in it.values():
        for c in CHANNELS:
            if v[c] is not None and pd.isna(v[c]):
                v[c] = None
    return it


def evaluate(it, pol):
    rows = []
    for (cond, idx), v in it.items():
        dec, val, cost = pol(cond, idx, v)
        rows.append(dict(cond=cond, idx=idx, dec=dec, ok=(dec == 'commit' and val == v['gold']),
                         wrong=(dec == 'commit' and val != v['gold']), cost=cost))
    R = pd.DataFrame(rows)
    com = R.dec == 'commit'
    return R, dict(coverage=round(com.mean(), 6),
                   committed_error=round(R.wrong.sum() / max(1, com.sum()), 6),
                   residual_risk=round(R.wrong.mean(), 6),
                   n_wrong_committed=int(R.wrong.sum()),
                   escalated=int((~com).sum()),
                   cost_s=round(R.cost.mean(), 5))


def main():
    d = load_a()
    it = items(d)

    def rr(cond):
        dpi, deg = cond.split('_')
        return None if dpi == '300' else f'300_{deg}'

    P = {
        'single-tess': lambda c, i, v: single(v, 'tess'),
        'single-easy': lambda c, i, v: single(v, 'easy'),
        'single-vlm': lambda c, i, v: single(v, 'vlm'),
        'majority-2of3': lambda c, i, v: majority(v),
        'cascade(easy>vlm>tess)': lambda c, i, v: cascade(v, ('easy', 'vlm', 'tess')),
        'cascade(easy>tess>vlm)': lambda c, i, v: cascade(v, ('easy', 'tess', 'vlm')),
        'cascade+rerender': lambda c, i, v: cascade(v, ('easy', 'vlm', 'tess'),
                                                    rerender=it.get((rr(c), i)) if rr(c) else None),
        'unanimous-3of3': lambda c, i, v: majority(v, k=3),
    }
    res, per = {}, []
    for name, f in P.items():
        R, s = evaluate(it, f)
        res[name] = s
        R['policy'] = name
        per.append(R)
        # by resolution
        for dpi, g in R.groupby(R.cond.str.split('_').str[0]):
            com = g.dec == 'commit'
            res[name].setdefault('by_dpi', {})[dpi] = dict(
                coverage=round(com.mean(), 6), committed_error=round(g.wrong.sum() / max(1, com.sum()), 6),
                cost_s=round(g.cost.mean(), 5))
    pd.concat(per).to_csv(os.path.join(OUT, 'a3_policy_items.csv'), index=False)
    # how many channel calls does each cascade order make?
    hist = {}
    for order in (('easy', 'tess', 'vlm'), ('easy', 'vlm', 'tess')):
        calls = {1: 0, 2: 0, 3: 0}
        for v in it.values():
            n, seen = 0, {}
            for c in order:
                n += 1
                if v[c] is not None:
                    seen[v[c]] = seen.get(v[c], 0) + 1
                    if seen[v[c]] >= 2:
                        break
            calls[n] += 1
        hist['>'.join(order)] = calls
    res['cascade_calls_histogram'] = hist['easy>tess>vlm']
    res['cascade_calls_histogram_by_order'] = hist
    calls = hist['easy>tess>vlm']
    res['cost_per_call_s'] = COST
    json.dump(res, open(os.path.join(OUT, 'a3_policies.json'), 'w'), indent=1)
    for k, v in res.items():
        if isinstance(v, dict) and 'coverage' in v:
            print(f'{k:26s} cov {v["coverage"]:.3f}  err {v["committed_error"]:.4f}  '
                  f'nwrong {v["n_wrong_committed"]:3d}  esc {v["escalated"]:3d}  cost {v["cost_s"]:.3f}')
    print(calls)


if __name__ == '__main__':
    main()
