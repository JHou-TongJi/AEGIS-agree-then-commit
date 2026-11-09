"""A11 -- Verifiers that live in the record rather than in the crop.

(i)  Master list (122 real rows, structural columns only): the traffic light and the status are
     a bijection (1 Problem identified, 2 in Process, 3 Solution identified, 4 solved).  We check
     the bijection on the data and compute how many single-digit misreads of the traffic light
     the status column would expose.
(ii) Calendar-week tokens of the seven sheets (local only): a domain guard for week codes --
     the week number must be 1..53 and the year prefix, when present, 2019..2026 -- applied to
     each channel's reads, and the vote re-evaluated with the guard.
"""
import json, os, re
from common import *  # noqa
from aegis.policies import majority, cascade


def wk_guard(v):
    if v is None:
        return None
    m = re.match(r'^(\d{2,4})?(CW|KW)(\d{1,2})', v)
    if not m:
        return None
    yr, wk = m.group(1), int(m.group(3))
    if not 1 <= wk <= 53:
        return None
    if yr is not None and len(yr) == 4 and not 2019 <= int(yr) <= 2026:
        return None
    if yr is not None and len(yr) == 2 and not 19 <= int(yr) <= 26:
        return None
    return v


def main():
    out = {}
    m = pd.read_csv(os.path.join(DATA, 'masterlist', 'issue_records_structural.csv'))
    BIJ = {1: 'Problem identified', 2: 'in Process', 3: 'Solution identified', 4: 'solved'}
    ok = sum(BIJ.get(int(t)) == s for t, s in zip(m.traffic_light, m.status))
    # single-digit misread of the traffic light: any of the other three legal digits
    exposed = 0; total = 0
    for t, s in zip(m.traffic_light, m.status):
        for wrong in (1, 2, 3, 4):
            if wrong == int(t):
                continue
            total += 1
            exposed += BIJ[wrong] != s
    out['masterlist'] = dict(rows=int(len(m)), bijection_holds=int(ok), single_misreads=total,
                             exposed_by_status=exposed, distribution=m.traffic_light.value_counts().to_dict())
    prev = os.path.join(OUT, 'a11_record_constraints.json')
    if os.path.exists(prev) and 'week_codes' in json.load(open(prev)):
        out['week_codes'] = json.load(open(prev))['week_codes']
    b = load_b()
    if b is not None:
        w = b[b.kind == 'week_code'].copy()
        rows = {}
        for guard in (False, True):
            dec = []
            for _, x in w.iterrows():
                it = {c: (wk_guard(x[c + '_c']) if guard else x[c + '_c']) for c in CHANNELS}
                dd, val, _ = majority(it)
                dec.append((dd == 'commit', dd == 'commit' and val != x.ref_c))
                for c in CHANNELS:
                    pass
            D = pd.DataFrame(dec, columns=['com', 'wrong'])
            sil = {c: int(sum((wk_guard(x[c + '_c']) if guard else x[c + '_c']) is not None and
                              (wk_guard(x[c + '_c']) if guard else x[c + '_c']) != x.ref_c
                              for _, x in w.iterrows())) for c in CHANNELS}
            rows['guard' if guard else 'no_guard'] = dict(vote_coverage=round(D.com.mean(), 4),
                                                          vote_wrong=int(D.wrong.sum()),
                                                          silent_reads=sil)
        out['week_codes'] = dict(reads=int(len(w)), **rows)
    json.dump(out, open(os.path.join(OUT, 'a11_record_constraints.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
