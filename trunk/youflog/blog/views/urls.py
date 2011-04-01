#!/usr/bin/env python
# *_* encoding=utf-8 *_*
from django.conf.urls.defaults import *
from django.conf import settings
from blog.views import views,wap


urlpatterns = patterns('',
    #wap
    url(r'^wap$',wap.index,name='wap index'), #wap的首页
    url(r'^wap/single/(?P<id>\d+)$',wap.single,name='single post for wap'),
    url(r'^wap/category/(?P<id>\d+)$',wap.category,name='category form wap'),
    
    url(r'^$', views.index, name='blog_index'), #首页
    url(r'^tag/(?P<tag>[-\w]+)',views.tag,name='find post by tag'), #查找所有包含tag的文章
    url(r'^category/(?P<name>[-\w]+)$',views.category,name=''), #文章分类
    url(r'^archive/(?P<id>\d+).html$',views.singlePostByID,name="single_post_by_id"), #文章的详细页面
    url(r'^postcomment$',views.post_comment,name="post_comment"), #发表评论
    url(r'^recentComments',views.recentComments,name="recentComments"),  #通过ajax的方式获取最新的几条评论信息
    url(r'^archives/(?P<year>\d{4})/(?P<month>\d{1,2})$', views.archives,name='entry_by_month'),
    url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})',views.calendar,name='entry_by_calendar'),
    url(r'^image_code',views.safecode,name='captcha_image'),
    url(r'^search/$', views.search,name='search'),
    url(r'^(.*)$', views.singlePost,name='single_post'),
   
)
