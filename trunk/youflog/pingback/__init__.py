# -*- coding: utf-8 -*-

import logging
from urlparse import urlsplit
from urllib2 import urlopen ,HTTPError, URLError
from xmlrpclib import Fault
from BeautifulSoup import BeautifulSoup

from django.conf import settings
from django.core import urlresolvers
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import get_resolver, get_callable
from django.utils.html import strip_tags
from django.utils.encoding import force_unicode, smart_str
import threading
from pingback.models import Pingback
from pingback.ping import ping_external_links
from blog.models import Entry

VERSION = (0, 1, 3)
__version__ = '.'.join(map(str, VERSION))
__all__ = ['Pingback', 'ping_external_links', 
           'handler_pingback', '__version__']

def handler_pingback(source,target):
    logging.info('receive pingback from %s to %s'%(source,target))
    try:
        logging.info('open url %s' %source)
        doc = urlopen(source)
    except Exception ,e:
        logging.info(e)
        raise Fault(16, 'The source URL does not exist.%s'%source)
    soup = BeautifulSoup(doc.read())
    
    mylink = soup.find('a', href=target)
    if not mylink:
        raise Fault(17, 'The post does not include URL [%s]'%target)
    
    title = soup.find('title')
    if title:
        title = strip_tags(unicode(title))
    else:
        title = 'Unknown title'
    
    content = unicode(mylink.findParent())
    logging.info(content)
    i = content.index(unicode(mylink))
    content = strip_tags(content)
    if len(content) > 200:
        start = i - max_length/2
        if start < 0:
            start = 0
        end = i + len(unicode(mylink)) + max_length/2
        if end > len(content):
            end = len(content)
        content = content[start:end]
    
    scheme, server, path, query, fragment = urlsplit(target)
    
    
    if path.startswith('/'):
        path=path[1:]
        
    try:
        post = Entry.objects.get(link=path)
    except Exception ,e:
        raise Fault(18, 'The post does not exists.')
    
    content_type = ContentType.objects.get_for_model(post)
    pings = Pingback.objects.filter(url=source, content_type=content_type, object_id=post.id)
    if pings.count() <= 0 :
        pb = Pingback(object=post, url=source, content=content.encode('utf-8'), title=title.encode('utf-8'), approved=True)
        pb.save()
        return 'success'
    else:
        raise Fault(19, 'pingback already registered!')