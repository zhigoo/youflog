#!/usr/bin/env python
# *_* encoding=utf-8*_*

from blog.models import Entry,Comment,Category
from utils.utils import paginator,render_response

def index(request):
    page=request.GET.get('page',1)
    page = int(page)
    entrys = Entry.objects.get_posts()
    categories=Category.objects.all()
    comments=Comment.objects.all().order_by('-date')[:8]
    return render_response(request,'wap/index.html',{'entrys':entrys,'comments':comments,'page':page,'categories':categories})

def single(request,id=None):
    id=int(id)
    page=request.GET.get('page',1)
    page=int(page)
    entry=Entry.objects.get(id=id)
    comments=entry.comments.all()
    comments = paginator(comments,10,page)
    return render_response(request,'wap/single.html',{'entry':entry,'comments':comments})

def category(request,id=None):
    id=int(id)
    cate=Category.objects.get(id=id)
    page=request.GET.get('page',1)
    entries=Entry.objects.get_posts().filter(category=cate)
    entries = paginator(entries,10,page)
    return render_response(request,'wap/category.html',{'entrys':entries,'category':cate})