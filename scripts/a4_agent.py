"""A4 -- The agent: cascade + domain verifier + re-render, and its sensitivity to the declared range.

The plausible range of a flush/gap deviation callout is declared as |x| <= R mm.  R is not fitted:
we report every R from 1.0 to 10.0 mm and mark the interval of R over which the result is constant.
The largest gold value on the page is 1.6 mm; the tolerance band of the feature is 0.5 mm.
"""
import json, os
from common import *  # noqa
from aegis.policies import cascade, majority, with_domain, COST
import importlib
a3 = importlib.import_module('a3_policies')


def run(R):
    d = load_a(); it = a3.items(d)
    dom = {k: with_domain(v, -R, R) for k, v in it.items()}
    for k, v in dom.items():
        v['gold'] = it[k]['gold']

    def rr(c):
        dpi, deg = c.split('_')
        return None if dpi == '300' else f'300_{deg}'
    P = {
        'majority+domain': lambda c, i, v: majority(v),
        'cascade+domain': lambda c, i, v: cascade(v, ('easy', 'tess', 'vlm')),
        'agent(cascade+domain+rerender)': lambda c, i, v: cascade(
            v, ('easy', 'tess', 'vlm'), rerender=dom.get((rr(c), i)) if rr(c) else None),
    }
    out = {}
    for name, f in P.items():
        Rr, s = a3.evaluate(dom, f)
        out[name] = s
        if name.startswith('agent') and R == 3.0:
            Rr.to_csv(os.path.join(OUT, 'a4_agent_items.csv'), index=False)
    return out


def main():
    grid = [1.0, 1.5, 1.6, 1.7, 2.0, 3.0, 5.0, 6.9, 7.0, 10.0, 1e9]
    res = {str(R): run(R) for R in grid}
    json.dump(res, open(os.path.join(OUT, 'a4_agent_range.json'), 'w'), indent=1)
    for R, v in res.items():
        print(R, {k: (s['coverage'], s['n_wrong_committed'], s['escalated'], s['cost_s']) for k, s in v.items()})


if __name__ == '__main__':
    main()
