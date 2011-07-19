#!/usr/bin/env python
# *_* encoding=utf-8*_*
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
    posts = cache.get_cache('recent_posts')
    if not posts:
        posts=Entry.objects.get_posts()
        cache.set_cache('recent_posts',posts)
        if number > len(posts):
            number = len(posts)
    return {'recentposts':posts[:number]}

@register.inclusion_tag('sidebar/popular_posts.html', takes_context = True)
def get_popular_posts(context,number=5):
    posts = cache.get_cache('popular_posts')
    if not posts:
        posts=Entry.objects.get_posts().order_by('-readtimes')
        cache.set_cache('popular_posts',posts)
        if number > len(posts):
            number = len(posts)
    return {'hotposts':posts[:number]}

@register.inclusion_tag('sidebar/random_posts.html', takes_context = True)
def get_random_posts(context,number=5):
    posts = Entry.objects.get_posts()
    if number > len(posts):
        number = len(posts)
    return {'randomposts':sample(posts,number)}

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
    pingbacks = cache.get_cache('recent_pingback')
    if not pingbacks:
        pingbacks = Pingback.objects.all().order_by('-date')[:15]
        cache.set_cache('recent_pingback',pingbacks)
    return {'pingbacks': pingbacks}

@register.inclusion_tag('sidebar/meta.html', takes_context = True)
def get_meta_widget(context):
    return {'user':context.get('request').user}

class CategoryNode(template.Node):
    
    def __init__(self, ctype=None,object_expr=None):
        self.object_expr = object_expr
    
    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))
    def render(self, context):
        obj = self.object_expr.resolve(context)
        def append_category_start(item,html):
            t = template.Template('<li><a href="{{cate.get_absolute_url}}">{{cate.name}}</a>({{cate.count}})')
            content = t.render(template.Context({'cate':item}))
            html.append(content)
        
        def append_category_end(html):
            html.append('</li>\n')

        def append_child_start(html):
            html.append('<ul class="children">\n')

        def append_child_end(html):
            html.append('</ul>\n')

        def create_category_html(root, list, html):
            append_category_start(root, html)
            list.remove(root)
            if root.has_children():
                children = root.get_children()
                for child in children:
                    append_child_start(html)
                    create_category_html(child, list, html)

            append_category_end(html)
            if root.has_parent():
                append_child_end(html)

            if len(list) > 0 and not root.has_parent():
                create_category_html(list[0], list, html)

        html = []
        if obj:
            sorted = []
            first = obj[0]
            html.append('<ul class="cat-item">\n')
            create_category_html(first, list(obj), html)
            html.append('</ul>')

        return ''.join(html)
    
@register.tag
def get_category_list(parser, token):
    return CategoryNode.handle_token(parser, token)