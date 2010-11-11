from django.db import models
import os.path
from django.conf import settings
from blog.photo import signals

class Album(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    createdate=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'blog_album'
    
    def photos(self):
        return Photo.objects.filter(album=self)
    
    def __unicode__(self):
        return self.name

class Photo(models.Model):
    name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='uploads/',blank=True,null=True)
    description=models.TextField()
    createdate=models.DateTimeField(auto_now_add=True)
    album=models.ForeignKey(Album)
    modifydate=models.DateTimeField(auto_now=True)
    
    def thumb_image(self):
        path=settings.MEDIA_ROOT+"/"+str(self.image)
        file,ext=os.path.splitext(path)
        basename=os.path.basename(file)
        return basename+".thumb"+ext
    
    class Meta:
        db_table = 'blog_photo'
    
    def save(self):
        super(Photo,self).save()
        #create thumb image
        signals.photo_was_uploaded.send(sender=self.__class__,photo=self)
        
    def delete(self):
        signals.photo_was_removed.send(sender=self.__class__,photo=self)
        super(Photo,self).delete()