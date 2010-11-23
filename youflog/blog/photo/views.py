# Create your views here.
from blog.photo.models import Album,Photo
from utils.utils import render_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import simplejson
from settings import MEDIA_ROOT
from os.path import isdir, dirname

@login_required
def albums(request):
    albums=Album.objects.all()
    photocount=Photo.objects.count()
    return render_response(request,'admin/albums.html',locals())

@login_required
@require_POST
def add_album(request):
    albumName=request.POST.get("albumName")
    desc=request.POST.get("desc")
    try:
        album=Album(name=albumName,description=desc)
        album.save()
        json = simplejson.dumps((True,"album created!"))
    except:
        json=simplejson.dumps((False,-103,'album create failure!'))
    return HttpResponse(json)


def detail(request):
    id=request.GET.get('id')
    album=get_object_or_404(Album,id=id)
    return render_response(request,'admin/photos.html',{'album':album})

from os import makedirs
import ImageFile
@login_required
@require_POST
def upload(request):
    id=request.POST.get('albumid')
    album=get_object_or_404(Album,id=id)

    file_obj=request.FILES.get('file',None)
    upload_path=MEDIA_ROOT;
    if file_obj:
        filename=file_obj.name
        savepath='%s/%s'%(upload_path,filename.decode('utf8'))
        dir = dirname(savepath)
        if not isdir(dir):
            makedirs(dir)
        parser = ImageFile.Parser()
        for chunk in file_obj.chunks():
            parser.feed(chunk)
        img = parser.close() 
        img.save(savepath)
        image_file=savepath[len(upload_path):]
        photo = Photo(name=filename,image=filename,album=album,description='')
        photo.save()
    return render_response(request,'admin/photos.html',{'album':album})