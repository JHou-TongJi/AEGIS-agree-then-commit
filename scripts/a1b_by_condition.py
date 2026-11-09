"""A1b -- accuracy, refusal and silent rate for every channel under every rendering condition."""
import os
from common import *  # noqa


def main():
    d = load_a()
    rows = []
    for k in CHANNELS:
        for c, s in d.groupby('cond'):
            lo, hi = wilson(int(s[k + '_ok'].sum()), len(s))
            rows.append(dict(channel=k, cond=c, n=len(s), acc=s[k + '_ok'].mean(), acc_lo=lo, acc_hi=hi,
                             invalid=s[k + '_inv'].mean(), silent=s[k + '_silent'].mean()))
    pd.DataFrame(rows).round(4).to_csv(os.path.join(OUT, 'a1_by_cond_detail.csv'), index=False)
    print('wrote a1_by_cond_detail.csv', len(rows))


if __name__ == '__main__':
    main()
