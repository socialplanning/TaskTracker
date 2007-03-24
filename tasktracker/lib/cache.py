#caches = {}

def get_cached(environ, cache_name, key, default_func,
               expiretime = 60, default_args = None, default_kwargs = None):
#    global caches
    beaker = environ['beaker.cache']
#    if not caches.has_key(cache_name):
#        caches[cache_name] = beaker.get_cache(cache_name)  # why? -egj
    
#    cache = caches[cache_name]
    cache = beaker.get_cache(cache_name)

    value = None
    if key in cache:
        value = cache.get_value(key, expiretime=expiretime)
    if not value:
# @@ why? - egj
        if default_args is None:
            default_args = []
        if default_kwargs is None:
            default_kwargs = {}
        value = default_func(*default_args, **default_kwargs)
        cache.set_value(key, value)
    return value
