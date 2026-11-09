"""Unit tests for the decision layer and regression tests for the headline numbers."""
import json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'src')); sys.path.insert(0, os.path.join(REPO, 'scripts'))
from aegis.canon import canon_numeric, canon_token
from aegis.policies import single, majority, cascade, with_domain
from aegis.crc import calibrate, min_feasible_alpha
from aegis.corroboration import candidate


def test_canon_never_edits_digits():
    assert canon_numeric('0.2') == 0.2
    assert canon_numeric(' -0.2 ') == -0.2
    assert canon_numeric('0,6') == 0.6
    assert canon_numeric('0.7.') == 0.7
    assert canon_numeric('0.22') is None      # second decimal place is not in the field grammar
    assert canon_numeric('07') == 7.0         # a dropped separator is a legal value: only the range guard catches it
    assert canon_numeric('.1.4') is None
    assert canon_numeric('') is None


def test_canon_token_kinds():
    assert canon_token('24CW12', 'week_code') == '24CW12'
    assert canon_token('2025,', 'numeral') == '2025'
    assert canon_token('', 'alnum') is None


def test_policies():
    it = dict(tess=1.4, easy=1.4, vlm=1.4)
    assert majority(it)[:2] == ('commit', 1.4)
    assert cascade(it, ('easy', 'tess', 'vlm'))[:2] == ('commit', 1.4)
    it = dict(tess=0.2, easy=0.2, vlm=-0.2)        # the sign-loss collision
    assert majority(it)[:2] == ('commit', 0.2)
    it = dict(tess=7.0, easy=7.0, vlm=0.0)
    assert cascade(with_domain(it, -3, 3), ('easy', 'tess', 'vlm'))[0] == 'escalate'
    assert single(dict(tess=None, easy=None, vlm=None), 'tess')[0] == 'escalate'


def test_cascade_cost_order():
    it = dict(tess=0.5, easy=0.5, vlm=0.5)
    c1 = cascade(it, ('easy', 'tess', 'vlm'))[2]
    c2 = cascade(it, ('vlm', 'tess', 'easy'))[2]
    assert c1 < c2


def test_candidate_score():
    v, c = candidate(dict(tess=0.9, easy=9.0, vlm=0.9, vlm_lp=np.log(0.996)))
    assert v == 0.9 and abs(c - 2.996) < 1e-6


def test_crc_floor():
    assert abs(min_feasible_alpha(90) - 1 / 91) < 1e-12
    lams = np.linspace(0, 1, 11)
    L = np.zeros((9, 11))
    assert calibrate(L, lams, 0.05) is None          # 1/10 > 0.05: infeasible even at zero risk
    assert calibrate(L, lams, 0.10) == 0.0


def test_headline_numbers():
    R = os.path.join(REPO, 'results')
    a1 = json.load(open(os.path.join(R, 'a1_summary.json')))
    assert a1['n_reads'] == 864
    assert abs(a1['easy']['acc'] - 0.8935) < 1e-4
    a2 = json.load(open(os.path.join(R, 'a2_detectors.json')))['callouts']
    assert round(a2['easy']['auroc_self'], 2) == 0.42
    assert a2['easy']['auroc_agree'] > 0.98
    a3 = json.load(open(os.path.join(R, 'a3_policies.json')))
    assert a3['majority-2of3']['n_wrong_committed'] == 2
    assert round(a3['cascade(easy>tess>vlm)']['cost_s'], 2) == 1.09
