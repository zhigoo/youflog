#!/usr/bin/env python
# *_* encoding=utf-8 *_*
from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
    url(r'^themes/(?P<path>.*)$','blog.ext_views.theme'),
    url(r'^tinymce/(?P<path>.*)$', 'blog.ext_views.tinymce'),
    (r'',include('blog.urls')),
    
)
