#!/usr/bin/env python
# *_* encoding=utf-8 *_*
from django.dispatch import Signal
from django.contrib.sites.models import Site
from threading import Thread

from blog.akismet import Akismet
from blog.akismet import AkismetError

from blog.models import Blog,OptionSet
from utils.utils import sendmail

comment_was_submit=Signal(providing_args=['comment'])

comment_was_posted = Signal(providing_args=["comment", "request"])

def validate_comment(sender, comment, request, *args, **kwargs):
    akismet_enable=OptionSet.get('akismet_enable', 0)
    domain="http://%s"%(Site.objects.get_current().domain)
    if int(akismet_enable) == 0:
        return
    
    akismet_key=OptionSet.get('akismet_key', '')
    ak = Akismet(
            #key = 'cda0f27f8e2f',
            key=akismet_key,
            blog_url=domain
        )
    try:
        if ak.verify_key():
            data = {
                'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referrer': request.META.get('HTTP_REFERER', ''),
                'comment_type': 'comment',
                'comment_author': comment.author.encode('utf-8'),
            }
            if ak.comment_check(comment.content.encode('utf-8'), data=data, build_data=True):
                comment.is_public = False
                comment.save()
                
                ak.submit_spam(comment.content.encode('utf-8'), data=data, build_data=True)
                
    except AkismetError:
        pass

def on_comment_was_posted(sender,comment,request,*args,**kwargs):
    th = Thread(target=validate_comment,args=(sender,comment,request))
    th.start()

def on_comment_was_submit(sender,comment,*args,**kwargs):
    blog=Blog.get()
    domain="http://%s"%(Site.objects.get_current().domain)
    if comment.parent_id != '0':
        old_c=comment.parent
        emailtitle=u'您在 '+blog.title+u' 上的评论有了新的回复'
        if old_c.mail_notify:
            sendmail('email/reply_comment.txt',{'old':old_c,"comment":comment,
                                'blog':blog,'domain':domain},
                      emailtitle,old_c.email)
    else:
        comments_notify=OptionSet.get('comments_notify',1)
        if int(comments_notify) == 1 and comment.is_public==True:
            emailtitle=u'文章'+comment.object.title+u'有了新的评论'
            sendmail('email/new_comment.txt',{'comment':comment,'domain':domain},emailtitle,blog.email)

comment_was_posted.connect(on_comment_was_posted)
comment_was_submit.connect(on_comment_was_submit)