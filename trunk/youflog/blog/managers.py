#!/usr/bin/env python
# *_* encoding=utf-8*_*
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

class EntryPublishManager(models.Manager):
    
    def get_posts(self):
        return super(EntryPublishManager, self).get_query_set().filter(published=True,entrytype='post')\
        .order_by('-sticky').order_by('-date')
    
    def get_pages(self):
        return  self.get_query_set().filter(published=True,entrytype='page').order_by('-menu_order')
    
    def get_post_by_date(self,year,month):
        return super(EntryPublishManager, self).get_query_set().\
            filter(published=True,entrytype='post',\
            date__year=int(year),date__month=int(month))
    
    def get_post_by_day(self,year,month,day):
        return super(EntryPublishManager, self).get_query_set().\
            filter(published=True,entrytype='post',\
            date__year=int(year),date__month=int(month),date__day=int(day))

class CommentManager(models.Manager):

    def in_public(self):
        return self.get_query_set().filter(is_public = True).order_by('-date')

    def in_moderation(self):
        return self.get_query_set().filter(is_public=False)

    def get_children_by_id(self, id):
        list = []
        comments = self.get_query_set().filter(is_public = True).order_by('date')
        for comment in comments:
            if comment.parent_id == id:
                list.append(comment)

        return list

    def for_model(self, model):
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_query_set().filter(content_type=ct, is_public = True)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=force_unicode(model._get_pk_val()), is_public = True)
        return qs

class PingbackManager(models.Manager):
    def pingbacks_for_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, object_id=obj.pk)

    def count_for_object(self, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=content_type, object_id=obj.pk).count()


class PingbackClientManager(models.Manager):
    def count_for_link(self, obj, link):
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=ctype, object_id=obj.pk, url=link).count()