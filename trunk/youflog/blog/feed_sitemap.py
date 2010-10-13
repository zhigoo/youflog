from django.contrib.syndication.views import Feed
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site
from blog.models import Blog,Entry,Comment

g_blog = Blog.get()
domain = Site.objects.get_current().domain

class LatestEntryFeed(Feed):
    title = g_blog.title
    description = g_blog.subtitle
    link = domain
    author="minhao123@gmail.com"

    def items(self):
        return Entry.objects.get_posts().order_by('-date')[:10]

    def item_title(self, item):
        return item.title
    
    def item_pubdate(self, item):
        return item.date

    def item_description(self, item):
        return item.content
    
    def item_link(self,item):
        return domain+'/'+item.link
    
class LatestComments(Feed):
    title = g_blog.title
    description = g_blog.subtitle
    author="minhao123@gmail.com"
    link = domain
    
    def items(self):
        return Comment.objects.order_by('-date')[:10]

    def item_title(self, item):
        return item.author
    
    def item_pubdate(self, item):
        return item.date

    def item_description(self, item):
        return item.content
    
    def item_link(self,item):
        return item.entry().fullurl()+'#comment-'+str(item.id)
    
    
class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    def items(self):
        return Entry.objects.get_posts()

    def lastmod(self, obj):
        return obj.date
    
    def location(self,obj):
        return "/"+obj.link;