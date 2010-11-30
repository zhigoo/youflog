from django.core.cache import cache
from settings import CACHE_PREFIX

get_cache_key= lambda key: "cache::%s::%s" % (CACHE_PREFIX, key)

def get_cache(key):
    return cache.get(get_cache_key(key))

def set_cache(key,value,timeout=600):
    cache.set(get_cache_key(key), value, timeout)
    
def delete_cache(key):
    cache.delete(get_cache_key(key))