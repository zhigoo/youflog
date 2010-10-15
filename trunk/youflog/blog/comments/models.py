import datetime
import hashlib,urllib
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from blog.managers import CommentManager
from blog.signals import comment_was_posted
from threading import Thread
from blog.akismet import Akismet
from blog.akismet import AkismetError

class Comment(models.Model):
    
    author   = models.CharField(max_length = 50)
    email  = models.EmailField()
    weburl   = models.URLField()

    content = models.TextField(max_length=3000)
    parent = models.ForeignKey('self', null = True, blank = True, default = 0, related_name = 'children')
    mail_notify = models.BooleanField(default = False)

    # Metadata about the comment
    ip_address  = models.IPAddressField(_('IP address'), blank=True, null=True)
    is_public   = models.BooleanField(_('is public'), default=True)
    date = models.DateTimeField(auto_now_add=True)
    
    content_type   = models.ForeignKey(ContentType)
    object_pk      = models.PositiveIntegerField(_('object id'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    
    # Manager
    objects = CommentManager()

    class Meta:
        permissions = [("can_moderate", "Can moderate comments")]
        
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
        
    @property
    def gravatar_url(self):
        default = '/static/images/none.jpg'
        if not self.email:
            return default
        try:
            imgurl = "http://www.gravatar.com/avatar/"
            imgurl +=hashlib.md5(self.email.lower()).hexdigest()+"?"+ urllib.urlencode({
                'd':'monsterid', 's':str(50),'r':'G'})
            return imgurl
        except:
            return default
    
    def has_parent(self):
        return bool(self.parent_id)

    def get_parent(self):
        if self.parent_id:
            return Comment.objects.get(pk = self.parent_id)
        else:
            return None

    def get_depth(self):
        def _get_depth(object, list):
            if object.has_parent():
                parent = object.get_parent()
                list.append(parent)
                _get_depth(parent, list)

        list = [1]
        _get_depth(self, list)

        return len(list)

    def get_parity(self):
        def _get_depth_odd(object):
            comments = list(Comment.objects.filter(content_type = object.content_type, 
                        object_pk = object.object_pk))
            for comment in comments:
                if comment.get_depth() != object.get_depth():
                    comments.remove(comment)

            if object.has_parent():
                parent = object.get_parent()
                podd = _get_depth_odd(parent)
                return bool((podd + 1) % 2)

            return bool((comments.index(object) + 1) % 2)

        if _get_depth_odd(self):
            return 'even'
        else:
            return 'odd'

    def is_last_child(self):
        '''Check whether this is the last child'''
        def get_root(object):
            if object.has_parent():
                return get_root(object.get_parent())
            else:
                return object

        def get_inherit(object, list):
            if object and object.has_children():
                for child in object.get_children():
                    if child.has_children():
                        list.append(child)
                        get_inherit(child, list)
                    else:
                        list.append(child)

        list = []
        last = True
        get_inherit(get_root(self), list)
        for item in list:
            if self.date < item.date:
                last = False
                break

        return last

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
    
    
def validate_comment(sender, comment, request, *args, **kwargs):
    ak = Akismet(
            key = 'cda0f27f8e2f',
            blog_url=Site.objects.get_current().domain
        )
    try:
        if ak.verify_key():
            data = {
                'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referrer': request.META.get('HTTP_REFERER', ''),
                'comment_type': 'comment',
                'comment_author': comment.author.encode('utf-8'),
            }
            if ak.comment_check(comment.content.encode('utf-8'), data=data, build_data=True):
                comment.is_public = False
                comment.save()
                
                ak.submit_spam(comment.content.encode('utf-8'), data=data, build_data=True)
                
    except AkismetError:
        #comment.save()
        pass

def on_comment_was_posted(sender,comment,request,*args,**kwargs):
    th = Thread(target=validate_comment,args=(sender,comment,request))
    th.start()

comment_was_posted.connect(on_comment_was_posted)