from blog.models import Album,Photo
from utils.utils import render_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import simplejson

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
    