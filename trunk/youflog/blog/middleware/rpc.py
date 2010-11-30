class RpcMiddleware(object):
    def process_request(self, request):
        if request.path == '/rpc':
            request.csrf_processing_done = True
        return None
    def process_view(self, request, callback, callback_args, callback_kwargs):
        return None
        