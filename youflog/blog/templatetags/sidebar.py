#from django.core.cache import cache
from django.template import Library
from django import template
from django.shortcuts import get_object_or_404
from tagging.models import Tag, TaggedItem
from django.db.models import Count
from django.db import connection

from datetime import date, timedelta,datetime
from calendar import LocaleHTMLCalendar
from pingback.models import Pingback
from blog.models import Entry,Comment,Category,Link,Blog
import blog.cache as cache
from settings import DATABASE_ENGINE
register = Library()

@register.inclusion_tag('sidebar/recent_posts.html', takes_context = True)
def get_recent_posts(context):
    posts=Entry.objects.get_posts()[:8]
    return {'recentposts':posts}

@register.inclusion_tag('sidebar/hot_posts.html', takes_context = True)
def get_popular_posts(context):
    posts=Entry.objects.get_posts().order_by('-readtimes')[:8]
    return {'hotposts':posts}

@register.inclusion_tag('sidebar/random_posts.html', takes_context = True)
def get_random_posts(context):
    if DATABASE_ENGINE == 'sqlite3' :
        entrys = Entry.objects.raw("select * from blog_entry where published=1 and entrytype='post' order by random() limit 8")
    elif DATABASE_ENGINE == 'mysql':
        entrys = Entry.objects.raw("select * from blog_entry where published=1 and entrytype='post' order by rand() limit 8")
    return {'randomposts':entrys}

@register.inclusion_tag('sidebar/recent_comments.html', takes_context = True)
def get_recent_comment(context):
    comments=Comment.objects.in_public().exclude(email=Blog.get().email)[:10]
    return {'comments':comments}

@register.inclusion_tag('sidebar/categories.html', takes_context = True)
def get_categories(context):
    categories=cache.get_cache('sidebar:categories')
    if not categories:
        categories=Category.objects.all()
        cache.set_cache('sidebar:categories',categories,60 * 60)
    return {'categories':categories}

@register.inclusion_tag('sidebar/links.html', takes_context = True)
def get_links(context):
    links=cache.get_cache('sidebar:links')
    if not links:
        links=Link.objects.all()
        cache.set_cache('sidebar:links',links,60*60)
    return {'links':links}

@register.inclusion_tag('sidebar/archives.html', takes_context = True)
def get_archives(context):
    archives=cache.get_cache('sidebar:archives')
    if not archives:
        archives = Entry.objects.dates('date','month','DESC')
        cache.set_cache('sidebar:archives',archives,60*20)
    return {'archives':archives}

@register.inclusion_tag('sidebar/tags.html', takes_context = True)
def get_tag_cloud(context):
    result=cache.get_cache('sidebar:tagcloud')
    if not result:
        result=[]
        tags=TaggedItem.objects.values('tag').annotate(count=Count('tag'))
        for tag in tags:
            t=get_object_or_404(Tag,id=tag['tag'])
            result.append({'count':tag['count'],'tag':t})
        cache.set_cache('sidebar:tagcloud',result,60*10)
    return {'tags':result}

@register.inclusion_tag('readwall.html', takes_context = True)
def get_reader_wall(context):
    comments=cache.get_cache('sidebar:readerwall')
    if not comments:
        admin_email=Blog.get().email
        sql="select count(email) as count,author,email,weburl from comments_comment where is_public=1 and email !='%s' group by email order by count desc limit 12"%(admin_email)
        cursor = connection.cursor()
        cursor.execute(sql)
        rows=cursor.fetchall()
        comments=[]
        
        for row in rows:
            count=row[0]
            author=row[1]
            email=row[2]
            weburl=row[3]
            comment={'author':author,'weburl':weburl,'count':str(count),'email':email}
            comments.append(comment)
        cache.set_cache('sidebar:readerwall',comments,30)
    return {'comments':comments}

@register.inclusion_tag('menus.html', takes_context = True)
def get_menus(context):
    pages=Entry.objects.get_pages()
    current = 'current' in context and context['current']
    return {'menus':pages,'current': current}

@register.inclusion_tag('sidebar/calendar.html',takes_context=True)
def get_calendar(context,year=date.today().year, month=date.today().month):
    try:
        from blog.templatetags.youflogCalendar import YouflogCalendar
    except ImportError:
        return {'calendar': '<p class="notice">Calendar is unavailable for Python<2.5.</p>'}
    
    calendar = YouflogCalendar()
    return {'calendar':calendar.formatmonth(year, month)}

@register.inclusion_tag('sidebar/pingbacks.html', takes_context = True)
def get_recent_pingbacks(context):
    pingbacks = Pingback.objects.all().order_by('-date')[:15]
    return {'pingbacks': pingbacks}