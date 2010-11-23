from blog.models import OptionSet
from django import template
from django.template import Library, Node,resolve_variable
from threading import Thread
import settings
import hashlib,urllib,os,time

register = Library()

class VarNode(Node):
    def __init__(self, var_name, var_to_resolve):
        self.var_name = var_name
        self.var_to_resolve = var_to_resolve
        
    def get_context(self, top_context):
        for context in top_context.dicts:
            if self.var_name in context:
                return context
        return top_context

    def render(self, context):
        try:
            resolved_var = template.resolve_variable(self.var_to_resolve,context)
            self.get_context(context)[self.var_name] = resolved_var
        except template.VariableDoesNotExist:
            self.get_context(context)[self.var_name] = ''
        return ''
    
@register.tag
def var(parser, token):
    args = token.split_contents()
    if len(args) != 4 or args[2] != '=':
        raise template.TemplateSyntaxError(
            "'%s' statement requires the form {% %s foo = bar %}." % (
                args[0], args[0]))
    return VarNode(args[1], args[3])


class gravatorNode(Node):
    update_interval = 3600*24*10 # 10 days
    def __init__(self,email):
        self.email = email
        self.gavatar=OptionSet.get('gavatar')
    
    def write2file(self,url,path):
        urllib.urlretrieve(url, path)
    
    def _check_cache(self,path):
        if not os.path.exists(path):
            return False
        else:
            mtime = os.path.getmtime(path)
            if mtime < time.time() - self.update_interval:
                return False
        return True
    
    def _fetchGravatarImage(self,email_digest,avator_path):
        imgurl = "http://www.gravatar.com/avatar/"
        imgurl +=email_digest+"?"+ urllib.urlencode({'d':self.gavatar, 's':str(50),'r':'G'})
        th = Thread(target=self.write2file,args=(imgurl,avator_path))
        th.start()
        return imgurl
    
    def render(self,context):
        avator_path=settings.STATIC_ROOT+"/avator/"
        email = resolve_variable(self.email,context)
        default = '/static/avator/default.png'
        if not self.email:
            return default
        try:
            email_digest=hashlib.md5(email).hexdigest()
            avator_path=avator_path+email_digest
            if self._check_cache(avator_path):
                return '/static/avator/'+email_digest
            else:
                return self._fetchGravatarImage(email_digest, avator_path)
        except:
            return default

@register.tag
def gravator(parser,token):
    tokens = token.contents.split()
    if len(tokens) != 2:
        raise template.TemplateSyntaxError("useage 'gravator email '")
    return gravatorNode(tokens[1])