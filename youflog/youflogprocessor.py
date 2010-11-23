from django.contrib.sites.models import Site
from blog.models import Blog

def side(request):
    blog=Blog.get()
    site=Site.objects.get_current()
    return locals()
