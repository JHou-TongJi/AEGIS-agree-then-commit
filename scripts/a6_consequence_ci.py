"""A6 -- (i) Consequence of silent errors at the 0.5 mm tolerance; (ii) cluster-bootstrap CIs.

(i) A silent error matters for the record when it flips the accept/reject decision |x| <= 0.5.
(ii) The 864 reads are not independent: they share 54 callouts and 16 renderings.  We resample
callouts (54) with replacement, keeping all 16 conditions of each, 2000 replicates, and report
percentile intervals for the headline contrasts.
"""
import json, os
from common import *  # noqa
import importlib
a2 = importlib.import_module('a2_detectors')

TOL = 0.5


def flips(d):
    out = {}
    for k in CHANNELS:
        s = d[d[k + '_silent']]
        fl = ((s[k + '_c'].abs() <= TOL) != (s.g.abs() <= TOL))
        out[k] = dict(n_silent=int(len(s)), n_flip=int(fl.sum()),
                      share_flip=round(float(fl.mean()) if len(s) else 0, 4),
                      mean_abs_err_mm=round(float((s[k + '_c'] - s.g).abs().mean()) if len(s) else 0, 3),
                      max_abs_err_mm=round(float((s[k + '_c'] - s.g).abs().max()) if len(s) else 0, 3))
    return out


def boot(d, B=2000, seed=0):
    rng = np.random.default_rng(seed)
    idx = d.idx.unique()
    g = {i: d[d.idx == i] for i in idx}
    stats = {f'acc_{k}': [] for k in CHANNELS}
    stats.update({f'auroc_self_{k}': [] for k in ('easy', 'vlm')})
    stats.update({f'auroc_agree_{k}': [] for k in ('easy', 'vlm')})
    for _ in range(B):
        s = pd.concat([g[i] for i in rng.choice(idx, len(idx), replace=True)], ignore_index=True)
        for k in CHANNELS:
            stats[f'acc_{k}'].append(s[k + '_ok'].mean())
        for k in ('easy', 'vlm'):
            z = a2.signals(s, k)
            if z.wrong.sum() and (1 - z.wrong).sum():
                stats[f'auroc_self_{k}'].append(auroc_np(-z['self'], z.wrong))
                stats[f'auroc_agree_{k}'].append(auroc_np(-z['agree'], z.wrong))
    return {k: [round(float(np.nanpercentile(v, 2.5)), 4), round(float(np.nanpercentile(v, 97.5)), 4)]
            for k, v in stats.items()}


def main():
    d = load_a()
    res = dict(tolerance_mm=TOL, flips=flips(d), bootstrap_ci_95=boot(d))
    json.dump(res, open(os.path.join(OUT, 'a6_consequence_ci.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
