from django.db import models
from django import http
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.http import require_POST
from blog.models import Blog,Entry,Comment,Category
from utils.utils import paginator,urldecode,sendmail,render
from django.utils import simplejson
from django.contrib.sites.models import Site
from blog.forms import CommentForm
from django.shortcuts import get_object_or_404
from tagging.models import Tag, TaggedItem
import blog.signals as signals
import logging

g_blog=Blog.get()

def get_comment_cookie_meta(request):
    return {}

def index(request):
    page=request.GET.get('page',1)
    entries = Entry.objects.get_posts()
    return render(request,'index.html',{'entries':entries,'ishome':True,'page':page})

def singlePost(request,slug=None):
    if slug:
        slug=urldecode(slug)
        entrys=Entry.objects.filter(slug=slug)
        entry=entrys[0]
    entry.updateReadtimes()
    return render(request,"single.html",{'entry':entry,'comment_meta':get_comment_cookie_meta(request)})

def singlePage(request,slug=None):
    if slug:
        slug=urldecode(slug)
        entrys=Entry.objects.filter(link='page/'+slug)
        entry=entrys[0]
    entry.updateReadtimes()
    
    return render(request,"page.html",{'entry':entry,'current':entry.link,
                                       'comment_meta':get_comment_cookie_meta(request)})


def singlePostByID (request,id=None):
    entry=Entry.objects.get(id=id)
    entry.updateReadtimes()
    return render(request,"single.html",{'entry':entry,'comment_meta':get_comment_cookie_meta(request)})

def recentComments(request,page=1):
    page=request.GET.get('page',1)
    page = int(page)
    allcomment=Comment.objects.all()
    comments = paginator(allcomment,g_blog.comments_per_page,page)
    t = get_template('themes/default/recentcomments.html')
    html = t.render(Context({'comments': comments}))
    json = simplejson.dumps((True,html))
    return HttpResponse(json)

def tag(request,tag):
    if tag:
        page=request.GET.get('page',1)
        tag = get_object_or_404(Tag, name =tag)
        entries=TaggedItem.objects.get_by_model(Entry, tag).order_by('-date')
        return render(request,'tag.html',{'entries':entries,'tag':tag,'page':page,'pagi_path': request.path})
    else:
        return HttpResponseRedirect('404.html')
    
def category(request,name):
    try:
        if name:
            cat = Category.objects.get(slug=name)
            page=request.GET.get('page',1)
            entries=Entry.objects.get_posts().filter(category=cat)
            return render(request,'category.html',{'entries':entries,'category':cat,'page':page})
    except:
        return HttpResponseRedirect('404.html')


def archives(request,year,month):
    page=request.GET.get('page',1)
    entries=Entry.objects.get_post_by_date(year,month)
    return render(request,'archives.html',{'entries':entries,'page':page,'year':year,'month':month})

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
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
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

    comment.save()
    
    #validate comment is or not akismet
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )
    
    if comment.parent_id != '0':
        old_c=comment.parent
        entry=comment.object
        domain=Site.objects.get_current().domain
        if old_c.mail_notify:
            sendmail({'old':old_c,"comment":comment,
                      'entry':entry,'blog':g_blog,'domain':domain},
                      'new Comment for ' +entry.title,old_c.email)

    response = HttpResponseRedirect('%s#comment-%d' % (target.fullurl(), comment.id))

    return response


def anypage(request,slug):
    return HttpResponseRedirect('/')