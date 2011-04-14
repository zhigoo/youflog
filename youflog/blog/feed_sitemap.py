from django.contrib.syndication.views import Feed
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site
from django.utils.feedgenerator import Atom1Feed
from blog.models import Blog,Entry,Comment

domain = Site.objects.get_current().domain

class LatestEntryFeed(Feed):
    title = Blog.get().title
    description = Blog.get().subtitle
    link = domain
    
    description_template = 'feed/post_content.html'
    
    def items(self):
        return Entry.objects.get_posts().order_by('-date')[:10]

    def item_title(self, item):
        return item.title
    
    def item_pubdate(self, item):
        return item.date
    
    def item_link(self,item):
        return "/%s" %(item.get_absolute_url())
    
class LatestComments(Feed):
    title = Blog.get().title
    description = Blog.get().subtitle
    link = domain
    
    def items(self):
        return Comment.objects.in_public()[:10]

    def item_title(self, item):
        return item.author
    
    def item_pubdate(self, item):
        return item.date

    def item_description(self, item):
        return item.content
    
    def item_link(self,item):
        return item.get_absolute_url()
    
class AtomLatestEntries(LatestEntryFeed):
    feed_type = Atom1Feed
    subtitle = LatestEntryFeed.description

class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    def items(self):
        return Entry.objects.get_posts()

    def lastmod(self, item):
        return item.date
    
    def location(self,item):
        return '/%s'%(item.get_absolute_url())