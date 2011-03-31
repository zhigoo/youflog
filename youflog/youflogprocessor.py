from django.contrib.sites.models import Site
from blog.models import Blog

def side(request):
    blog=Blog.get()
    site=Site.objects.get_current()
    domain = site.domain
    if domain.endswith('/'):
        domain= domain[:-1]
    xmlrpcurl = 'http://%s/xmlrpc/'%(domain)
    return locals()
