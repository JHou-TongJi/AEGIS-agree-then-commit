"""A12 -- Sensitivity to localisation error.  The crops are shifted by 15 % of the callout width to
the right and 10 % of its height downwards -- a typical detector error -- and all three channels
re-read all 864 crops.  Reported: per-channel accuracy and silent rate, detectors, and the policies,
next to the reference-geometry numbers."""
import json, os
from common import *  # noqa
import importlib
a2 = importlib.import_module('a2_detectors'); a3 = importlib.import_module('a3_policies')
from aegis.policies import single, majority, cascade


def load_shift():
    d = pd.read_csv(os.path.join(DATA, 'callouts', 'channel_reads_shifted.csv'),
                    dtype={'gold': str, 'tess': str, 'easy': str, 'vlm': str}, keep_default_na=False)
    d['g'] = d.gold.astype(float); d['idx'] = d.idx.astype(int)
    for k in CHANNELS:
        d[k + '_c'] = d[k].map(canon_numeric)
        d[k + '_ok'] = d[k + '_c'] == d.g
        d[k + '_inv'] = d[k + '_c'].isna()
        d[k + '_silent'] = ~d[k + '_inv'] & ~d[k + '_ok']
    d['easy_conf'] = d.easy_conf.astype(float); d['vlm_logprob'] = d.vlm_logprob.astype(float)
    d['tess_conf'] = 0.0
    return d


def main():
    res = {}
    for name, d in [('reference', load_a()), ('shifted', load_shift())]:
        r = {k: dict(acc=round(d[k + '_ok'].mean(), 4), invalid=round(d[k + '_inv'].mean(), 4),
                     silent=round(d[k + '_silent'].mean(), 4)) for k in CHANNELS}
        for k in ('easy', 'vlm'):
            s = a2.signals(d, k)
            r[k]['auroc_self'] = round(auroc_np(-s['self'], s.wrong), 4)
            r[k]['auroc_agree'] = round(auroc_np(-s['agree'], s.wrong), 4)
        it = a3.items(d)
        for pn, f in [('vote', lambda c, i, v: majority(v)),
                      ('cascade', lambda c, i, v: cascade(v, ('easy', 'tess', 'vlm'))),
                      ('vlm_only', lambda c, i, v: single(v, 'vlm'))]:
            _, s = a3.evaluate(it, f)
            r[pn] = s
        res[name] = r
    json.dump(res, open(os.path.join(OUT, 'a12_localisation.json'), 'w'), indent=1)
    for n, r in res.items():
        print(n, {k: r[k] for k in CHANNELS})
        print('   ', {p: (r[p]['coverage'], r[p]['committed_error'], r[p]['n_wrong_committed'], r[p]['cost_s']) for p in ('vote', 'cascade', 'vlm_only')})


if __name__ == '__main__':
    main()


def recrop_agent():
    """Agent with a re-crop tool: run the cascade on the reference crop; if no two channels agree,
    re-read the shifted crop of the same callout with the cascade (cost: the channel calls again).
    Optionally followed by re-render.  Replayed exactly from the two logged reading sets."""
    from aegis.policies import with_domain
    ref = a3.items(load_a()); sh = a3.items(load_shift())
    out = {}
    for R in (3.0, 1e9):
        refd = {k: with_domain(v, -R, R) | {'gold': v['gold']} for k, v in ref.items()}
        shd = {k: with_domain(v, -R, R) | {'gold': v['gold']} for k, v in sh.items()}

        def rr(c):
            dpi, deg = c.split('_')
            return None if dpi == '300' else f'300_{deg}'

        P = {
          'cascade': lambda c, i, v: cascade(v, ('easy', 'tess', 'vlm')),
          'cascade+recrop': lambda c, i, v: cascade(v, ('easy', 'tess', 'vlm'), rerender=shd[(c, i)]),
          'cascade+rerender': lambda c, i, v: cascade(v, ('easy', 'tess', 'vlm'),
                                                      rerender=refd.get((rr(c), i)) if rr(c) else None),
        }
        for n, f in P.items():
            _, s = a3.evaluate(refd, f)
            out[f'{n}|R={R:g}'] = s
    return out


if __name__ == '__main__':
    o = recrop_agent()
    j = json.load(open(os.path.join(OUT, 'a12_localisation.json')))
    j['recrop'] = o
    json.dump(j, open(os.path.join(OUT, 'a12_localisation.json'), 'w'), indent=1)
    for k, v in o.items():
        print(k, v['coverage'], v['committed_error'], v['n_wrong_committed'], v['escalated'], v['cost_s'])
