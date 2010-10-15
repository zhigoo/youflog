#!/usr/bin/env python
# *_* encoding=utf-8*_*
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from tagging.fields import TagField
from datetime import datetime
from blog.comments.models import Comment
from tagging.models import Tag
from blog.managers import EntryPublishManager
import logging

class Archive(models.Model):
    monthyear = models.CharField(max_length=20)
    year = models.CharField(max_length=8)
    month = models.CharField(max_length=4)
    entrycount = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.monthyear
    
    def get_absolute_url(self):
        return 'archives/%s/%s'%(self.year,self.month)
    
class Blog(models.Model):
    author = models.CharField('admin',default='admin',max_length=20)
    email=models.EmailField(default='admin@iyouf.info')
    description = models.TextField()
    title = models.CharField(max_length=100,default='youflog')
    subtitle = models.CharField(max_length=100,default='a simple blog named youflog')
    posts_per_page = models.IntegerField(default=8)
    comments_per_page = models.IntegerField(default=10)
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
    
    @property
    def count(self):
        return Entry.objects.get_posts().filter(category=self).count()
       
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
 
class Entry(models.Model):
    ENTRY_TYPE_CHOICES=(('page','page'),('post','post'))
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(null=True, blank=True)
    published = models.BooleanField(default=False)
    entrytype = models.CharField(max_length=10,choices=ENTRY_TYPE_CHOICES,default='post')
    #标签
    tags=TagField()
    category= models.ForeignKey(Category) #文章分类
    #阅读的次数
    readtimes = models.IntegerField(default=0)
    slug = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    monthyear = models.CharField(max_length=20, null=True, blank=True)
    #允许评论
    allow_comment = models.BooleanField()
    allow_pingback = models.BooleanField()
    menu_order=models.IntegerField(default=0)
    #文章置顶
    sticky=models.BooleanField(default=False)
    #所有评论
    comments =  generic.GenericRelation(Comment, object_id_field='object_pk',
                                        content_type_field='content_type')
    date = models.DateTimeField(auto_now_add=True)
    objects=EntryPublishManager()
    
    postname=''
    class Meta:
        ordering= ['-id']
    
    def get_absolute_url(self):
        if self.link:
            return self.link
        else:
            return 'archive/%s.html'%(str(self.id))
    
    def shortcontent(self,len=200):
        return self.content[:len]
    
    def __unicode__(self):
        return self.title
    
    @property
    def excerpt_content(self):
        return self.__get_excerpt_content('Read More...')
    
    def __get_excerpt_content(self,more='Read More...'):
        if self.excerpt:
            return self.excerpt+' <a href="/%s">%s</a>'%(self.link,more)
        else:
            spl=self.content.split('<!--more-->')
            if len(spl) > 1:
                return spl[0]+u' <a href="/%s">%s</a>'%(self.link,more)
            else:
                return spl[0]
    
    #next post
    def next(self):
        next = Entry.objects.raw("select * from blog_entry where entrytype='post' and id > %s limit 1"%(str(self.id)))
        return next[:1]

    #prev post
    def prev(self):
        prev = Entry.objects.raw("select * from blog_entry where entrytype='post' and id < %s order by date desc limit 1"%(str(self.id)))
        return prev[:1]

    def get_tags(self):
        return Tag.objects.get_for_object(self)
    
    def fullurl(self):
        '''返回文章的绝对路径'''
        url=Site.objects.get_current().domain+"/"+self.link
        return  url
    
    def updateReadtimes (self):
        self.readtimes += 1
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
                        self.link='archive/%(post_id)s.html'%vals
                    else:
                        super(Entry,self).save()
                        vals.update({'post_id':self.id})
                        self.link='archive/%(post_id)s.html'%vals
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
        #删除该文章下的所有评论
        self.comments.all().delete()
        super(Entry,self).delete()

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
    
class Link(models.Model):
    href=models.URLField()
    text=models.CharField("text",max_length=20)
    comment=models.CharField("comment",max_length=50,null=True, blank=True)
    createdate=models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.text
