from blog.models import Entry,Comment,Link,Category,OptionSet
from utils.utils import render_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from datetime import datetime
from theme import ThemeIterator
from blog.forms import SettingForm
from settings import MEDIA_ROOT
from os.path import isdir, dirname
import logging

#login process
def _login(request,username,password):
    ret=False
    if not username or not password:
        messages.add_message(request, messages.INFO, 'username or password is null')
        return ret
    user=authenticate(username=username,password=password)
    if user:
        if user.is_active:
            auth_login(request,user)
            ret=True
        else:
            messages.add_message(request, messages.INFO, 'user is no active')
    else:
        messages.add_message(request, messages.INFO, 'username or password wrong!')
    return ret

def logout(request):
    auth_logout(request)
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
    return render_response(request,"admin/index.html",{})

@login_required
def admin_posts(request):
    page=request.GET.get('page',1)
    post_status = request.GET.get('post_status')
    try:
        page = int(page)
    except:
        page =1
    all = Entry.objects.all().filter(entrytype='post')
    all_publish=Entry.objects.get_posts()
    
    if post_status =='all':
        entrys = all
    else:
        entrys = all_publish
    publish_count = all_publish.count()
    all_count=all.count()
    
    return render_response(request,"admin/posts.html",{'entrys':entrys,\
                                                       'publish_count':publish_count,
                                                       'all_count':all_count,'page':page})

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
        return HttpResponseRedirect('/admin/entrys')
    
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
    comments = Comment.objects.all().order_by('-date')
    return render_response(request,'admin/comments.html',{'comments':comments,'page':page})

@login_required
def comment_delete(request):
    try:
        allchecks = request.POST.getlist("checks")
        for id in allchecks:
            c = Comment.objects.get(id=id)
            c.delete()
    finally:
        return HttpResponseRedirect('/admin/comments'); 

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
        else:
            id=request.POST.get('id','')
            link=Link.objects.get(id=id)
            link.text=text
            link.href=href
            link.comment=comment
            link.save()
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
        if not domain.startswith('http://'):
            domain='http://'+domain
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
    ctx={'gavatar':gavatar,'comments_per_page':comments_per_page,'comments_notify':bool(comments_notify)}
    return render_response(request,'admin/comment_setting.html',ctx)

@login_required
@require_POST
def save_commentOption(request):
    data=request.POST.copy()
    gavatar=data['gavatar']
    comments_per_page=data['comments_per_page']
    comments_notify=request.POST.get('comments_notify',0)
    OptionSet.set('gavatar', gavatar)
    OptionSet.set('comments_per_page',comments_per_page)
    OptionSet.set('comments_notify',comments_notify)
    return HttpResponseRedirect('/admin/comment_setting')

@login_required
def permalink(request):
    domain = Site.objects.get_current().domain
    permalink_format=OptionSet.get('permalink_format', 'archive/%(id)s.html')
    permalink_structure=OptionSet.get('permalink_structure','%(year)s/%(month)s/%(day)s/%(postname)s.html')
    return render_response(request,'admin/permalink.html',{'domain':domain,\
                            'permalink_format':permalink_format,'permalink_structure':permalink_structure})

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
    
    