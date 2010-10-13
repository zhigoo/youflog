#!/usr/bin/env python
# *_* encoding=utf-8*_*
from django.db.models.signals import post_syncdb
from blog import models as youflog
from blog.models import Entry,Link,Category

def init_data(**kwargs):
    link=Link(text="dengmin's blog",href="http://www.iyouf.info")
    link.save()
    
    default_cate=Category(name=u'未分类',slug='default')
    default_cate.save()
    
    entry=Entry(title='Hello World!',content='Hello World, welcome to use youflog! thank you!',tags='youflog')
    entry.excerpt='Hello World!'
    entry.allow_comment=True
    entry.category=default_cate
    entry.save(True)

post_syncdb.connect(init_data,sender = youflog) 