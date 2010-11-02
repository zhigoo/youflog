from django.http import HttpResponse
from settings import STATIC_ROOT
import zipfile,mimetypes
import email.Utils
import time

def tinymce(request,path):
    
    def SetCachingHeaders(response):
        MAX_AGE=600
        response['Cache-Control'] = 'max-age=%d,public'%(MAX_AGE)
        response['Expires']=email.Utils.formatdate(time.time() + MAX_AGE, usegmt=True)
    
    zipfileName=STATIC_ROOT+'/tinymce.zip'
    zipfile_cache={}
    zf_object = zipfile_cache.get(zipfileName)
    if zf_object is None:
        try:
            zf_object = zipfile.ZipFile(zipfileName, "r")
        except (IOError, RuntimeError):
            zf_object=''
        zipfile_cache[zipfileName]=zf_object
    if zf_object == '':
        return HttpResponse('Not Found')
    file="tinymce/"+path
    mimetype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    content=zf_object.read(file)
    response = HttpResponse(content,mimetype=mimetype,status=304)
    response["Content-Length"] = len(content)
    SetCachingHeaders(response)
    return response


def theme(request,path):
    pass