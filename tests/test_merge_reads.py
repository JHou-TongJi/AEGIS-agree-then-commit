"""acquisition/merge_reads.py rebuilds the released table from the two per-channel logs."""
import hashlib, os, sys
import pandas as pd
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'acquisition'))
import merge_reads

REL = os.path.join(REPO, 'data', 'callouts', 'channel_reads.csv')


def test_split_and_merge_roundtrip(tmp_path):
    d = pd.read_csv(REL, dtype=str, keep_default_na=False)
    a = d[['cond', 'idx', 'panel', 'gold', 'tess', 'tess_conf', 'easy', 'easy_conf']].sample(frac=1, random_state=1)
    b = d[['cond', 'idx', 'gold', 'vlm', 'vlm_logprob']].sample(frac=1, random_state=2)
    a.to_csv(tmp_path / 'reads.csv', index=False, lineterminator='\n')
    b.to_csv(tmp_path / 'vlm.csv', index=False, lineterminator='\n')
    merge_reads.merge(str(tmp_path / 'reads.csv'), str(tmp_path / 'vlm.csv'), str(tmp_path / 'out.csv'))
    h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
    assert h(tmp_path / 'out.csv') == h(REL)
