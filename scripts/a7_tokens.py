"""A7 -- Does the callout result transfer to the other digit-bearing tokens of the seven sheets?

Dataset B (local only: contains recognised text) = 344 digit tokens x 2 renderings (200 dpi clean,
100 dpi JPEG q25), text-layer reference.  Policies replayed exactly, by token kind.  Only
aggregate numbers are written.
"""
import json, os
from common import *  # noqa
from aegis.policies import single, majority, cascade


def main():
    b = load_b()
    if b is None:
        print('SKIP: dataset B is local-only'); return
    res = {}
    for kind in ['numeral', 'week_code', 'alnum', 'all']:
        s = b if kind == 'all' else b[b.kind == kind]
        r = {'n': int(len(s))}
        for name, f in {'single-tess': lambda v: single(v, 'tess'), 'single-easy': lambda v: single(v, 'easy'),
                        'single-vlm': lambda v: single(v, 'vlm'), 'majority-2of3': majority,
                        'cascade(easy>tess>vlm)': lambda v: cascade(v, ('easy', 'tess', 'vlm'))}.items():
            dec = []
            for _, x in s.iterrows():
                it = {c: x[c + '_c'] for c in CHANNELS}
                dd, val, cost = f(it)
                dec.append((dd == 'commit', dd == 'commit' and val != x.ref_c, cost))
            D = pd.DataFrame(dec, columns=['com', 'wrong', 'cost'])
            r[name] = dict(coverage=round(D.com.mean(), 6),
                           committed_error=round(D.wrong.sum() / max(1, D.com.sum()), 6),
                           cost_s=round(D.cost.mean(), 5))
        for c in CHANNELS:
            r['acc_' + c] = round(s[c + '_ok'].mean(), 6)
        res[kind] = r
    by_cond = b.groupby('cond')[[c + '_ok' for c in CHANNELS]].mean().round(4).to_dict()
    res['acc_by_cond'] = by_cond
    json.dump(res, open(os.path.join(OUT, 'a7_tokens.json'), 'w'), indent=1)
    for k, v in res.items():
        if k == 'acc_by_cond':
            continue
        print(k, v['n'], {p: (q['coverage'], q['committed_error']) for p, q in v.items() if isinstance(q, dict)},
              {c: v['acc_' + c] for c in CHANNELS})


if __name__ == '__main__':
    main()
