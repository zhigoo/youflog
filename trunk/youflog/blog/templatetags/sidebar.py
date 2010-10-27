from django.template import Library
from django.shortcuts import get_object_or_404
from blog.models import Entry,Comment,Category,Link,Archive,Blog
from settings import DATABASE_ENGINE
from tagging.models import Tag, TaggedItem
from django.db.models import Count
register = Library()

@register.inclusion_tag('sidebar/recent_posts.html', takes_context = True)
def get_recent_posts(context):
    entrys=Entry.objects.get_posts()[:8]
    return {'recentposts':entrys}

@register.inclusion_tag('sidebar/hot_posts.html', takes_context = True)
def get_popular_posts(context):
    entrys=Entry.objects.get_posts().order_by('-readtimes')[:8]
    return {'hotposts':entrys}

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
    categories=Category.objects.all()
    return {'categories':categories}

@register.inclusion_tag('sidebar/links.html', takes_context = True)
def get_links(context):
    links=Link.objects.all()[:20]
    return {'links':links}

@register.inclusion_tag('sidebar/archives.html', takes_context = True)
def get_archives(context):
    archives=Archive.objects.all()[:12]
    return {'archives':archives}

@register.inclusion_tag('sidebar/tags.html', takes_context = True)
def get_tag_cloud(context):
    #tags=Tag.objects.all()
    tags=TaggedItem.objects.values('tag').annotate(count=Count('tag'))
    result=[]
    for tag in tags:
        t=get_object_or_404(Tag,id=tag['tag'])
        result.append({'count':tag['count'],'tag':t})
    return {'tags':result}

@register.inclusion_tag('readwall.html', takes_context = True)
def get_reader_wall(context):
    admin_email=Blog.get().email
    sql="select count(email) as count,author,email,weburl from comments_comment where email !='%s' group by email order by count desc limit 12"%(admin_email)
    from django.db import connection
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
        
    return {'comments':comments}
