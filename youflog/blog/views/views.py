#!/usr/bin/env python
# *_* encoding=utf-8*_*
from django.db import models
from django import http
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST
from blog.models import Blog,Entry,Comment,Category,OptionSet
from utils.utils import paginator,urldecode,render,loadTempalte
from django.utils import simplejson
from blog.forms import CommentForm
from django.shortcuts import get_object_or_404
from tagging.models import Tag, TaggedItem
import blog.comments.signals as signals
import blog.cache as cache
from django.views.decorators.cache import cache_page
import Image,ImageFont,ImageDraw,cStringIO,random
from settings import CAPTCHA_FONT

def get_comment_cookie_meta(request):
    author = ''
    email = ''
    weburl = ''
    if 'author' in request.COOKIES:
        author = request.COOKIES['author']
    if 'email' in request.COOKIES:
        email = request.COOKIES['email']
    if 'weburl' in request.COOKIES:
        weburl = request.COOKIES['weburl']
    return {'author': author, 'email': email, 'url': weburl}

def index(request):
    page=request.GET.get('page',1)
    posts=cache.get_cache('index_posts')
    if not posts:
        posts = Entry.objects.get_posts()
        cache.set_cache('index_posts',posts)
    return render(request,'index.html',{'entries':posts,'ishome':True,'page':page})

def singlePost(request,slug):
    if slug:
        slug=urldecode(slug)
        try:
            entry=Entry.objects.get(link=slug)
        except:
            return render_to_response('404.html')
        entry.updateReadtimes()
        
        if entry.entrytype=='post':
            return render(request,"single.html",{'entry':entry,'comment_meta':get_comment_cookie_meta(request)})
        else:
            return render(request,"page.html",{'entry':entry,'current':entry.link,
                                       'comment_meta':get_comment_cookie_meta(request)})
    else:
        return render_to_response('404.html')

def singlePostByID (request,id=None):
    try:
        entry=Entry.objects.get(id=id)
        entry.updateReadtimes()
    except:
        return render_to_response('404.html')
    return render(request,"single.html",{'entry':entry,'comment_meta':get_comment_cookie_meta(request)})

def recentComments(request,page=1):
    page=request.GET.get('page',1)
    page = int(page)
    allcomment=Comment.objects.exclude(email=Blog.get().email).filter(is_public=True).order_by('-date')
    comments = paginator(allcomment,10,page)
    t = loadTempalte('recentcomments.html')
    html = t.render(Context({'comments': comments}))
    json = simplejson.dumps((True,html))
    return HttpResponse(json)

@cache_page(60*10)
def tag(request,tag):
    if tag:
        page=request.GET.get('page',1)
        tag = get_object_or_404(Tag, name =tag)
        entries=TaggedItem.objects.get_by_model(Entry, tag).order_by('-date')
        response=render(request,'archive.html',{'archtype':'tag','entries':entries,'tag':tag,'page':page,'pagi_path': request.path})
        return response
    else:
        return HttpResponseRedirect('404.html')

@cache_page(60*10)
def category(request,name):
    try:
        if name:
            cat = Category.objects.get(slug=name)
            page=request.GET.get('page',1)
            entries=Entry.objects.get_posts().filter(category=cat)
            return render(request,'archive.html',{'archtype':'category','entries':entries,'category':cat,'page':page})
    except:
        return HttpResponseRedirect('404.html')

@cache_page(60*10)
def archives(request,year,month):
    page=request.GET.get('page',1)
    posts=Entry.objects.get_post_by_date(year,month)
    return render(request,'archive.html',{'archtype':'archive','entries':posts,'page':page,'year':year,'month':month})

def calendar(request,year,month,day):
    page=request.GET.get('page',1)
    posts=Entry.objects.get_post_by_day(year,month,day)
    return render(request,'archive.html',{'archtype':'calendar','entries':posts,'page':page,'year':year,'month':month,'day':day})

class CommentPostBadRequest(http.HttpResponseBadRequest):
   
    def __init__(self, why):
        super(CommentPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("400-debug.html", {"why": why})

@require_POST
def post_comment(request, next = None):
    
    data = request.POST.copy()
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    checkcode = data.get('safecode') == request.session['safecode']
    if not checkcode:
        return CommentPostBadRequest("验证码可不要写错了!")
        
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except (TypeError,AttributeError,ObjectDoesNotExist):
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))

    form = CommentForm(target, data=data)
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    if form.errors:
        message = None
        for field in ['author', 'email', 'content', 'url']:
            if field in form.errors:                                              
                if form.errors[field][0]:                                         
                    message = '[%s] %s' % (field.title(), form.errors[field][0].capitalize())
                    break
        return render_to_response('400-debug.html', {'why': message})

    comment = form.get_comment_object()
    comment.parent_id = data['parent_id']
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    comment.useragent=request.META.get('HTTP_USER_AGENT','unknown')

    comment.save()
    
    #validate comment is or not akismet
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )
    #send email
    signals.comment_was_submit.send(
        sender  = comment.__class__,
        comment = comment                             
    )
    response = HttpResponseRedirect(comment.get_absolute_url())
    try:
        response.set_cookie('author', comment.author, max_age = 31536000)
        response.set_cookie('email', comment.email, max_age = 31536000)
        response.set_cookie('weburl', comment.weburl, max_age = 31536000)
    except:
        pass
    
    return response

def safecode(request):
    fontSize=15
    image = Image.new('RGB', (80, 20), (255, 255, 255))
    font = ImageFont.truetype(CAPTCHA_FONT, fontSize)
    draw = ImageDraw.Draw(image)
    tp=OptionSet.get('safecode_type', 1);
    if tp == str(1):
        code=[]
        gap = 5
        start = 0
        for i in range(0, 4):
            x = start + fontSize * i + random.randint(0, gap) + gap * i
            txt=str(random.randint(0,9))
            code.append(txt)
            draw.text((x,5), txt,font=font,fill=(100,211, 90))
        del draw
        request.session['safecode']=''.join(code)
    else:
        first=random.randint(0,9)
        second=random.randint(0,9)
        draw.text((0,5), str(first)+'+'+str(second),font=font,fill=(100,211, 90))
        del draw
        request.session['safecode']=str(first+second)
    buf = cStringIO.StringIO()
    image.save(buf, 'gif') 
    return HttpResponse(buf.getvalue(),'image/gif')

from django.db.models import Q
def search(request):
    page=request.GET.get('page',1)
    query = escape(request.GET.get('s', ''))
    qd = request.GET.copy()
    if 'page' in qd:
        qd.pop('page')
    posts=None
    if query:
        qset = (
            Q(title__icontains=query)
        )
        posts = Entry.objects.filter(qset, published=True,entrytype='post').distinct().order_by('-date')
    return render(request,'search.html',{'entries':posts,'page':page,'query':query,'pagi_path': qd.urlencode()})