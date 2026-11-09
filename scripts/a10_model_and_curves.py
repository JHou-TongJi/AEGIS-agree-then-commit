"""A10 -- (i) an analytical model of the 2-of-3 vote, checked against the observed vote;
(ii) risk-coverage curves of the corroboration threshold on both sets;
(iii) the agent per rendering condition; (iv) the token set per document (aggregate only).

(i) With per-read error probabilities e_k and collision probability q_ab (two channels return the
    same wrong value), the vote commits a wrong value only if some pair collides; under the
    simplifying assumption that collisions of different pairs are disjoint,
        P(wrong commit) ~= sum_{a<b} q_ab,
    and the vote escalates when no pair agrees.  We compare the model's prediction using
    (a) independence: q_ab ~= e_a e_b / |V| with |V| the number of plausible wrong values, and
    (b) the measured collision rates, with the observed committed error.
"""
import json, os
from common import *  # noqa
from aegis.corroboration import candidate
import importlib
a5 = importlib.import_module('a5_crc')


def main():
    d = load_a()
    out = {}
    e = {k: float((~d[k + '_ok']).mean()) for k in CHANNELS}
    pairs = [('tess', 'easy'), ('tess', 'vlm'), ('easy', 'vlm')]
    coll = {f'{a}-{b}': float(((d[a + '_c'] == d[b + '_c']) & d[a + '_c'].notna() & ~d[a + '_ok']).mean())
            for a, b in pairs}
    V = 15  # plausible wrong values: the other 15 distinct values on the page
    indep = {f'{a}-{b}': e[a] * e[b] / V for a, b in pairs}
    obs = json.load(open(os.path.join(OUT, 'a3_policies.json')))['majority-2of3']
    out['model'] = dict(error_rates=e, collision_measured=coll, collision_independent=indep,
                        predicted_wrong_commit_measured=sum(coll.values()),
                        predicted_wrong_commit_independent=sum(indep.values()),
                        observed_wrong_commit_share=obs['n_wrong_committed'] / 864,
                        observed_committed_error=obs['committed_error'])
    # sweep: what if the strongest channel were weaker? scale e_vlm, keep others; independence model
    sweep = []
    for ev in [0.0093, 0.02, 0.05, 0.10, 0.20, 0.30]:
        p_ind = e['tess'] * e['easy'] / V + e['tess'] * ev / V + e['easy'] * ev / V
        sweep.append(dict(e_vlm=ev, wrong_commit_indep=p_ind))
    out['sweep'] = sweep

    # (ii) risk-coverage curves over lambda
    A = a5.build_a(); B = a5.build_b()
    curves = {}
    for name, df in [('A', A), ('B', B)]:
        if df is None:
            continue
        rows = []
        for lam in a5.LAMS[::5]:
            com = df.c >= lam
            rows.append(dict(lam=float(lam), coverage=float(com.mean()),
                             risk=float((com & (df.wrong == 1)).sum() / max(1, com.sum()))))
        curves[name] = rows
    prev = os.path.join(OUT, 'a10_model.json')
    if B is None and os.path.exists(prev):
        curves['B'] = json.load(open(prev))['curves'].get('B')
    out['curves'] = curves

    # (iii) agent per condition
    ag = pd.read_csv(os.path.join(OUT, 'a4_agent_items.csv'))
    per = ag.groupby('cond').agg(coverage=('dec', lambda s: (s == 'commit').mean()),
                                 wrong=('wrong', 'sum'), escalated=('dec', lambda s: (s == 'escalate').sum()),
                                 cost=('cost', 'mean')).reset_index()
    per.round(4).to_csv(os.path.join(OUT, 'a10_agent_by_cond.csv'), index=False)

    # (iv) token set per document, aggregate
    b = load_b()
    if b is not None:
        rows = []
        for doc, g in b.groupby('doc'):
            vals = []
            for _, x in g.iterrows():
                it = {c: x[c + '_c'] for c in CHANNELS}
                from aegis.policies import majority
                dd, v, _ = majority(it)
                vals.append((dd == 'commit', dd == 'commit' and v != x.ref_c))
            D = pd.DataFrame(vals, columns=['com', 'wrong'])
            rows.append(dict(doc=doc, reads=len(g), pages=int(g.page.nunique()),
                             numeral=int((g.kind == 'numeral').sum()),
                             week=int((g.kind == 'week_code').sum()),
                             alnum=int((g.kind == 'alnum').sum()),
                             acc_easy=round(g.easy_ok.mean(), 3), acc_vlm=round(g.vlm_ok.mean(), 3),
                             vote_cov=round(D.com.mean(), 3),
                             vote_err=round(D.wrong.sum() / max(1, D.com.sum()), 4)))
        pd.DataFrame(rows).to_csv(os.path.join(OUT, 'a10_tokens_by_doc.csv'), index=False)
    json.dump(out, open(os.path.join(OUT, 'a10_model.json'), 'w'), indent=1)
    print(json.dumps(out['model'], indent=1))
    print(per.round(3).to_string(index=False))
    if b is not None:
        print(pd.DataFrame(rows).to_string(index=False))
    else:
        print('SKIP (token part): local-only')


if __name__ == '__main__':
    main()
