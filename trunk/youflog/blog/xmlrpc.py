#!/usr/bin/env python
# *_* encoding=utf-8*_*

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.sites.models import Site
from django.http import HttpResponse
from blog.models import Blog
import logging
__all__ = ['dispatcher']

def checkAuth(username,password):
    logging.info(username)
    result=False
    if not username or not password:
        raise Exception, 'access denied'

    user=authenticate(username=username,password=password)
    
    if user and user.is_active:
        auth_login(username,password)
        result=True
    return result
     
def rpc(request):
    
    if request.method == 'GET':
        return HttpResponse('user post method')
    
    logging.info('............xmlrpc.........')
    response=dispatcher._marshaled_dispatch(request.raw_post_data)
    logging.info(response)
    return response
       

def blogger_getUsersBlogs(discard, username, password):
    logging.info(username)
    if not checkAuth(username,password):
        raise Exception, 'access denied'
    return {'url':Site.objects.get_current().domain,'blogid':'youflog','blogName':Blog.get().title}

class PlogXMLRPCDispatcher(SimpleXMLRPCDispatcher):
    def __init__(self, funcs):
        SimpleXMLRPCDispatcher.__init__(self, True, 'utf-8')
        self.funcs = funcs
        
dispatcher = PlogXMLRPCDispatcher({
 'blogger.getUsersBlogs':blogger_getUsersBlogs,
})