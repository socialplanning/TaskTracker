
# Copyright (C) 2006 The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 
# 51 Franklin Street, Fifth Floor, 
# Boston, MA  02110-1301
# USA

def get_cached(environ, cache_name, key, expiretime, default_func,
               *default_args, **default_kwargs):
    return default_func(*default_args, **default_kwargs)

    beaker = environ['beaker.cache']
    cache = beaker.get_cache(cache_name)

    value = None
    if key in cache:
        value = cache.get_value(key, expiretime=expiretime)
    if not value:
        value = default_func(*default_args, **default_kwargs)
        cache.set_value(key, value)
    return value
