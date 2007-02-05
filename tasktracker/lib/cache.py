caches = {}

def get_cached(environ, cache_name, key, default_func, default_args = None, default_kwargs = None):
    global caches
    beaker = environ['beaker.cache']
    if not caches.has_key(cache_name):
        caches[cache_name] = beaker.get_cache(cache_name)

    cache = caches[cache_name]
    value = None
    if key in cache:
        try:
            value = cache[key]
        except KeyError:
            value = None
    if not value:
        if default_args is None:
            default_args = []
        if default_kwargs is None:
            default_kwargs = {}
        value = default_func (*default_args, **default_kwargs)
        cache.set_value(key, value)
    return value
