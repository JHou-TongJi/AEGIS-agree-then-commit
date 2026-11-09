"""A14 -- (i) sensitivity of the corroboration score to the weight w on the VLM probability term,
c = agreements + w * p_vlm, for w in {0, 0.25, 0.5, 0.99}: AUROC against the silent error of the
plurality candidate, on both sets.  (ii) the full list of committed-wrong values under every policy
of results/a3_policies.json at the callout level (no free text: callout index, condition, reference, readings)."""
import json, math, os
from common import *  # noqa
from aegis.corroboration import candidate
from aegis.policies import with_domain


def score(d, w, ref_col, guard=None):
    cs, wr = [], []
    for _, r in d.iterrows():
        it = {k: (None if pd.isna(r[k + '_c']) else r[k + '_c']) for k in CHANNELS}
        if guard is not None:
            it = with_domain(it, -guard, guard)
        it['vlm_lp'] = r.vlm_logprob
        v, c0 = candidate(dict(it, vlm_lp=None))
        p = math.exp(r.vlm_logprob) if it['vlm'] == v and v is not None else 0.0
        cs.append(c0 + w * p); wr.append(int(v is not None and v != r[ref_col]))
    return np.array(cs), np.array(wr)


def main():
    prev = os.path.join(OUT, 'a14_weight.json')
    out = json.load(open(prev)) if os.path.exists(prev) else {}
    a = load_a(); b = load_b()
    for w in (0.0, 0.25, 0.5, 0.99):
        c, y = score(a, w, 'g', guard=3.0)
        out[f'A_w={w}'] = round(auroc_np(-c, y), 4)
        if b is not None:
            c2, y2 = score(b, w, 'ref_c')
            out[f'B_w={w}'] = round(auroc_np(-c2, y2), 4)
    P = pd.read_csv(os.path.join(OUT, 'a3_policy_items.csv'))
    W = P[P.wrong].merge(a[['cond', 'idx', 'gold', 'tess', 'easy', 'vlm']], on=['cond', 'idx'])
    W[['policy', 'cond', 'idx', 'gold', 'tess', 'easy', 'vlm']].to_csv(
        os.path.join(OUT, 'a14_wrong_commits.csv'), index=False)
    out['n_wrong_rows'] = int(len(W))
    json.dump(out, open(os.path.join(OUT, 'a14_weight.json'), 'w'), indent=1)
    print(out)
    print(W.groupby('policy').size().to_dict())


if __name__ == '__main__':
    main()
