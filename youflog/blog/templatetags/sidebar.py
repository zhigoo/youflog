#from django.core.cache import cache
from django.template import Library
from django import template
from django.shortcuts import get_object_or_404
from tagging.models import Tag, TaggedItem
from django.db.models import Count
from django.db import connection

from random import sample
from datetime import date, timedelta,datetime
from calendar import LocaleHTMLCalendar
from pingback.models import Pingback
from blog.models import Entry,Comment,Category,Link,Blog
import blog.cache as cache
register = Library()

@register.inclusion_tag('sidebar/recent_posts.html', takes_context = True)
def get_recent_posts(context,number=5):
    posts=Entry.objects.get_posts()
    if number > len(posts):
        number = len(posts)
    return {'recentposts':posts[:number]}

@register.inclusion_tag('sidebar/hot_posts.html', takes_context = True)
def get_popular_posts(context,number=5):
    posts=Entry.objects.get_posts().order_by('-readtimes')
    if number > len(posts):
        number = len(posts)
    return {'hotposts':posts[:number]}

@register.inclusion_tag('sidebar/random_posts.html', takes_context = True)
def get_random_posts(context,number=5):
    entries = Entry.objects.get_posts()
    if number > len(entries):
        number = len(entries)
    return {'randomposts':sample(entries,number)}

@register.inclusion_tag('sidebar/recent_comments.html', takes_context = True)
def get_recent_comment(context,number=10):
    comments=Comment.objects.in_public().exclude(email=Blog.get().email)
    return {'comments':comments[:number]}

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
def get_reader_wall(context,number=10):
    comments=cache.get_cache('sidebar:readerwall')
    if not comments:
        admin_email=Blog.get().email
        sql="select count(email) as count,author,email,weburl from comments_comment where is_public=1 and email !='%s' group by email order by count desc limit %d"%(admin_email,number)
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
def get_calendar(context,year=None, month=None):
    if not year or not month:
        if context.get('year'):
            year = int(context.get('year'))
        if context.get('month'):
            month = int(context.get('month'))
        if not year or not month:
            date_month = datetime.today()
            year, month = date_month.timetuple()[:2]
    try:
        from blog.templatetags.youflogCalendar import YouflogCalendar
    except ImportError:
        return {'calendar': '<p class="notice">Calendar is unavailable for Python<2.5.</p>'}
    
    calendar = YouflogCalendar()
    
    current_month = datetime(year, month, 1)
    dates = list(Entry.objects.dates('date', 'month'))
    
    if not current_month in dates:
        dates.append(current_month)
        dates.sort()
    index = dates.index(current_month)

    previous_month = index > 0 and dates[index - 1] or None
    next_month = index != len(dates) - 1 and dates[index + 1] or None
    
    return {'next_month': next_month,
            'previous_month': previous_month,
            'calendar':calendar.formatmonth(year, month)}

@register.inclusion_tag('sidebar/pingbacks.html', takes_context = True)
def get_recent_pingbacks(context):
    pingbacks = Pingback.objects.all().order_by('-date')[:15]
    return {'pingbacks': pingbacks}