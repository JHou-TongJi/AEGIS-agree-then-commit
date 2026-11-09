"""A13 -- token set by rendering and kind (aggregate only; needs the local token readings)."""
import json, os
from common import *  # noqa
from aegis.policies import majority


def main():
    b = load_b()
    if b is None:
        print('SKIP: token readings are local-only'); return
    rows = []
    for (cond, kind), g in b.groupby(['cond', 'kind']):
        r = dict(cond=cond, kind=kind, n=len(g))
        for k in CHANNELS:
            r['acc_' + k] = round(g[k + '_ok'].mean(), 3); r['sil_' + k] = round(g[k + '_silent'].mean(), 3)
        D = [majority({c: x[c + '_c'] for c in CHANNELS}) for _, x in g.iterrows()]
        com = [d[0] == 'commit' for d in D]
        wr = [d[0] == 'commit' and d[1] != x.ref_c for d, (_, x) in zip(D, g.iterrows())]
        r['vote_cov'] = round(float(np.mean(com)), 3); r['vote_err'] = round(sum(wr) / max(1, sum(com)), 4)
        rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, 'a13_tokens_cond_kind.csv'), index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == '__main__':
    main()


def dependence():
    """Pairwise error dependence and same-wrong-value collisions on the token set (aggregate)."""
    b = load_b()
    if b is None:
        print('SKIP'); return
    out = {}
    E = {k: ~b[k + '_ok'] for k in CHANNELS}
    for a, c in [('tess', 'easy'), ('tess', 'vlm'), ('easy', 'vlm')]:
        joint = float((E[a] & E[c]).mean()); ind = float(E[a].mean() * E[c].mean())
        coll = float(((b[a + '_c'] == b[c + '_c']) & b[a + '_c'].notna() & ~b[a + '_ok']).mean())
        out[f'{a}-{c}'] = dict(joint_error=round(joint, 4), independent=round(ind, 4),
                               ratio=round(joint / ind, 2), collision=round(coll, 4))
    json.dump(out, open(os.path.join(OUT, 'a13_token_dependence.json'), 'w'), indent=1)
    print(out)


if __name__ == '__main__':
    import json
    dependence()
