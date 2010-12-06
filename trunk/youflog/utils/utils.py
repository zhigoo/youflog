#*_* coding=utf-8 *_*
import urllib
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from threading import Thread

from django.template.loader import get_template
from django.template.context import Context
from blog.models import Blog


def render_response(request, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(request)
    return render_to_response(*args, **kwargs)

def render(request,theme_file,template_ctx):
    blog=Blog.get()
    theme = blog.theme_name
    tpl_file='themes/'+theme+'/'+theme_file
    return render_response(request,tpl_file,template_ctx)


def loadTempalte(theme_file):
    blog=Blog.get()
    theme = blog.theme_name
    tpl_file='themes/'+theme+'/'+theme_file
    return get_template(tpl_file)
    

def urldecode(value):
    return  urllib.unquote(urllib.unquote(value)).decode('utf8')

def urlencode(value):
    return urllib.quote(value.encode('utf8'))

#object_list  对象列表
#per_page  每页多少条
#pagenum 当前第几页
def paginator(object_list,per_page,pagenum):
    paginator = Paginator(object_list, per_page)
    return paginator.page(pagenum)


def sendmail(template,template_data,subject,reveivers):
    template = get_template(template)
    msg = template.render(Context(template_data))
   
    th = Thread(target=send_html_email,args=(subject,msg,reveivers))
    th.start()

#发送html格式的邮件
def send_html_email(subject,msg,reveivers,**kwargs):
    sender=Blog.get().email
    mailmsg = EmailMessage(subject,msg,sender, [reveivers])
    mailmsg.content_subtype = 'html'
    mailmsg.send(fail_silently=True)