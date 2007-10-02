from decorator import decorator
from pylons import c

def _make_key(f, args, kw):
    return tuple([f, tuple(args), tuple(sorted(kw.items()))])

def memoize(f, *args, **kw):
    if not c.memos:
        c.memos = {}

    key = _make_key(f, args, kw)
    if not c.memos.has_key(key):
        c.memos[key] = f(*args, **kw)

    return c.memos[key]

memoize=decorator(memoize)
