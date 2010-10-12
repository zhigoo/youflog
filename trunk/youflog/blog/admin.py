from blog.models import Entry,Comment,Link,Category,Blog,Tag
from utils.utils import render_response,paginator
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from datetime import datetime
from theme import ThemeIterator
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
    all = Entry.objects.all()
    all_publish=Entry.publish.all()
    
    if post_status =='all':
        entrys = all
        #entrys = paginator(entrys,10,page)
    else:
        entrys = all_publish
        #entrys = paginator(all_publish,10,page)
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
        if not entry.categories:
            entry.categories='[]'
        return {"id":cat.id,"name":cat.name,"slug":cat.slug,\
                "select":cat.id in eval(entry.categories)}
    
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
        return HttpResponseRedirect('/admin/entrys'); 
@login_required
def submit_post(request):
    published=False
    if request.method == 'POST':
        title = request.POST['title']
        content=request.POST.get('content','')
        excerpt = request.POST.get('excerpt','')
        category = request.POST.getlist("category")
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
        
        categorys = [int(c) for c in category]
        
        ctx={'action':action}
        
        if not (title and content):
            ctx.update({'msg':'Please input title and content.'})
            return render_response(request,"admin/post.html",ctx)
        
        if action== 'add':
            entry = Entry(title=title,content=content,excerpt=excerpt,\
                          categories=categorys,slug=slug.replace(" ","-"))
            entry.settags(tags)
            entry.allow_comment=allow_comment
            entry.entrytype=posttype
            entry.sticky=sticky
            if posttype and posttype =='page':
                menu_order=request.POST.get('order',0)
                entry.menu_order=menu_order
            
            entry.date=datetime.now()
            entry.save(published)
            
            for c in categorys:
                try:
                    cate=Category.objects.get(id=c)
                    cate.count += 1
                    cate.save()
                except:
                    pass
            
            def mapcategoy(cat):
                return  {"id":cat.id,"name":cat.name,\
                         "slug":cat.slug,"select":cat.id in categorys}
            
            ctx.update({'action':'edit','entry':entry,\
                        'entrytype':posttype,'cats':map(mapcategoy,Category.objects.all())})
            
        elif action== 'edit':
            postid = request.POST.get('postid','')
            if postid:
                entry = Entry.objects.get(id=postid)
                entry.settags(tags)
                entry.title=title
                entry.content=content
                entry.excerpt=excerpt
                entry.slug=slug.replace(" ","-")
                entry.entrytype=posttype
                entry.sticky=sticky
                if posttype and posttype =='page':
                    menu_order=request.POST.get('order',0)
                    entry.menu_order=menu_order
                entry.allow_comment=allow_comment
                entry.setCategory(categorys)
                entry.save(published)
                def mapcategoy(cat):
                    return  {"id":cat.id,"name":cat.name,"slug":cat.slug,"select":cat.id in categorys}
    
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
    try:
        page = int(page)
    except:
        page =1
    all=Entry.objects.all().filter(entrytype='page')
    all_entrys = Entry.objects.all().filter(published = True).filter(entrytype='page')
    
    if post_status =='all':
        entrys = all
        entrys = paginator(entrys,10,page)
    else:
        entrys = paginator(all_entrys,10,page)
    
    return render_response(request,"admin/pages.html",\
                           {'entrys':entrys,'publish_count':all_entrys.count(),'all_count':all.count()})

@login_required
def comments(request):
    page=request.GET.get('page',1)
    page = int(page)
    cmts = Comment.objects.all()
    comments = paginator(cmts,10,page)
    return render_response(request,'admin/comments.html',{'comments':comments})

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
def tags(request):
    page=request.GET.get('page',1)
    try:
        page = int(page)
    except:
        page = 1
    
    tags=paginator(Tag.objects.all(),10,page)
    return render_response(request,'admin/tags.html',{'tags':tags})

@login_required
def addTag(request):
    if request.method == 'POST':
        name = request.POST['name'];
        slug=request.POST['slug']
        tag = Tag(name=name,slug=slug)
        tag.save()
        return HttpResponseRedirect('/admin/tags')
    
@login_required
def deleteTag(request):
    if request.method == 'POST':
        action = request.POST.get('action','')
        checks = request.POST.getlist('checks')
        if checks or action=='delete':
            for id in checks:
                if id:
                    t = Tag.objects.get(id=id)
                    t.delete()
        return HttpResponseRedirect('/admin/tags')           

@login_required
def categories(request):
    page=request.GET.get('page',1)
    try:
        page = int(page)
    except:
        page = 1
    categories = paginator(Category.objects.all(),10,page)
    return render_response(request,'admin/categories.html',{'categories':categories})

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
    try:
        id = int(id)
        cat=Category.objects.get(id=id)
    except:
        pass
    categories = paginator(Category.objects.all(),10,1)
    return render_response(request,'admin/category.html',{'cat':cat,'categories':categories})

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
    try:
        page = int(page)
    except:
        page = 1
    links = paginator(Link.objects.all(),10,page)
    return render_response(request,'admin/links.html',{'links':links})

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
    try:
        id = int(id)
        link = Link.objects.get(id=id)
    except:
        pass
    links = paginator(Link.objects.all(),10,1)
    return render_response(request,'admin/link.html',{'link':link,'links':links})

@login_required
def settings(request):
    themeIter=ThemeIterator()
    themes=[t for t in themeIter if t]
    site = Site.objects.get_current()
    return render_response(request,'admin/settings.html',{'themes':themes,'site':site})

@login_required
def save_setting(request):
    if request.method=='POST':
        blogtitle= request.POST.get('blogname','')
        subtitle=request.POST.get('subtitle','')
        blognotice = request.POST.get('blognotice','')
        sitekeywords=request.POST.get('sitekeywords','')
        sitedesc=request.POST.get('sitedesc','')
        theme = request.POST.get('theme','default')
        domain = request.POST.get('domain','')
        if not domain.startswith('http://'):
            domain='http://'+domain
        try:    
            g_blog=Blog.get()
            g_blog.title=blogtitle
            g_blog.subtitle=subtitle
            g_blog.blognotice=blognotice
            g_blog.sitekeywords=sitekeywords
            g_blog.sitedescription=sitedesc
            g_blog.theme_name=theme
            g_blog.save()
            #site info
            site = Site.objects.get_current()
            site.domain=domain
            site.name=blogtitle
            site.save()
            messages.add_message(request,messages.INFO,'setting save ok!')
        except:
            messages.add_message(request,messages.INFO,'setting save failure!')
        return HttpResponseRedirect('/admin/settings')