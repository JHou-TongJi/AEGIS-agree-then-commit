"""README.md shows tables that are formatted from results/; they must not drift from it."""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import make_readme_tables as m


def test_readme_tables_are_current():
    text = open(os.path.join(REPO, 'README.md'), encoding='utf8').read()
    for name in m.TABLES:
        assert m.block(name) in text, 'README table %r is stale: run scripts/make_readme_tables.py --write' % name
