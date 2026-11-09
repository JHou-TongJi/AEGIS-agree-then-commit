"""A1 -- How do three independent reading channels fail on the 54 real callouts?

Per channel: accuracy, invalid (format-rejected) share, silent share (format-valid and wrong),
by resolution and by degradation; an error taxonomy; and pairwise error dependence.
Writes results/a1_*.
"""
import json, os, re
from common import *  # noqa


def taxonomy(gold, read):
    """Classify a format-valid wrong reading against the gold string."""
    g, r = str(gold), str(read)
    gv, rv = float(g), float(r)
    if rv == -gv:
        return 'sign loss'
    if '.' in g and '.' not in r and r.lstrip('-') == g.replace('.', '').lstrip('-').lstrip('0') or \
       ('.' in g and '.' not in r and r.lstrip('-') == g.replace('.', '').lstrip('-')):
        return 'decimal drop'
    if len(r.replace('-', '')) > len(g.replace('-', '')) and r.startswith(g):
        return 'digit insertion'
    if abs(rv) >= 10 * max(abs(gv), 0.1) - 1e-9:
        return 'magnitude x10'
    return 'digit substitution'


def main():
    d = load_a()
    out = {}
    rows = []
    for k in CHANNELS:
        for by in ['dpi', 'deg']:
            for v, s in d.groupby(by):
                rows.append(dict(channel=k, by=by, level=str(v), n=len(s),
                                 acc=s[k + '_ok'].mean(), invalid=s[k + '_inv'].mean(),
                                 silent=s[k + '_silent'].mean()))
        lo, hi = wilson(int(d[k + '_ok'].sum()), len(d))
        out[k] = dict(acc=round(d[k + '_ok'].mean(), 6), acc_ci=[round(lo, 6), round(hi, 6)],
                      invalid=round(d[k + '_inv'].mean(), 6), silent=round(d[k + '_silent'].mean(), 6),
                      silent_share_of_errors=round(d[k + '_silent'].sum() / max(1, (~d[k + '_ok']).sum()), 6),
                      n_errors=int((~d[k + '_ok']).sum()))
    pd.DataFrame(rows).round(4).to_csv(os.path.join(OUT, 'a1_by_condition.csv'), index=False)
    # taxonomy of silent errors
    tax = []
    for k in CHANNELS:
        s = d[d[k + '_silent']]
        for _, r in s.iterrows():
            tax.append(dict(channel=k, cond=r.cond, gold=r.gold, read=r[k + '_c'],
                            kind=taxonomy(r.gold, ('%g' % r[k + '_c']))))
    T = pd.DataFrame(tax)
    T.to_csv(os.path.join(OUT, 'a1_silent_errors.csv'), index=False)
    out['taxonomy'] = {k: T[T.channel == k].kind.value_counts().to_dict() for k in CHANNELS}
    # pairwise dependence
    E = {k: ~d[k + '_ok'] for k in CHANNELS}
    pair = {}
    for a, b in [('tess', 'easy'), ('tess', 'vlm'), ('easy', 'vlm')]:
        joint = (E[a] & E[b]).mean(); ind = E[a].mean() * E[b].mean()
        same = ((d[a + '_c'] == d[b + '_c']) & d[a + '_c'].notna() & ~d[a + '_ok']).sum()
        # phi coefficient of error indicators
        x, y = E[a].astype(float), E[b].astype(float)
        phi = float(np.corrcoef(x, y)[0, 1])
        pair[f'{a}-{b}'] = dict(joint_error=round(joint, 4), independent=round(ind, 4),
                                ratio=round(joint / ind, 2) if ind else None, phi=round(phi, 3),
                                same_wrong_value=int(same))
    out['pairs'] = pair
    out['n_reads'] = int(len(d)); out['n_conditions'] = int(d.cond.nunique())
    json.dump(out, open(os.path.join(OUT, 'a1_summary.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
