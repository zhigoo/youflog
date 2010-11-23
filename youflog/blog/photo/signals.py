from django.dispatch import Signal
from django.conf import settings
from PIL import Image
import os.path

photo_was_uploaded=Signal(providing_args=['photo'])

photo_was_removed=Signal(providing_args=['photo'])


def on_photo_was_uploaded(sender,photo,*args,**kwargs):
    size= 128,128
    path=settings.MEDIA_ROOT+"/"+str(photo.image)
    file,ext=os.path.splitext(path)
    im=Image.open(path)
    im.thumbnail(size,Image.ANTIALIAS)
    im.save(file + ".thumb"+ext, im.format)

def on_photo_was_removed(sender,photo,*args,**kwargs):
    pass



photo_was_uploaded.connect(on_photo_was_uploaded)
photo_was_removed.connect(on_photo_was_removed)