#!/usr/bin/env python
# *_* encoding=utf-8 *_*
from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page
from blog import feed_sitemap,rpc

sitemaps = {
    'posts': feed_sitemap.PostSitemap(),
}

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
    url(r'^themes/(?P<path>.*)$','blog.views.ext_views.theme'),
    url(r'^tinymce/(?P<path>.*)$', 'blog.views.ext_views.tinymce'),
    (r'^media/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
    #sitemap and feed
    url(r'^sitemap.xml$', cache_page(sitemap_views.sitemap, 60 * 60 * 6),{'sitemaps': sitemaps},name='sitemap'),
    url(r'^feed$', cache_page(feed_sitemap.LatestEntryFeed(),60 * 60 * 6),name="rss_feed"),
    url(r'^atom$',cache_page(feed_sitemap.AtomLatestEntries(),60 * 60 * 6),name="rss_atom"),
    url(r'^feed/comments$',cache_page(feed_sitemap.LatestComments(),60 * 60 * 10)),
    url(r'^rpc',rpc.xmlrpc_handler,name='xmlrpc'),
    (r'',include('blog.views.admin_url')),
    (r'',include('blog.views.urls')),
)
