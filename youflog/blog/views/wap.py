#!/usr/bin/env python
# *_* encoding=utf-8*_*

from blog.models import Entry,Comment,Category,Blog
from utils.utils import paginator,render_response

def index(request):
    page=request.GET.get('page',1)
    page = int(page)
    entrys = Entry.objects.get_posts()
    categories=Category.objects.all()
    comments=Comment.objects.in_public().exclude(email=Blog.get().email)[:8]
    return render_response(request,'wap/index.html',locals())

def single(request,id=None):
    id=int(id)
    page=request.GET.get('page',1)
    page=int(page)
    entry=Entry.objects.get(id=id)
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