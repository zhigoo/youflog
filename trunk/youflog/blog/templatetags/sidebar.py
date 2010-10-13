from django.template import Library
import hashlib,urllib
from blog.models import Entry,Comment,Category,Link,Archive
from settings import DATABASE_ENGINE
from tagging.models import Tag
register = Library()

@register.inclusion_tag('sidebar/recent_posts.html', takes_context = True)
def get_recent_posts(context):
    entrys=Entry.objects.get_posts()[:8]
    return {'recentposts':entrys}

@register.inclusion_tag('sidebar/hot_posts.html', takes_context = True)
def get_hot_posts(context):
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
    comments=Comment.objects.all().order_by('-date')[:10]
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
    tags=Tag.objects.all()
    
    return {'tags':tags}

@register.inclusion_tag('readwall.html', takes_context = True)
def get_reader_wall(context):
    sql="select count(email) as count,author,email,weburl  from comments_comment group by author order by count desc limit 12"
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(sql)
    rows=cursor.fetchall()
    comments=[]
    
    for row in rows:
        imgurl = "http://www.gravatar.com/avatar/"
        imgurl +=hashlib.md5(row[2].lower()).hexdigest()+"?"+ urllib.urlencode({
                'd':'identicon', 's':str(50),'r':'G'})
        count=row[0]
        author=row[1]
        weburl=row[3]
        comment={'author':author,'gravatar_url':imgurl,'weburl':weburl,'count':str(count)}
        comments.append(comment)
    
    return {'comments':comments}
