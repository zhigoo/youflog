from django.template import Library

from blog.models import Entry,Comment,Category,Link,Archive
from settings import DATABASE_ENGINE
register = Library()

@register.inclusion_tag('sidebar/recent_posts.html', takes_context = True)
def get_recent_posts(context):
    entrys=Entry.publish.all()[:8]
    return {'recentposts':entrys}

@register.inclusion_tag('sidebar/hot_posts.html', takes_context = True)
def get_hot_posts(context):
    entrys=Entry.publish.order_by('-readtimes')[:8]
    return {'hotposts':entrys}

@register.inclusion_tag('sidebar/random_posts.html', takes_context = True)
def get_random_posts(context):
    if DATABASE_ENGINE == 'sqlite3' :
        entrys = Entry.publish.raw("select * from blog_entry where entrytype='post' order by random() limit 8")
    elif DATABASE_ENGINE == 'mysql':
        entrys = Entry.publish.raw("select * from blog_entry where entrytype='post' order by rand() limit 8")
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

