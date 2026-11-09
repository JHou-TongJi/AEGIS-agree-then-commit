"""A9 -- Ablations replayed exactly: every channel pair, every cascade order, and per-callout difficulty.

(i)  Two-channel systems: commit when both channels return the same admissible value.
(ii) All six orders of the three-channel cascade: decisions are order-invariant, cost is not.
(iii) Per-callout difficulty: for each of the 54 callouts, how many of the 16 conditions each
     channel reads wrongly, and whether the agent commits a wrong value on it.
"""
import itertools, json, os
from common import *  # noqa
from aegis.policies import cascade, COST
import importlib
a3 = importlib.import_module('a3_policies')


def pair_policy(v, a, b):
    cost = COST[a] + COST[b]
    if v[a] is not None and v[a] == v[b]:
        return ('commit', v[a], cost)
    return ('escalate', None, cost)


def main():
    d = load_a(); it = a3.items(d)
    out = {'pairs': {}, 'orders': {}}
    for a, b in itertools.combinations(CHANNELS, 2):
        R, s = a3.evaluate(it, lambda c, i, v: pair_policy(v, a, b))
        out['pairs'][f'{a}+{b}'] = s
    for order in itertools.permutations(['easy', 'tess', 'vlm']):
        R, s = a3.evaluate(it, lambda c, i, v: cascade(v, order))
        out['orders']['>'.join(order)] = s
    # per-callout difficulty
    A4 = pd.read_csv(os.path.join(OUT, 'a4_agent_items.csv'))
    rows = []
    for idx, g in d.groupby('idx'):
        r = dict(idx=int(idx), panel=g.panel.iloc[0], gold=g.gold.iloc[0])
        for k in CHANNELS:
            r[k + '_wrong'] = int((~g[k + '_ok']).sum())
            r[k + '_silent'] = int(g[k + '_silent'].sum())
        ag = A4[A4.idx == idx]
        r['agent_wrong'] = int(ag.wrong.sum()); r['agent_escalated'] = int((ag.dec == 'escalate').sum())
        rows.append(r)
    P = pd.DataFrame(rows)
    P.to_csv(os.path.join(OUT, 'a9_per_callout.csv'), index=False)
    out['per_callout_summary'] = dict(
        callouts_never_wrong_any=int(((P.tess_wrong + P.easy_wrong + P.vlm_wrong) == 0).sum()),
        callouts_with_agent_error=int((P.agent_wrong > 0).sum()),
        callouts_with_escalation=int((P.agent_escalated > 0).sum()),
        tess_wrong_ge8=int((P.tess_wrong >= 8).sum()))
    json.dump(out, open(os.path.join(OUT, 'a9_ablation.json'), 'w'), indent=1)
    for k, v in out['pairs'].items():
        print('pair', k, v['coverage'], v['committed_error'], v['n_wrong_committed'], v['cost_s'])
    for k, v in out['orders'].items():
        print('order', k, v['coverage'], v['committed_error'], v['cost_s'])
    print(out['per_callout_summary'])


if __name__ == '__main__':
    main()
