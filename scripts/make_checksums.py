"""Write checksums.sha256 for every file under data/ and results/ (sha256sum format).

    python scripts/make_checksums.py            # rewrite checksums.sha256
    python scripts/make_checksums.py --check    # verify (same as `sha256sum -c checksums.sha256`)
"""
import hashlib, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'checksums.sha256')


def files():
    for top in ('data', 'results'):
        for d, dirs, fs in os.walk(os.path.join(REPO, top)):
            dirs[:] = sorted(x for x in dirs if x != '__pycache__')
            for f in sorted(fs):
                if f.endswith('.pyc'):
                    continue
                yield os.path.relpath(os.path.join(d, f), REPO).replace(os.sep, '/')


def digest(rel):
    h = hashlib.sha256()
    with open(os.path.join(REPO, rel), 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_sums():
    out = {}
    for line in open(OUT, encoding='utf8'):
        line = line.rstrip('\n')
        if line:
            h, rel = line.split('  ', 1)
            out[rel] = h
    return out


def check():
    sums, bad = read_sums(), []
    for rel, h in sums.items():
        if not os.path.exists(os.path.join(REPO, rel)) or digest(rel) != h:
            bad.append(rel)
    extra = sorted(set(files()) - set(sums))
    return bad, extra


if __name__ == '__main__':
    if '--check' in sys.argv:
        bad, extra = check()
        for b in bad:
            print('FAILED', b)
        for e in extra:
            print('NOT LISTED', e)
        print('checksums OK' if not (bad or extra) else 'checksums differ')
        sys.exit(1 if (bad or extra) else 0)
    with open(OUT, 'w', encoding='utf8', newline='\n') as fh:
        for rel in sorted(files()):
            fh.write('%s  %s\n' % (digest(rel), rel))
    print('wrote', OUT)
