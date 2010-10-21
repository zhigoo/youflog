from django.dispatch import Signal
from django.contrib.sites.models import Site
from threading import Thread

from blog.akismet import Akismet
from blog.akismet import AkismetError

from blog.models import OptionSet

comment_was_submit=Signal(providing_args=['comment'])

comment_was_posted = Signal(providing_args=["comment", "request"])

def validate_comment(sender, comment, request, *args, **kwargs):
    akismet_enable=OptionSet.get('akismet_enable', 0)
    
    if int(akismet_enable) == 0:
        return
    
    akismet_key=OptionSet.get('akismet_key', '')
    ak = Akismet(
            #key = 'cda0f27f8e2f',
            key=akismet_key,
            blog_url=Site.objects.get_current().domain
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

comment_was_posted.connect(on_comment_was_posted)