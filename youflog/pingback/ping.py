import re
from urlparse import urlsplit
from xmlrpclib import ServerProxy, Fault, ProtocolError
from urllib2 import urlopen
from urlparse import urljoin
import socket
import threading
import logging

from BeautifulSoup import BeautifulSoup
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse

from pingback.models import PingbackClient

def maybe_call(smth):
    if callable(smth):
        return smth()
    else:
        return smth

def search_link(content):
    match = re.search(r'<link rel="pingback" href="([^"]+)" ?/?>', content)
    return match and match.group(1)

class PingBackThread(threading.Thread):
    def __init__(self, instance, url, links):
        threading.Thread.__init__(self)
        self.instance = instance
        self.url = url
        self.links = links
        
    def run(self):
        ctype = ContentType.objects.get_for_model(self.instance)
        
        for link in self.links:
            try:
                PingbackClient.objects.get(url=link, content_type=ctype,object_id=self.instance.id)
            except Exception, e:
                pingback = PingbackClient(object=self.instance, url=link)
                try:
                    f = urlopen(link)
                    server_url = f.info().get('X-Pingback', '') or search_link(f.read(512 * 1024))
                    logging.info("start ping %s"%server_url)
                    if server_url:
                        server = ServerProxy(server_url)
                        try:
                            result = server.pingback.ping(self.url, link)
                            logging.info('ping result: %s' %result)
                        except Exception, e:
                            logging.info(e)
                            pingback.success = False
                        else:
                            pingback.success = True
                            pingback.save()
                except (IOError, ValueError, Fault), e:
                    pass

def ping_external_links(content_attr=None,instance=None,
                        url_attr='get_absolute_url'):
    if instance is None: return
    site = getattr(instance, 'site', Site.objects.get_current())
    content = maybe_call(getattr(instance, content_attr))
    url = maybe_call(getattr(instance, url_attr))
    if not (url.startswith('http://') or url.startswith('https://')):
        url = '%s://%s/%s' % (getattr(settings, 'SITE_PROTOCOL', 'http'),site.domain, url)
    
    def is_external(external, url):
        path_e = urlsplit(external)[2]
        path_i = urlsplit(url)[2]
        return path_e != path_i
    
    soup = BeautifulSoup(content)
    links = [a['href'] for a in soup.findAll('a')
                 if a.has_key('href') and is_external(a['href'], url)]
    pbt = PingBackThread(instance=instance, url=url, links=links)
    pbt.start()
