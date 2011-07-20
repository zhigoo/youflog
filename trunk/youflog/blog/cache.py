#!/usr/bin/env python
# *_* encoding=utf-8*_*
from django.core.cache import cache
from settings import CACHE_PREFIX

get_cache_key= lambda key: "cache::%s::%s" % (CACHE_PREFIX, key)

def get(key):
    return cache.get(get_cache_key(key))

def set(key,value,timeout=600):
    cache.set(get_cache_key(key), value, timeout)
    
def delete(key):
    cache.delete(get_cache_key(key))
    
def clear():
    cache.clear()