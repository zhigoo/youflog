from django.http import HttpResponse,HttpResponseNotModified
from django.utils.http import http_date
from settings import STATIC_ROOT
import zipfile,mimetypes
from email.Utils import formatdate,parsedate_tz, mktime_tz
import time,os,stat,re

def SetCachingHeaders(response):
    MAX_AGE=600
    response['Cache-Control'] = 'max-age=%d,public'%(MAX_AGE)
    response['Expires']=formatdate(time.time() + MAX_AGE, usegmt=True)

def tinymce(request,path):
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
    response = HttpResponse(content,mimetype=mimetype)
    response["Content-Length"] = len(content)
    SetCachingHeaders(response)
    return response

cwd = os.getcwd()
def theme(request,path):
    file_path = os.path.normpath(os.path.join(cwd, 'templates/themes', path))
    statobj = os.stat(file_path)
    mimetype = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    if not _was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(file_path, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response

def _was_modified_since(header=None, mtime=0, size=0):
    try:
        if header is None:
            raise ValueError
        matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header,
                           re.IGNORECASE)
        header_mtime = mktime_tz(parsedate_tz(matches.group(1)))
        header_len = matches.group(3)
        if header_len and int(header_len) != size:
            raise ValueError
        if mtime > header_mtime:
            raise ValueError
    except (AttributeError, ValueError):
        return True
    return False
