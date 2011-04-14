#!/usr/bin/env python
# *_* encoding=utf-8*_*
import blog.cache as cache
from blog.models import Entry,Comment,Link,Category,OptionSet,Blog,UserProfile
from utils.utils import render_response
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.contrib.auth.models import User
from datetime import datetime
from blog.theme import ThemeIterator
from blog.forms import SettingForm
from settings import MEDIA_ROOT
from os.path import isdir, dirname
from tagging.models import Tag
from settings import DATABASES
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import blog.comments.signals as signals
import logging

#login process
def _login(request,username,password):
    ret=False
    if not username or not password:
        messages.add_message(request, messages.INFO, '错误：用户名或密码不能为空.')
        return ret
    user=authenticate(username=username,password=password)
    if user:
        if user.is_active:
            auth_login(request,user)
            ret=True
        else:
            messages.add_message(request, messages.INFO, '错误：用户没有激活')
    else:
        messages.add_message(request, messages.INFO, '错误：用户名或密码错误!')
    return ret

def logout(request):
    auth_logout(request)
    messages.add_message(request, messages.INFO, '您已退出.')
    return HttpResponseRedirect('/accounts/login')

def login(request):
    if request.method =='POST':
        name = request.POST.get('user','')
        passwd = request.POST.get('password','')
        if _login(request,name,passwd):
            return HttpResponseRedirect('/admin')
    return render_response(request,"admin/login.html",{})

@login_required
def index(request):
    
    post_count=Entry.objects.all().filter(entrytype='post').count()
    comment_count=Comment.objects.in_public().count()
    spam_count=Comment.objects.in_moderation().count()
    page_count=Entry.objects.all().filter(entrytype='page').count()
    category_count=Category.objects.count()
    tag_count=Tag.objects.count()
    comments=Comment.objects.all().exclude(email=Blog.get().email).filter(is_public=True).order_by('-date')[:10]
    return render_response(request,"admin/index.html",locals())

@login_required
@require_POST
def quick_post(request):
    title=request.POST.get('title')
    content=request.POST.get('content','')
    tags=request.POST.get('tags','')
    save=request.POST.get('save')
    publish=request.POST.get('publish')
    
    if not title and not content:
        return HttpResponse(u"文章标题和内容不能为空!")
    entry=Entry(title=title,content=content,tags=tags,slug='',allow_comment=True)
    entry.author=request.user
    entry.category_id=1
    if save:
        entry.save(False)
        html=u"<p>文章已保存.&nbsp;<a href='/admin/editpost/%s'>编辑文章</a></p>"%(str(entry.id))
    elif publish:
        entry.save(True)
        html=u"<p>文章已发布.&nbsp;<a href='%s' target='_blank'>查看文章</a></p>"%(entry.get_absolute_url())
    
    return HttpResponse(html)
    

@login_required
def all_posts(request):
    page=request.GET.get('page',1)
    all_posts = Entry.objects.all().filter(entrytype='post').order_by('-date')
    publish_posts=Entry.objects.get_posts()
    unpubcount=all_posts.count()-publish_posts.count()
    categories = Category.objects.all()
    archives=Entry.objects.dates('date','month')
    return render_response(request,"admin/posts.html",{'entrys':all_posts,\
                                   'publish_count':publish_posts.count(),'unpubcount':unpubcount,
                                   'all_count':all_posts.count(),'page':page,'categories':categories,'archives':archives})
@login_required
def all_pub_posts(request):
    page=request.GET.get('page',1)
    all_posts = Entry.objects.all().filter(entrytype='post').order_by('-date')
    publish_posts=Entry.objects.get_posts()
    unpubcount=all_posts.count()-publish_posts.count()
    categories = Category.objects.all()
    archives=Entry.objects.dates('date','month')
    return render_response(request,"admin/posts.html",{'entrys':publish_posts,\
                                   'publish_count':publish_posts.count(),'unpubcount':unpubcount,
                                   'all_count':all_posts.count(),'page':page,'categories':categories,'archives':archives})
@login_required
def unpub_posts(request):
    page=request.GET.get('page',1)
    all_posts = Entry.objects.all().filter(entrytype='post').order_by('-date')
    publish_posts=Entry.objects.get_posts()
    unpub_posts=Entry.objects.all().filter(entrytype='post',published=False).order_by('-date')
    unpubcount=all_posts.count()-publish_posts.count()
    categories = Category.objects.all()
    archives=Entry.objects.dates('date','month')
    return render_response(request,"admin/posts.html",{'entrys':unpub_posts,\
                                   'publish_count':publish_posts.count(),'unpubcount':unpubcount,
                                   'all_count':all_posts.count(),'page':page,'categories':categories,'archives':archives})

@login_required
def posts_by_category(request,slug):
    if slug:
        cat = Category.objects.get(slug=slug)
        posts=Entry.objects.get_posts().filter(category=cat)
        page=request.GET.get('page',1)
        return render_response(request,'admin/category_posts.html',{'posts':posts,'page':page})

@login_required
def admin_addpost(request):
    return render_response(request,"admin/post.html",{'cats':Category.objects.all(),\
                                                      'action':'add','entrytype':'post'})

@login_required
def edit_post(request,id):
    entry = Entry.objects.get(id=id)
    entrytype=request.GET.get('entrytype','post')
    def mapcategoy(cat):
        
        return {"id":cat.id,"name":cat.name,"slug":cat.slug,\
                "select":cat.id ==entry.category.id}
    
    cats = Category.objects.all();
    return render_response(request,"admin/post.html",\
                           {'entry':entry,'cats':map(mapcategoy,cats),\
                            'action':'edit','entrytype':entrytype})

@login_required
def post_delete(request):
    try:
        allchecks = request.POST.getlist("checks")
        for id in allchecks:
            entry = Entry.objects.get(id=id)
            entry.delete()
    finally:
        return HttpResponseRedirect('/admin/allposts')
    
@login_required
def submit_post(request):
    published=False
    if request.method == 'POST':
        title = request.POST['title']
        content=request.POST.get('content','')
        excerpt = request.POST.get('excerpt','')
        category_id = request.POST.get("category",1)
        tags = request.POST.get('tags','')
        slug=request.POST.get('slug','')
        allow_comment = request.POST.get('allow_comment',False)
        allow_pingback = request.POST.get('allow_pingback',False)
        action=request.POST.get('action','')
        posttype=request.POST.get('posttype','post')
        sticky=request.POST.get('sticky',False)
        
        sticky= True and sticky=='sticky'
        allow_comment= True and allow_comment == 'open'
        allow_pingback= True and allow_pingback == 'open'
        
        if request.POST.get('publish'):
            published = True
        elif request.POST.get('unpublish'):
            published = False
        else:
            published = request.POST.get('published')=='True'
        
        
        category=Category.objects.get(id=int(category_id))
        
        ctx={'action':action}
        
        if not (title and content):
            ctx.update({'msg':'Please input title and content.'})
            return render_response(request,"admin/post.html",ctx)
        
        if action== 'add':
            entry = Entry(title=title,content=content,excerpt=excerpt,\
                          category=category,slug=slug.replace(" ","-"))
            entry.tags=tags
            entry.allow_comment=allow_comment
            entry.allow_pingback=allow_pingback
            entry.entrytype=posttype
            entry.sticky=sticky
            entry.author=request.user
            if posttype and posttype =='page':
                menu_order=request.POST.get('order',0)
                if menu_order:
                    entry.menu_order=menu_order 
            
            entry.date=datetime.now()
            entry.save(published)
            
            def mapcategoy(cat):
                return  {"id":cat.id,"name":cat.name,\
                         "slug":cat.slug,"select":cat.id == int(category_id)}
            
            ctx.update({'action':'edit','entry':entry,\
                        'entrytype':posttype,'cats':map(mapcategoy,Category.objects.all())})
            
        elif action== 'edit':
            postid = request.POST.get('postid','')
            if postid:
                entry = Entry.objects.get(id=postid)
                entry.tags=tags
                entry.title=title
                entry.content=content
                entry.excerpt=excerpt
                entry.slug=slug.replace(" ","-")
                entry.entrytype=posttype
                entry.sticky=sticky
                entry.category=category
                entry.allow_pingback=allow_pingback
                if posttype and posttype =='page':
                    menu_order=request.POST.get('order',0)
                    entry.menu_order=menu_order
                entry.allow_comment=allow_comment
                entry.save(published)
                def mapcategoy(cat):
                    return  {"id":cat.id,"name":cat.name,"slug":cat.slug,"select":cat.id == entry.category.id}
    
                ctx.update({'action':'edit','entry':entry,\
                    'entrytype':posttype,'cats':map(mapcategoy,Category.objects.all())})
        else:
            pass
        
    return render_response(request,"admin/post.html",ctx)

@login_required
def delpost(request):
    id=request.GET.get('id')
    entry=get_object_or_404(Entry,id=id)
    entry.delete()
    return HttpResponseRedirect('/admin/allposts') 

@login_required
def addPage(request):
    return render_response(request,"admin/post.html",\
                {'cats':Category.objects.all(),'action':'add','entrytype':'page'})


def pages(request):
    page=request.GET.get('page',1)
    post_status = request.GET.get('post_status')
    
    all=Entry.objects.all().filter(entrytype='page')
    all_entrys = Entry.objects.all().filter(published = True).filter(entrytype='page')
    
    if post_status =='all':
        entrys = all
    else:
        entrys = all_entrys
    
    return render_response(request,"admin/pages.html",\
                           {'entrys':entrys,'publish_count':all_entrys.count(),'all_count':all.count(),
                            'page':page})

@login_required
def comments(request):
    page=request.GET.get('page',1)
    page = int(page)
    comments = Comment.objects.filter(is_public=True).order_by('-date')
    spam_count=Comment.objects.filter(is_public=False).count()
    return render_response(request,'admin/comments.html',{'page':page,'comments':comments,\
                                                          'spam_count':spam_count,'comment_count':comments.count()})
@login_required
def spam_comment(request):
    page=request.GET.get('page',1)
    page=int(page)
    comments = Comment.objects.filter(is_public=False).order_by('-date')
    comment_count=Comment.objects.filter(is_public=True).count()
    return render_response(request,'admin/comments.html',{'page':page,'comments':comments,\
                                                          'comment_count':comment_count,
                                                          'spam_count':comments.count()})
@login_required
def save_comment(request):
    comment_status=request.POST.get('comment_status')
    id=request.POST.get('id')
    comment=get_object_or_404(Comment,id=id)
    comment.author=request.POST.get('name')
    comment.email=request.POST.get('email')
    comment.weburl=request.POST.get('url')
    comment.content=request.POST.get('content')
    comment.is_public=True and (comment_status=='1' or comment_status ==1)
    comment.save()
    
    return HttpResponseRedirect('/admin/comments')
    
@login_required
def flag_comment_for_spam(request,id):
    approve=request.GET.get('approve',0)
    currpath = request.GET.get('currpath')
    comment=get_object_or_404(Comment,id=id)
    if int(approve) == 0:
        comment.is_public=False
    else:
        comment.is_public=True
    comment.save()
    if currpath:
        return HttpResponseRedirect(currpath)
    else:
        return HttpResponseRedirect('/admin/comments')
    
@login_required
def delete_single_comment(request,id):
    current_path = request.GET.get('currpath')
    comment=get_object_or_404(Comment,id=id)
    comment.delete()
    if current_path:
        return HttpResponseRedirect(current_path)
    else:
        return HttpResponseRedirect('/admin/comments')

@login_required
def edit_comment(request,id):
    comment=get_object_or_404(Comment,id=id)
    return render_response(request,'admin/comment-edit.html',{'comment':comment})

@login_required
def comment_delete(request):
    current_path = request.POST.get('currpath')
    try:
        allchecks = request.POST.getlist("checks")
        for id in allchecks:
            c = Comment.objects.get(id=id)
            c.delete()
    finally:
        if current_path:
            return HttpResponseRedirect(current_path)
        else:
            return HttpResponseRedirect('/admin/comments')

@login_required
def reply_comment(request):
    data = request.POST.copy()
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    path=data.get('path')
    user=request.user
    try:
        model = models.get_model(*ctype.split(".", 1))
        target = model._default_manager.get(pk=object_pk)
    except (TypeError,AttributeError,ObjectDoesNotExist):
        logging.info('object not exits')
    comment = Comment(content_type = ContentType.objects.get_for_model(target),
            object_pk    = force_unicode(target._get_pk_val()),
            author=user.username,
            email=user.email,
            weburl=user.get_profile().website,
            content=data.get('comment'),
            date  = datetime.now(),
            mail_notify=True,
            is_public    = True,
            parent_id    = data.get('parent_id'),
            )
    comment.save()
    signals.comment_was_submit.send(
        sender  = comment.__class__,
        comment = comment                             
    )
    return HttpResponseRedirect(path)
    
@login_required
def categories(request):
    page=request.GET.get('page',1)
    
    categories = Category.objects.all()
    return render_response(request,'admin/categories.html',{'categories':categories,'page':page})

@login_required
def addCategory(request):
    if request.method=='POST':
        name = request.POST['name']
        slug = request.POST['slug']
        desc = request.POST['desc']
        type = request.POST['type']
        if type and type == 'add':
            try:
                cats=Category.objects.filter(name=name)
                if cats.count() >= 1:
                    messages.add_message(request,messages.INFO,'categry [%s] already exits!'%(name))
                else:
                    cat = Category(name=name,slug=slug,desc=desc)
                    cat.save()
                    messages.add_message(request,messages.INFO,'categry [%s] save ok!'%(name))
            except:
                pass
                
        elif type and type == 'edit':
            id = request.POST.get('id','')
            cat = Category.objects.get(id=id)
            cat.name=name
            cat.slug=slug
            cat.desc=desc
            cat.save()
        return HttpResponseRedirect('/admin/categories')
@login_required
def editCategory(request,id):
    page=request.GET.get('page',1)
    try:
        id = int(id)
        cat=Category.objects.get(id=id)
    except:
        pass
    categories = Category.objects.all()
    return render_response(request,'admin/category.html',{'cat':cat,'categories':categories,'page':page})

@login_required
def deleteCategory(request):
    if request.method=='POST':
        action = request.POST.get('action','')
        checks = request.POST.getlist('checks')
        if checks or action == 'delete':
            for id in checks:
                if id:
                    cat = Category.objects.get(id=id)
                    cat.delete()
        return HttpResponseRedirect('/admin/categories')
    
def links(request):
    page = request.GET.get('page',1)
    links = Link.objects.all()
    return render_response(request,'admin/links.html',{'links':links,'page':page})

@login_required
def addLink(request):
    if request.method=='POST':
        type= request.POST.get('type','add')
        text = request.POST.get('text','')
        href = request.POST.get('href','http://www.iyouf.info')
        if not href.startswith('http://'):
            href = 'http://'+href
        comment = request.POST.get('comment','')
        if type and type == 'add':
            link=Link(text=text,href=href,comment=comment)
            link.save()
            cache.delete_cache('sidebar:links')
        else:
            id=request.POST.get('id','')
            link=Link.objects.get(id=id)
            link.text=text
            link.href=href
            link.comment=comment
            link.save()
            cache.delete_cache('sidebar:links')
    return HttpResponseRedirect('/admin/links')

@login_required
def deleteLink(request):
    if request.method=='POST':
        action = request.POST.get('action','')
        checks = request.POST.getlist('checks')
        if checks or action=='delete':
            for id in checks:
                link=Link.objects.get(id=id)
                link.delete()
                cache.delete_cache('sidebar:links')
        return HttpResponseRedirect('/admin/links')

@login_required
def editlink(request,id):
    page = request.GET.get('page',1)
    try:
        id = int(id)
        link = Link.objects.get(id=id)
    except:
        pass
    links = Link.objects.all()
    return render_response(request,'admin/link.html',{'link':link,'links':links,'page':page})

@login_required
def settings(request):
    themeIter=ThemeIterator()
    themes=[t for t in themeIter if t]
    site = Site.objects.get_current()
    form=SettingForm()
    return render_response(request,'admin/settings.html',{'themes':themes,'site':site,'form':form})

@login_required
def save_setting(request):
    if request.method=='POST':
        data=request.POST.copy()
        form=SettingForm(data=data)
        
        blog=form.get_form_object()
       
        theme = request.POST.get('theme','default')
        domain = request.POST.get('domain','')
        if domain.startswith('http://'):
            domain=domain[7:]
        if domain.endswith('/'):
            domain=domain[:-1]
        try:    
            blog.theme_name=theme
            blog.save()
            #site info
            site = Site.objects.get_current()
            site.domain=domain
            site.name=blog.title
            site.save()
            messages.add_message(request,messages.INFO,'setting save ok!')
        except:
            messages.add_message(request,messages.INFO,'setting save failure!')
        return HttpResponseRedirect('/admin/settings')
    
@login_required 
def media(request):
    return render_response(request,'admin/media.html',{})

from os import makedirs
@login_required
def upload_media(request):
    file_obj=request.FILES.get('file',None)
    if file_obj:
        filename=file_obj.name
        savepath='%s/%s'%(MEDIA_ROOT,filename.decode('utf8'))
        dir = dirname(savepath)
        if not isdir(dir):
            makedirs(dir)
        f = open(savepath, 'wb+')
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
    return HttpResponseRedirect('/admin/media')

@login_required
def setting_comment(request):
    gavatar=OptionSet.get('gavatar','gravatar_default')
    comments_per_page=OptionSet.get('comments_per_page',10)
    comments_notify=OptionSet.get('comments_notify',1)
    enable_akismet=int(OptionSet.get('akismet_enable',0))
    akismet_key=OptionSet.get('akismet_key')
    safecode_type=OptionSet.get('safecode_type',1)
    return render_response(request,'admin/comment_setting.html',locals())

@login_required
@require_POST
def save_commentOption(request):
    data=request.POST.copy()
    gavatar=data['gavatar']
    comments_per_page=data['comments_per_page']
    comments_notify=request.POST.get('comments_notify',0)
    akismet_enable=request.POST.get('akismet_enable')
    akismet_key=request.POST.get('akismet_key')
    safecode=request.POST.get('safecode_type')
    if akismet_enable:
        OptionSet.set('akismet_enable',1)
    else:
        OptionSet.set('akismet_enable',0)
    
    OptionSet.set('akismet_key',akismet_key)
    OptionSet.set('gavatar', gavatar)
    OptionSet.set('comments_per_page',comments_per_page)
    OptionSet.set('comments_notify',comments_notify)
    OptionSet.set('safecode_type',safecode)
    return HttpResponseRedirect('/admin/comment_setting')

@login_required
def permalink(request):
    domain = 'http://%s'%Site.objects.get_current().domain
    permalink_format=OptionSet.get('permalink_format', 'archive/%(id)s.html')
    permalink_structure=OptionSet.get('permalink_structure','%(year)s/%(month)s/%(day)s/%(postname)s.html')
    return render_response(request,'admin/permalink.html',locals())

@login_required
@require_POST
def save_permalink(request):
    linkformat=request.POST.get('permalink_format','archive/%(id)s.html')
    permalink_structure=request.POST.get('permalink_structure','%(year)s/%(month)s/%(day)s/%(postname)s')
    OptionSet.set('permalink_structure', permalink_structure)
    if linkformat== 'custom':
        OptionSet.set('permalink_format', 'custom')
    else:
        OptionSet.set('permalink_format', linkformat)
    messages.add_message(request, messages.INFO, 'save ok!')
    return HttpResponseRedirect('/admin/permalink')

@login_required
@require_POST
def format_permalink(request):
    pass

def backup_db(request):
    defaultdb = DATABASES.get('default')
    engine = defaultdb.get('ENGINE')
    dbname = defaultdb.get('NAME')
    if engine == 'django.db.backends.sqlite3':
        f = open(dbname, "rb")
        data = f.read()
        f.close()
        response = HttpResponse(data,mimetype='application/octet-stream') 
        response['Content-Disposition'] = 'attachment; filename=youflog.sqlite'
        return response

@login_required
def users(request):
    page = request.GET.get('page',1)
    users = User.objects.all()
    return render_response(request,'admin/users.html',locals())

@login_required
def profile(request):
    uid=request.GET.get('uid')
    if uid is None:
        user=request.user
    else:
        user = User.objects.get(id=uid)
    return render_response(request,'admin/profile.html',locals())

@login_required
@require_POST
def saveprofile(request):
    user_id=request.POST.get('user_id',1)
    first_name=request.POST.get('first_name')
    last_name=request.POST.get('last_name')
    nickname=request.POST.get('nickname')
    email=request.POST.get('email')
    url=request.POST.get('url')
    yim=request.POST.get('yim')
    jabber=request.POST.get('jabber')
    description=request.POST.get('description')
    pass1 = request.POST.get('pass1')
    pass2 = request.POST.get('pass2')
    user = User.objects.get(id=user_id)
    try:
        profile=user.get_profile()
    except:
        profile=UserProfile(user=user)
    user.first_name=first_name
    user.last_name=last_name
    user.email=email
    profile.nickname=nickname
    profile.website=url
    profile.yim=yim
    profile.jabber=jabber
    profile.desc=description
    profile.save()
    user.save()
    return render_response(request,'admin/profile.html',{'user':user})