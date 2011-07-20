from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from settings import YOUFLOG_VERSION
import re

_HTML_TYPES = ('text/html', 'application/xhtml+xml')
HTML_TITLE_RE = re.compile(r'(</title>)', re.IGNORECASE)

class RpcMiddleware(object):
    xmlrpc_url = reverse('xmlrpc')

    def process_response(self, request, response):
        if response.status_code == 200:
            response['X-Pingback'] = request.build_absolute_uri(self.xmlrpc_url)
        return response
    
    def process_request(self, request):
        if request.path == '/rpc':
            request.csrf_processing_done = True
        return None
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        return None
    
    
class VersionMiddleware(object):
    
    def process_response(self,request,response):
        if response['Content-Type'].split(';')[0] in _HTML_TYPES:
           def add_version_meta(match):
               return mark_safe(match.group() + '<meta name="generator" content="youflog %s" />'%YOUFLOG_VERSION)
        
           a = response.content
           response.content, n = HTML_TITLE_RE.subn(add_version_meta, response.content)
        return response
        