"""The shipped data and results are the files the paper's numbers were computed from."""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import make_checksums


def test_checksums_match_shipped_files():
    bad, extra = make_checksums.check()
    assert not bad, 'files changed since checksums.sha256 was written: %s' % bad
    assert not extra, 'files missing from checksums.sha256: %s' % extra
