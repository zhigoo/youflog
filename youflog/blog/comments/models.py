import datetime
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from blog.managers import CommentManager

class Comment(models.Model):
    
    author   = models.CharField(max_length = 50)
    email  = models.EmailField()
    weburl   = models.URLField()

    content = models.TextField(max_length=3000)
    parent = models.ForeignKey('self', null = True, blank = True, default = 0, related_name = 'children')
    mail_notify = models.BooleanField(default = False)

    # Metadata about the comment
    ip_address  = models.IPAddressField( blank=True, null=True)
    is_public   = models.BooleanField(default=True)
    date = models.DateTimeField()
    useragent=models.CharField(max_length=300)
    content_type   = models.ForeignKey(ContentType)
    object_pk      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    
    # Manager
    objects = CommentManager()
   
    def shortcontent(self,len=25):
        return self.content[0:len]

    def get_content_object_url(self):
        model = ContentType.objects.get(pk = self.content_type_id).model_class()
        object = model.objects.get(pk = self.object_pk)
        return object.get_absolute_url()

    def get_content_object_title(self):
        model = ContentType.objects.get(pk = self.content_type_id).model_class()
        object = model.objects.get(pk = self.object_pk)
        return object.title

    def __unicode__(self):
        return "%s: %s..." % (self.author, self.content[:50])
    
    def save(self, force_insert=False, force_update=False):
        if self.date is None:
            self.date = datetime.datetime.now()
        super(Comment, self).save(force_insert, force_update)
    
    def has_parent(self):
        return bool(self.parent_id)

    def get_parent(self):
        if self.parent_id:
            return Comment.objects.get(pk = self.parent_id)
        else:
            return None

    def has_children(self):
        return bool(self.children.get_children_by_id(self.id))

    def get_children(self):
        return self.children.get_children_by_id(self.id)

    def _get_object(self):
        model = ContentType.objects.get(pk = self.content_type_id).model_class()
        object = model.objects.get(pk = self.object_pk)
        return object
    object = property(_get_object)

    def get_absolute_url(self, anchor_pattern="#comment-%(id)s"):
        return self.get_content_object_url() + (anchor_pattern % self.__dict__)