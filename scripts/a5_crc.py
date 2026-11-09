"""A5 -- Distribution-free risk control on top of the agent.

Loss of a unit at threshold lam = share of its items committed (corroboration >= lam) and wrong.
Units:
  A: (condition, panel) blocks of the callout page, 16 x 6 = 96 units of 9 callouts;
     evaluated leave-one-condition-out (calibrate on the 90 units of the other 15 conditions,
     test on the 6 units of the held-out condition) so that a whole degradation regime is unseen.
  B: (document, page, condition) units of the digit-token set, evaluated leave-one-document-out.
For each alpha we report mean realised risk of held-out units, the worst held-out unit, coverage,
and the share of folds in which alpha is infeasible.
"""
import json, os
from common import *  # noqa
from aegis.corroboration import candidate
from aegis.policies import with_domain
from aegis.crc import calibrate

LAMS = np.round(np.arange(0.0, 4.001, 0.01), 3)


def build_a(R=3.0):
    d = load_a()
    rows = []
    for _, r in d.iterrows():
        it = dict(tess=None if pd.isna(r.tess_c) else r.tess_c, easy=None if pd.isna(r.easy_c) else r.easy_c,
                  vlm=None if pd.isna(r.vlm_c) else r.vlm_c, vlm_lp=r.vlm_logprob)
        it = with_domain(it, -R, R); it['vlm_lp'] = r.vlm_logprob
        v, c = candidate(it)
        rows.append(dict(unit=f'{r.cond}|{r.panel}', fold=r.cond, c=c, wrong=int(v is not None and v != r.g)))
    return pd.DataFrame(rows)


def build_b():
    b = load_b()
    if b is None:
        return None
    rows = []
    for _, r in b.iterrows():
        it = dict(tess=r.tess_c, easy=r.easy_c, vlm=r.vlm_c, vlm_lp=r.vlm_logprob)
        v, c = candidate(it)
        rows.append(dict(unit=f'{r.doc}|{r.page}|{r.cond}', fold=r.doc, c=c, kind=r.kind,
                         wrong=int(v is not None and v != r.ref_c)))
    return pd.DataFrame(rows)


def unit_loss(df):
    U = []
    for u, g in df.groupby('unit'):
        c = g.c.to_numpy()[:, None]; w = g.wrong.to_numpy()[:, None]
        U.append(((c >= LAMS[None, :]) & (w == 1)).mean(0))
    return np.array(U)


def lofo(df, alphas):
    out = []
    for a in alphas:
        risks, covs, worst, infeas = [], [], [], 0
        for f in df.fold.unique():
            cal, te = df[df.fold != f], df[df.fold == f]
            lam = calibrate(unit_loss(cal), LAMS, a)
            if lam is None:
                infeas += 1; lam = np.inf
            Lt = [((g.c >= lam) & (g.wrong == 1)).mean() for _, g in te.groupby('unit')]
            risks.extend(Lt); worst.append(max(Lt)); covs.append((te.c >= lam).mean())
        out.append(dict(alpha=a, mean_risk=round(float(np.mean(risks)), 5), worst_fold_unit=round(float(max(worst)), 4),
                        coverage=round(float(np.mean(covs)), 4), infeasible_folds=infeas,
                        n_folds=int(df.fold.nunique())))
    return out


def main():
    A = build_a()
    prev = json.load(open(os.path.join(OUT, 'a5_crc.json'))) if os.path.exists(os.path.join(OUT, 'a5_crc.json')) else {}
    alphas = [0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20]
    res = {'A_units': int(A.unit.nunique()), 'A': lofo(A, alphas),
           'A_auroc_corroboration': round(auroc_np(-A.c, A.wrong), 4),
           'A_base_error_plurality': round(A.wrong.mean(), 5)}
    B = build_b()
    if B is None:
        for k in ('B_units', 'B', 'B_auroc_corroboration', 'B_base_error_plurality', 'B_by_kind_base_error'):
            if k in prev:
                res[k] = prev[k]
    if B is not None:
        res['B_units'] = int(B.unit.nunique())
        res['B'] = lofo(B, alphas)
        res['B_auroc_corroboration'] = round(auroc_np(-B.c, B.wrong), 4)
        res['B_base_error_plurality'] = round(B.wrong.mean(), 4)
        res['B_by_kind_base_error'] = B.groupby('kind').wrong.mean().round(4).to_dict()
    A.to_csv(os.path.join(OUT, 'a5_A_scores.csv'), index=False)
    json.dump(res, open(os.path.join(OUT, 'a5_crc.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items()}, indent=1))


if __name__ == '__main__':
    main()
