"""Canonicalisation of a channel reading into a field value.

Canonicalisation is deliberately conservative: it removes layout noise (whitespace, a trailing
full stop, a decimal comma) but never edits a digit.  A reading that does not fit the declared
format of the field is *invalid*, not repaired; repairing is how silent errors are made.
"""
import re

NUM_1DP = re.compile(r'^-?\d{1,2}(\.\d)?$')          # metrology deviation, mm, <= 1 decimal
NUM_ANY = re.compile(r'^[-+]?(\d+([.]\d+)?|\.\d+)$')
WEEK = re.compile(r'^\d{0,4}(CW|KW)\d', re.I)


def squash(s):
    return ''.join(str(s).split()) if s is not None else ''


def canon_numeric(s, fmt=NUM_1DP):
    """Return a float for a format-valid numeric reading, else None."""
    t = squash(s).replace(',', '.')
    t = t.rstrip('.')
    if t in ('', '-', '.'):
        return None
    if not fmt.match(t):
        return None
    v = float(t)
    return 0.0 if v == 0 else v


def canon_token(s, kind):
    """Canonical string for a free token of a given kind (dataset B)."""
    t = squash(s)
    if kind == 'numeral':
        t = t.replace(',', '.') if t.count(',') == 1 and t.count('.') == 0 else t
        t = t.rstrip('.')
        return t if NUM_ANY.match(t) else None
    if kind == 'week_code':
        t = t.upper()
        return t if WEEK.match(t) else None
    return t if t else None
