"""A2 -- Self-confidence versus cross-channel agreement as detectors of silent errors.

For each primary channel we consider the items on which it produced a format-valid value (the
values a naive pipeline would commit) and ask how well each signal separates its wrong values
from its right ones:
  * self   : the channel's own confidence (EasyOCR score, VLM sequence log-probability,
             Tesseract mean word confidence);
  * agree  : number of *other* channels returning the same canonical value (0, 1, 2);
  * agree+self : agree + self-confidence mapped to [0,1) as tie-breaker.
Reports AUROC (wrong = positive, low score = suspicious) and the operating point at which each
signal flags the same number of items. Also on dataset B (local only) with documents as units.
"""
import json, os
from common import *  # noqa

SELF = {'tess': 'tess_conf', 'easy': 'easy_conf', 'vlm': 'vlm_logprob'}


def signals(d, k):
    m = ~d[k + '_inv']
    s = d[m].copy()
    others = [c for c in CHANNELS if c != k]
    s['agree'] = sum((s[o + '_c'] == s[k + '_c']).astype(int) for o in others)
    conf = s[SELF[k]].astype(float) if SELF[k] in s else pd.Series(0.0, index=s.index)
    if k == 'vlm':
        conf = np.exp(conf)
    s['self'] = conf
    s['agree_self'] = s.agree + 0.999 * (conf - conf.min()) / (conf.max() - conf.min() + 1e-12)
    s['wrong'] = (~s[k + '_ok']).astype(int)
    return s


def flag_at_budget(s, col, budget):
    """Flag the `budget` lowest-scoring items; return recall of wrong items and precision."""
    order = s.sort_values(col, kind='mergesort').index[:budget]
    caught = s.loc[order, 'wrong'].sum()
    return caught / max(1, s.wrong.sum()), caught / max(1, budget)


def run(d, tag):
    res = {}
    for k in CHANNELS:
        s = signals(d, k)
        r = dict(n_committed=int(len(s)), n_wrong=int(s.wrong.sum()))
        for col in ['self', 'agree', 'agree_self']:
            r['auroc_' + col] = round(auroc_np(-s[col].to_numpy(), s.wrong.to_numpy()), 4)
        r['self_conf_distinct_values'] = int(s['self'].nunique())
        r['self_conf_share_zero'] = round(float((s['self'] == 0).mean()), 4)
        # budget = number of items the agreement rule flags (agree == 0, i.e. no corroboration)
        bud = int((s.agree == 0).sum())
        r['flag_budget_agree0'] = bud
        for col in ['self', 'agree_self']:
            rec, prec = flag_at_budget(s, col, bud)
            r[f'recall_{col}_at_budget'] = round(rec, 4); r[f'precision_{col}_at_budget'] = round(prec, 4)
        caught = s[(s.agree == 0)].wrong.sum()
        r['recall_agree0'] = round(caught / max(1, s.wrong.sum()), 4)
        r['precision_agree0'] = round(caught / max(1, bud), 4)
        # confident-and-wrong: wrong values above the median confidence of correct ones
        if s.wrong.sum():
            med = s[s.wrong == 0]['self'].median()
            r['wrong_above_median_correct_conf'] = round(float((s[s.wrong == 1]['self'] >= med).mean()), 4)
        res[k] = r
    return res


def main():
    out = {'callouts': run(load_a(), 'A')}
    prev = os.path.join(OUT, 'a2_detectors.json')
    if os.path.exists(prev):
        p = json.load(open(prev))
        for k in ('tokens', 'tokens_n', 'tokens_numeral'):
            if k in p:
                out[k] = p[k]
    b = load_b()
    if b is not None:
        out['tokens'] = run(b, 'B')
        out['tokens_n'] = int(len(b))
        # the second, independent test of self-confidence vs corroboration: numeral tokens only
        out['tokens_numeral'] = run(b[b.kind == 'numeral'].copy(), 'B-numeral')
    json.dump(out, open(os.path.join(OUT, 'a2_detectors.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
