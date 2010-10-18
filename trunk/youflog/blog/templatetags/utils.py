from blog.models import OptionSet
from django import template
from django.template import Library, Node,resolve_variable

import hashlib,urllib

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
            resolved_var = template.resolve_variable(self.var_to_resolve,
                                                     context)
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
    
    def __init__(self,email):
        self.email = email
        self.gavatar=OptionSet.get('gavatar')
        
    def render(self,context):
        email = resolve_variable(self.email,context)
        default = '/static/images/default.png'
        if not self.email:
            return default
        try:
            
            imgurl = "http://www.gravatar.com/avatar/"
            imgurl +=hashlib.md5(email).hexdigest()+"?"+ urllib.urlencode({
                'd':self.gavatar, 's':str(50),'r':'G'})
            return imgurl
        except:
            return default
        


@register.tag
def gravator(parser,token):
    tokens = token.contents.split()
    
    if len(tokens) != 2:
        raise template.TemplateSyntaxError("useage 'gravator email '")
    return gravatorNode(tokens[1])
    