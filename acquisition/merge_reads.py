"""Join the per-channel logs written by run_cond.py and run_vlm.py into the released table.

    $AEGIS_WORK/reads.csv  cond,idx,panel,gold,tess,tess_conf,easy,easy_conf      (run_cond.py)
    $AEGIS_WORK/vlm.csv    cond,idx,gold,vlm,vlm_logprob                           (run_vlm.py)
 -> data/callouts/channel_reads.csv  (864 rows: 16 conditions x 54 callouts)

Values are kept as strings so that "0.70" or "07" are never re-formatted. Usage:
    python acquisition/merge_reads.py [reads.csv vlm.csv out.csv]
"""
import os, sys
import pandas as pd

HERE = os.environ.get('AEGIS_WORK', 'work')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS = ['cond', 'idx', 'panel', 'gold', 'tess', 'tess_conf', 'easy', 'easy_conf', 'vlm', 'vlm_logprob']


def merge(reads, vlm, out):
    a = pd.read_csv(reads, dtype=str, keep_default_na=False)
    b = pd.read_csv(vlm, dtype=str, keep_default_na=False)
    for name, d in (('reads', a), ('vlm', b)):
        if d.duplicated(['cond', 'idx']).any():
            raise SystemExit('%s.csv has duplicated (cond, idx) rows; remove the partial run first' % name)
    m = a.merge(b[['cond', 'idx', 'gold', 'vlm', 'vlm_logprob']], on=['cond', 'idx'], how='inner',
                suffixes=('', '_v'), validate='one_to_one')
    if (m.gold != m.gold_v).any():
        raise SystemExit('reference values of the two logs disagree')
    m['idx'] = m.idx.astype(int)
    m['_c'] = m.cond.map(lambda c: (int(c.split('_')[0]), ['clean', 'jpeg', 'blur', 'skew'].index(c.split('_')[1])))
    m = m.sort_values(['_c', 'idx'])[COLS]
    m.to_csv(out, index=False, lineterminator='\n')
    print('wrote', out, len(m), 'rows')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 3:
        merge(*args)
    else:
        merge(os.path.join(HERE, 'reads.csv'), os.path.join(HERE, 'vlm.csv'),
              os.path.join(REPO, 'data', 'callouts', 'channel_reads.csv'))
