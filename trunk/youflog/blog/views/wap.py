#!/usr/bin/env python
# *_* encoding=utf-8*_*

from blog.models import Entry,Comment,Category,Blog
from utils.utils import paginator,render_response
from blog import cache
def index(request):
    page=request.GET.get('page',1)
    page = int(page)
    entrys = cache.get('wap_index')
    if not entrys:
        entrys = Entry.objects.get_posts()
        cache.set('wap_index',entrys)
    categories = cache.get('wap_category')
    if not categories:
        categories=Category.objects.all()
        cache.set('wap_category',categories)
    comments=Comment.objects.in_public().exclude(email=Blog.get().email)[:8]
    return render_response(request,'wap/index.html',locals())

def single(request,id=None):
    id=int(id)
    page=request.GET.get('page',1)
    page=int(page)
    entry = cache.get('wap_entry_'+str(id))
    if not entry:
        entry=Entry.objects.get(id=id)
        cache.set('wap_entry_'+str(id),entry)
    comments=entry.comments.in_public().exclude(email=Blog.get().email)
    comments = paginator(comments,10,page)
    return render_response(request,'wap/single.html',{'entry':entry,'comments':comments})

def category(request,id=None):
    id=int(id)
    cate=Category.objects.get(id=id)
    page=request.GET.get('page',1)
    entries=Entry.objects.get_posts().filter(category=cate)
    entries = paginator(entries,10,page)
    return render_response(request,'wap/category.html',{'entrys':entries,'category':cate})