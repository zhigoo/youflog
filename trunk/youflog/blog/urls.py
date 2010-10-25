#!/usr/bin/env python
# *_* encoding=utf-8 *_*
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from blog import views,admin,feed_sitemap,wap
from blog import xmlrpc

sitemaps = {
    'posts': feed_sitemap.PostSitemap(),
}

urlpatterns = patterns('',
    
    url(r'^admin$',admin.index,name="admin_index"), # 后台管理页面
    #post
    url(r'^admin/allposts',admin.all_posts,name='all posts'),
    url(r'^admin/pubposts',admin.all_pub_posts,name='all publish posts'),
    url(r'^admin/unpubposts',admin.unpub_posts,name='all unpublish posts'),
    url(r'^admin/post$',admin.admin_addpost,name="add post"), #跳转到文章添加页面
    url(r'^admin/submit_post',admin.submit_post,name='submit_post_page'), #提交文章 或者页面
    url(r'^admin/editpost/(?P<id>\d+)',admin.edit_post,name="editor post"),#文章火着页面的编辑
    url(r'^admin/post_delete$',admin.post_delete,name="delete post"), #删除文章或者页面
    url(r'admin/page$',admin.addPage,name='add page '), #跳转到页面添加
    url(r'admin/pages$',admin.pages,name='show all pages'),#分页显示所有的页面
    #comment
    url(r'^admin/comments',admin.comments,name="show all comments"), #分页显示所有的评论
    url(r'^admin/spam_comment',admin.spam_comment,name='spam comment'),
    url(r'^admin/comment_delete',admin.comment_delete,name="delete comment"), #批量删除评论信息
    
    #category
    url(r'^admin/categories',admin.categories,name='show all categories'),
    url(r'^admin/category/add$',admin.addCategory,name='add category'),
    url(r'^admin/editcategory/(?P<id>\d+)$',admin.editCategory,name='editor category'),
    url(r'^admin/category/delete$',admin.deleteCategory,name='delete category'),
    
    #links
    url(r'^admin/links',admin.links,name='show all links'),
    url(r'^admin/link/add$',admin.addLink,name='add link'),
    url(r'^admin/editlink/(?P<id>\d+)$',admin.editlink,name='editor link'), #编辑连接
    url(r'^admin/link/delete$',admin.deleteLink,name='delete links'), #删除连接
    #settings
    url(r'^admin/settings$',admin.settings,name='settings'), #基本设置页面
    url(r'^admin/settings/save$',admin.save_setting,name='save settings'), #保持设置
    url(r'^admin/comment_setting$',admin.setting_comment),
    url(r'^admin/save_commentOption$',admin.save_commentOption),
    url(r'^admin/permalink$',admin.permalink),
    url(r'^admin/save_permalink',admin.save_permalink),
    url(r'^admin/backup_db$',admin.backup_db),
    
    #media
    url(r'^admin/media$',admin.media,name='show all media'),
    url(r'^admin/upload_media$',admin.upload_media),
    
    #sitemap
    url(r'^sitemap.xml$', cache_page(sitemap_views.sitemap, 60 * 60 * 6),{'sitemaps': sitemaps}),#sitemap
    #feed
    url(r'^feed$', feed_sitemap.LatestEntryFeed()),
    url(r'^feed/comments$',feed_sitemap.LatestComments()),
    #login logout
    url(r'^accounts/login', admin.login,name="login"), #登录
    url(r'^accounts/logout$',admin.logout,name='logout'), #退出
    
    #wap
    url(r'^wap$',wap.index,name='wap index'), #wap的首页
    url(r'^wap/single/(?P<id>\d+)$',wap.single,name='single post for wap'),
    url(r'^wap/category/(?P<id>\d+)$',wap.category,name='category form wap'),
    
    url(r'^$', views.index, name='blog_index'), #首页
    url(r'^tag/(?P<tag>[-\w]+)',views.tag,name='find post by tag'), #查找所有包含tag的文章
    url(r'^category/(?P<name>[-\w]+)$',views.category,name=''), #文章分类
    url(r'^archive/(?P<id>\d+).html$',views.singlePostByID,name="single post"), #文章的详细页面
    url(r'^postcomment$',views.post_comment,name="post_comment"), #发表评论
    url(r'^recentComments',views.recentComments,name="recentComments"),  #通过ajax的方式获取最新的几条评论信息
    url(r'^archives/(?P<year>\d{4})/(?P<month>\d{1,2})$', views.archives),
    url(r'^xmlrpc$',xmlrpc.rpc),
    (r'^(.*)$', views.singlePost),
    
)
