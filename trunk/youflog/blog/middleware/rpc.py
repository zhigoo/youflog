from django.core.urlresolvers import reverse

class RpcMiddleware(object):
    xmlrpc_url = reverse('xmlrpc')

    def process_response(self, request, response):
        if response.status_code == 200:
            response['X-Pingback'] = request.build_absolute_uri(self.xmlrpc_url)
        return response
    
    def process_request(self, request):
        if request.path == '/xmlrpc':
            request.csrf_processing_done = True
        return None
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        return None
        