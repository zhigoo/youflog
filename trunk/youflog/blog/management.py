#!/usr/bin/env python
# *_* encoding=utf-8*_*
from django.db.models.signals import post_syncdb
from blog import models as youflog
from blog.models import Entry,Link,Category
from blog.comments.models import Comment

def init_data(**kwargs):
    link=Link(text="dengmin's blog",href="http://www.iyouf.info")
    link.save()
    
    default_cate=Category(name=u'未分类',slug='default',desc=u'未分类')
    default_cate.save()
    
    entry=Entry(title='Hello World!',content='<b>Hello World, welcome to use youflog! thank you!</a>',tags='youflog')
    entry.allow_comment=True
    entry.slug='hello-world'
    entry.category=default_cate
    entry.author_id=1
    entry.save(True)
    
    comment=Comment(author='admin',email='admin@iyouf.info',weburl='http://iyouf.info',content=u'测试第一条评论')
    comment.content_object=entry
    comment.save()

post_syncdb.connect(init_data,sender = youflog) 