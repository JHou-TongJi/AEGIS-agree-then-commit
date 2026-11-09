"""Format the result tables shown in README.md straight from results/*.json.

    python scripts/make_readme_tables.py          # prints the tables
    python scripts/make_readme_tables.py --write  # refreshes the marked blocks of README.md in place
    tests/test_readme.py                          # fails if README.md and results/ disagree

Nothing in the README tables is typed by hand: every cell is a rounded value read from the
JSON file named under the table.
"""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda f: json.load(open(os.path.join(REPO, 'results', f)))
pc = lambda x, d=1: f'{100 * x:.{d}f} %'


def channels():
    d = R('a1_summary.json')
    rows = ['| Channel | Exact match | Refused | Silent wrong | Silent share of its errors |',
            '|---|---:|---:|---:|---:|']
    for k, n in (('tess', 'Tesseract 4.1'), ('easy', 'EasyOCR 1.7'), ('vlm', 'SmolVLM-256M')):
        c = d[k]
        rows.append(f"| {n} | {pc(c['acc'])} | {pc(c['invalid'])} | {pc(c['silent'])} | "
                    f"{pc(c['silent_share_of_errors'], 0)} |")
    return '\n'.join(rows)


def detectors():
    d = R('a2_detectors.json')['callouts']
    rows = ['| Channel | Committed reads | Wrong | AUROC, own confidence | AUROC, corroboration by the others |',
            '|---|---:|---:|---:|---:|']
    for k, n in (('tess', 'Tesseract 4.1'), ('easy', 'EasyOCR 1.7'), ('vlm', 'SmolVLM-256M')):
        c = d[k]
        rows.append(f"| {n} | {c['n_committed']} | {c['n_wrong']} | {c['auroc_self']:.2f} | {c['auroc_agree']:.3f} |")
    return '\n'.join(rows)


def policies():
    d = R('a3_policies.json')
    names = [('single-tess', 'Tesseract alone'), ('single-easy', 'EasyOCR alone'), ('single-vlm', 'SmolVLM alone'),
             ('majority-2of3', '2-of-3 vote, all channels called'),
             ('cascade(easy>tess>vlm)', 'cascade EasyOCR > Tesseract > SmolVLM'),
             ('unanimous-3of3', 'unanimity of three')]
    rows = ['| Policy | Committed | Committed error | Wrong committed (of 864) | Cost per value |',
            '|---|---:|---:|---:|---:|']
    for k, n in names:
        c = d[k]
        rows.append(f"| {n} | {pc(c['coverage'])} | {pc(c['committed_error'], 2)} | {c['n_wrong_committed']} | "
                    f"{c['cost_s']:.2f} s |")
    a = R('a12_localisation.json')['recrop']['cascade+recrop|R=3']
    rows.append(f"| cascade + range guard (R = 3 mm) + re-crop | {pc(a['coverage'], 2)} | "
                f"{pc(a['committed_error'], 2)} | {a['n_wrong_committed']} | {a['cost_s']:.2f} s |")
    return '\n'.join(rows)


def risk_control():
    d = R('a5_crc.json')
    rows = ['| Requested bound α | Mean realised risk | Worst held-out block | Coverage | Infeasible folds |',
            '|---:|---:|---:|---:|---:|']
    for r in d['A']:
        rows.append(f"| {pc(r['alpha'], 1)} | {pc(r['mean_risk'], 2)} | {pc(r['worst_fold_unit'], 2)} | "
                    f"{pc(r['coverage'], 1)} | {r['infeasible_folds']} / {r['n_folds']} |")
    return '\n'.join(rows)


def tokens():
    d = R('a7_tokens.json')
    rows = ['| Token kind | Reads | EasyOCR alone: committed error | SmolVLM alone: committed error | '
            '2-of-3 vote: committed | 2-of-3 vote: committed error |',
            '|---|---:|---:|---:|---:|---:|']
    for k, n in (('numeral', 'numerals'), ('week_code', 'calendar-week codes'), ('alnum', 'alphanumeric strings'),
                 ('all', 'all tokens')):
        c = d[k]
        v = c['majority-2of3']
        rows.append(f"| {n} | {c['n']} | {pc(c['single-easy']['committed_error'])} | "
                    f"{pc(c['single-vlm']['committed_error'])} | {pc(v['coverage'])} | {pc(v['committed_error'], 2)} |")
    return '\n'.join(rows)


TABLES = {'channels': channels, 'detectors': detectors, 'policies': policies,
          'risk_control': risk_control, 'tokens': tokens}

def block(name):
    return '<!-- table:%s -->\n%s\n<!-- /table:%s -->' % (name, TABLES[name](), name)


def write_readme(path=os.path.join(REPO, 'README.md')):
    import re
    text = open(path, encoding='utf8').read()
    for k in TABLES:
        text, n = re.subn(r'<!-- table:%s -->.*?<!-- /table:%s -->' % (k, k),
                          lambda m: block(k), text, flags=re.S)
        assert n == 1, 'README.md needs exactly one <!-- table:%s --> block' % k
    open(path, 'w', encoding='utf8').write(text)


if __name__ == '__main__':
    import sys
    if '--write' in sys.argv:
        write_readme()
        print('README.md tables refreshed')
    else:
        for k in TABLES:
            print(block(k))
            print()
