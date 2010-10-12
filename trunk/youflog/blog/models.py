#!/usr/bin/env python
# *_* encoding=utf-8*_*
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site

from datetime import datetime
from blog.comments.models import Comment

from blog.managers import EntryPublishManager


class Archive(models.Model):
    monthyear = models.CharField(max_length=20)
    year = models.CharField(max_length=8)
    month = models.CharField(max_length=4)
    entrycount = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.monthyear

class Tag(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField()
    count=models.IntegerField(default=1)

    
    def update(self,type):
        if type and type == 'increment':
            self.count += 1
            self.save()
        else:
            self.delete()
    
    def delete(self):
        if self.count <= 1:
            super(Tag,self).delete()
        else:
            self.count -= 1
            self.save()
    
    def __unicode__(self):
        return '%s %s '%(self.name,self.count)
    
class Blog(models.Model):
    author = models.CharField('admin',default='admin',max_length=20)
    description = models.TextField();
    baseurl = models.URLField();
    domain = models.URLField()
    title = models.CharField(max_length=100,default='youflog')
    subtitle = models.CharField(max_length=100,default='a simple blog named youflog')
    entrycount = models.IntegerField(default=0);
    posts_per_page = models.IntegerField(default=8)
    comments_per_page = models.IntegerField(default=10)
    feedurl = models.URLField()
    theme_name = models.CharField(default='default',max_length=30)
    link_format=models.CharField(max_length=100,default='%(year)s/%(month)s/%(day)s/%(postname)s.html')
    blognotice = models.TextField("notice")
    sitekeywords=models.CharField(max_length=100,default='youflog')
    sitedescription=models.CharField(max_length=200,default='simple blog system')
    
    @staticmethod
    def get():
        blog=None
        try:
            blog = Blog.objects.all()[0]
        except:
            pass
        if not blog:
            blog= Blog(title='youflog')
            blog.save()
        return blog
    
    def __unicode__(self):
        return self.title

class Category(models.Model):
    name=models.CharField(max_length=50)
    slug=models.SlugField()
    desc=models.TextField(null=True, blank=True)
    count=models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name

 
class Entry(models.Model):
    ENTRY_TYPE_CHOICES=(('page','page'),('post','post'))
    author=models.CharField(max_length=40)
    title = models.CharField(max_length=40)
    content = models.TextField()
    excerpt = models.TextField(null=True, blank=True)
    published = models.BooleanField(default=False)
    entrytype = models.CharField(max_length=10,choices=ENTRY_TYPE_CHOICES,default='post')
    readtimes = models.IntegerField(default=0)
    tags = models.CharField(max_length=200,null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    categories= models.CommaSeparatedIntegerField(max_length=50)
    slug = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    monthyear = models.CharField(max_length=20, null=True, blank=True)
    #允许评论
    allow_comment = models.BooleanField()
    #allow_pingback = models.BooleanField()
    commentcount = models.IntegerField(default=0)
    
    menu_order=models.IntegerField(default=0)
    #文章置顶
    sticky=models.BooleanField(default=False)
    
    comments =  generic.GenericRelation(Comment, object_id_field='object_pk',
                                        content_type_field='content_type')
    
    objects = models.Manager()
    
    publish=EntryPublishManager()
    
    
    postname=''
    class Meta:
        ordering=('-id','-date',)
    
    def get_absolute_url(self):
        return ""
    
    def shortcontent(self,len=200):
        return self.content[:len]
    
    def __unicode__(self):
        return self.title
    
    #next post
    def next(self):
        next = Entry.publish.raw("select * from blog_entry where entrytype='post' and id > %s limit 1"%(str(self.id)))
        return next[:1]

    #prev post
    def prev(self):
        prev = Entry.publish.raw("select * from blog_entry where entrytype='post' and id < %s order by date desc limit 1"%(str(self.id)))
        return prev[:1]

    def tagstr(self):
        if self.tags:
            return self.tags.split(',')
        else:
            return []
    
    def cates(self):
        categories=eval(self.categories)
        cate=[]
        for id in categories:
            c = Category.objects.get(id=id)
            cate.append(c)
        return cate
    
    def fullurl(self):
        '''返回文章的绝对路径'''
        url=Site.objects.get_current().domain+"/"+self.link
        return  url
    
    def updateReadtimes (self):
        self.readtimes += 1
        super(Entry,self).save()
    
    def updateCommentCount (self,count):
        self.commentcount += count
        super(Entry,self).save()

    def save(self,pub):
        self.date=datetime.now()
        g_blog = Blog.get()
        old_pub=self.published
        if pub: 
            vals={'year':self.date.year,'month':str(self.date.month).zfill(2),\
                  'day':self.date.day,'postname':self.slug}
            
            if self.entrytype == 'post':
                if g_blog.link_format and self.slug:
                    self.link=g_blog.link_format.strip()%vals
                else:
                    if self.id:
                        vals.update({'post_id':self.id})
                        self.link='post/%(post_id)s.html'%vals
                    else:
                        super(Entry,self).save()
                        vals.update({'post_id':self.id})
                        self.link='post/%(post_id)s.html'%vals
            else:
                if self.slug:
                    self.link='page/'+self.slug
                else:
                    super(Entry,self).save()
                    self.link='page/%s'%(str(self.id))
        
        self.published=pub
        super(Entry,self).save()
        #以前发布过了且点击了取消发布 archive数量减1
        if old_pub and not pub: 
            self.update_archive(-1)
        #以前没有发布且点击了发布按钮 archive数量加1
        if not old_pub and pub:
            self.update_archive(1)
        
    def delete(self):
        '''删除文章'''
        if self.published:
            #更新archinve
            self.update_archive(-1)
        #删除所有的评论
        self.delete_comments()
        super(Entry,self).delete()
    
    def delete_comments(self):
        '''删除该文章下的所有评论'''
        cmts = self.comments()
        for c in cmts:
            c.forceDelete()
        self.commentcount=0

    def update_archive(self,cnt=1):
        my = self.date.strftime('%B %Y')
        sy = self.date.strftime('%Y')
        sm = self.date.strftime('%m')

        if self.entrytype == 'post':
            try:
                archive = Archive.objects.get(monthyear=my)
                if not archive:
                    archive = Archive(monthyear=my,year=sy,month=sm,entrycount=1)
                    self.monthyear = my
                    archive.save()
                else:
                    archive.entrycount += cnt
                    if archive.entrycount <= 0:
                        archive.entrycount = 0
                    archive.save()
            except:
                archive = Archive(monthyear=my,year=sy,month=sm,entrycount=1)
                archive.save()
    
    
    def setCategory(self,categorys):
        exist_category = eval(self.categories)
        addcategories,removecategories=list(set(categorys)-set(exist_category)),\
            list(set(exist_category)-set(categorys))

        if addcategories:
            for cid in addcategories:
                cate = Category.objects.get(id=int(cid))
                cate.count += 1
                cate.save()
        if removecategories:
            for cid in removecategories:
                cate = Category.objects.get(id=int(cid))
                cate.count -= 1
                cate.save()
        self.categories = categorys
        

    def settags(self,values):
        if values:
            tags=values.split(',')
            tags=[n for n in tags if n]
        else:
            tags=[]
        if self.tags:
            exist_tags = self.tags.split(',')
            exist_tags = [n for n in exist_tags if n]
        else:
            exist_tags=[]
        addTags,removeTags=list(set(tags)-set(exist_tags)),\
            list(set(exist_tags)-set(tags))
        
        if addTags:
            for t in addTags:
                try:
                    tag= Tag.objects.get(name=t)
                    tag.name=t
                    tag.slug=t
                    tag.update('increment')
                except:
                    tag=Tag(name=t,slug=t)
                    tag.save()
        if removeTags:
            for t in removeTags:
                try:
                    tag = Tag.objects.get(name=t)
                    tag.update('increment')
                except:pass
        self.tags=values
    
class Link(models.Model):
    href=models.URLField()
    text=models.CharField("text",max_length=20)
    comment=models.CharField("comment",max_length=50,null=True, blank=True)
    createdate=models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.text
