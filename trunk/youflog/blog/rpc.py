#! /usr/bin/env python
#coding=utf-8
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from xmlrpclib import Fault
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from blog.models import Blog,Entry,Category
from django.http import HttpResponse
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    from django.contrib.csrf.middleware import csrf_exempt
import logging

def post_struct(entry):
    if not entry:
        raise Fault(404, "Post does not exist")
    struct = {
        'postid': entry.id,
        'title': unicode(entry.title),
        'link': entry.fullurl,
        'permaLink': entry.fullurl,
        'description': unicode(entry.content),
        'categories': entry.category,
        'mt_keywords':entry.tags,
        'userid': '1',
        'mt_allow_comments': entry.allow_comment and 1 or 0,
        'mt_allow_pings': 1,
        'custom_fields':[],
        'sticky':entry.sticky,
        'wp_author_display_name': entry.author.username,
         'wp_author_id': entry.author.id,
         'wp_slug':entry.slug,
         'wp_author': 'admin',
        }
    return struct

def _checkUser(username,password):
    try:
        user = User.objects.get(username__exact=username)
    except User.DoesNotExist:
        raise ValueError("Authentication Failure")
    if not user.check_password(password):
        raise ValueError("Authentication Failure")
    if not user.is_superuser:
        raise ValueError("Authorization Failure")

def blogger_getUsersBlogs(appkey, username, password):
    _checkUser(username,password)
    blog=Blog.get()
    url='http://%s'%(Site.objects.get_current().domain)
    return [{'url' : url, 'blogid' : '1','isAdmin':True, 'blogName' : blog.title,'xmlrpc':url+"/rpc"}]

def blogger_deletePost(appkey,postid,username,password,publish):
    try:
        post = Entry.objects.get(id=int(postid))
        post.delete()
        return True
    except:
        return False

def blogger_getRecentPosts(appkey,blogid,username,password,num=20):
    posts=Entry.objects.get_posts()
    return [post_struct(post) for post in posts[:num]]

def metaWeblog_getPost(postid, username, password):
    post = Entry.objects.get(int(postid))
    return post_struct(post)

def metaWeblog_newPost(blogid, username, password, struct, publish):
    user = User.objects.get(username__exact=username)
    if struct.has_key('title') and struct.has_key('description'):
        post = Entry(title=struct['title'],content = struct['description'])
        post.author=user
        if struct.has_key('categories'):
            catename = struct['categories'][0]
            cate=Category.objects.get(name__exact=catename)
            post.category=cate
        else:
            post.category_id=1
        if struct.has_key('mt_keywords'):
            post.tags=struct['mt_keywords']
        if struct.has_key('wp_slug'):
            post.slug=struct['wp_slug']
        post.save(True)
    return ""

def metaWeblog_editPost(postid, username, password, struct, publish):
    return True

def wp_getPages(blogid,num=20):
    pages = Entry.objects.get_pages()
    return [post_struct(page) for page in pages[:num]] 

def wp_getPageList(blogid,num=20):
    return []

def mt_getCategoryList(blogid,username,password):
    categories =Category.objects.all()
    cates=[]
    for cate in categories:
        cates.append({ 'categoryId' : cate.id,'categoryName':cate.name})
    return cates

def metaWeblog_getCategories(blogid,username,password):
    categories =Category.objects.all()
    logging.info(categories)
    cates=[]
    for cate in categories:
        cates.append({  'categoryDescription':cate.desc,
                        'categoryId' : cate.id,
                        'parentId':'0',
                        'description':cate.desc,
                        'categoryName':cate.name,
                        'htmlUrl':'',
                        'rssUrl':''
                        })
    return cates

def mt_setPostCategories(postid,username,password,cates):
    return 0
 
def mt_publishPost(postid,username,password):
    try:
        post = Entry.objects.get(int(postid))
        post.save(True)
        return post.id
    except:
        return 0

from pingback import handler_pingback
def ping(source,target):
    return handler_pingback(source,target)
    
class PlogXMLRPCDispatcher(SimpleXMLRPCDispatcher):
    def __init__(self, funcs):
        SimpleXMLRPCDispatcher.__init__(self, True, 'utf-8')
        self.funcs = funcs

dispatcher = PlogXMLRPCDispatcher({
        'blogger.getUsersBlogs' : blogger_getUsersBlogs,
        'blogger.deletePost' : blogger_deletePost,
        'metaWeblog.newPost' : metaWeblog_newPost,
        'metaWeblog.editPost' : metaWeblog_editPost,
        'metaWeblog.getCategories' : metaWeblog_getCategories,
        'metaWeblog.getPost' : metaWeblog_getPost,#
        'metaWeblog.getRecentPosts' : blogger_getRecentPosts,
        'mt.getCategoryList':mt_getCategoryList,
        'wp.getPages':wp_getPages,
        'wp.getPageList':wp_getPageList,
        'mt.setPostCategories':mt_setPostCategories,
        'mt.publishPost':mt_publishPost,
        'pingback.ping':ping
        })

@csrf_exempt
def xmlrpc_handler(request):
    if request.method == 'POST':
        return HttpResponse(dispatcher._marshaled_dispatch(request.raw_post_data))
    elif request.method == 'GET':
        response = '\n'.join(dispatcher.system_listMethods())
        return HttpResponse(response, mimetype='text/plain')