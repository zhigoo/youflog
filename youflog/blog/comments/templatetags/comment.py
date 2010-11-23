from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_unicode
from django.template.context import Context
from blog.comments.models import Comment
from blog.forms import CommentForm

from utils.utils import loadTempalte

COMMENT_MAX_DEPTH = 5

register = template.Library()

class BaseCommentNode(template.Node):
   
    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        if len(tokens) == 5:
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError("Third argument in %r must be 'as'" % tokens[0])
            return cls(
                object_expr = parser.compile_filter(tokens[2]),
                as_varname = tokens[4],
            )
        else:
            raise template.TemplateSyntaxError("%r tag requires 4 or 5 arguments" % tokens[0])

    @staticmethod
    def lookup_content_type(token, tagname):
        try:
            app, model = token.split('.')
            return ContentType.objects.get(app_label=app, model=model)
        except ValueError:
            raise template.TemplateSyntaxError("Third argument in %r must be in the format 'app.model'" % tagname)
        except ContentType.DoesNotExist:
            raise template.TemplateSyntaxError("%r tag has non-existant content-type: '%s.%s'" % (tagname, app, model))

    def __init__(self, ctype=None, object_pk_expr=None, object_expr=None, as_varname=None, comment=None):
        if ctype is None and object_expr is None:
            raise template.TemplateSyntaxError("Comment nodes must be given either a literal object or a ctype and object pk.")
        self.comment_model = Comment
        self.as_varname = as_varname
        self.ctype = ctype
        self.object_pk_expr = object_pk_expr
        self.object_expr = object_expr
        self.comment = comment

    def render(self, context):
        qs = self.get_query_set(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        return ''

    def get_query_set(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        if not object_pk:
            return self.comment_model.objects.none()

        qs = self.comment_model.objects.filter(
            content_type = ctype, object_pk = smart_unicode(object_pk),is_public = True,
        )
        return qs

    def get_target_ctype_pk(self, context):
        if self.object_expr:
            try:
                obj = self.object_expr.resolve(context)
            except template.VariableDoesNotExist:
                return None, None
            return ContentType.objects.get_for_model(obj), obj.pk
        else:
            return self.ctype, self.object_pk_expr.resolve(context, ignore_failures=True)

    def get_context_value_from_queryset(self, context, qs):
        raise NotImplementedError

class CommentFormNode(BaseCommentNode):
    def get_form(self, context):
        ctype, object_pk = self.get_target_ctype_pk(context)
        initial_date = context['comment_meta']

        if object_pk:
            return CommentForm(ctype.get_object_for_this_type(pk=object_pk), initial = initial_date)
        else:
            return None

    def render(self, context):
        context[self.as_varname] = self.get_form(context)
        return ''


class ThreadedCommentNode(BaseCommentNode):
    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])

        if len(tokens) == 3:
            return cls(object_expr=parser.compile_filter(tokens[2]))

    def tpl(self):
        return loadTempalte('comment.html')
    
    def render(self, context):
        qs = self.get_query_set(context)
        comments = list(qs)

        def append_comment_start(comment, list, html):
            template= self.tpl()
            comment_html=template.render(Context({'comment':comment}))
            html.append(comment_html)

        def append_comment_end(html):
            html.append('</li>\n')

        def append_child_start(html):
            html.append('<ul class="children">\n')

        def append_child_end(html):
            html.append('</ul>\n')

        def create_comment_html(root, list, html):
            append_comment_start(root, list, html)
            list.remove(root)
            if root.has_children():
                children = root.get_children()
                for child in children:
                    append_child_start(html)
                    create_comment_html(child, list, html)

            append_comment_end(html)
            if root.has_parent():
                append_child_end(html)

            if len(list) > 0 and not root.has_parent():
                create_comment_html(list[0], list, html)

        html = []
        if comments:
            sorted = []
            first = comments[0]
            html.append('<ol class="commentlist">\n')
            create_comment_html(first, comments, html)
            html.append('</ol>')

        return ''.join(html)

@register.tag
def get_comment_form(parser, token):
    
    return CommentFormNode.handle_token(parser, token)

@register.tag
def get_threaded_comment_list(parser, token):
    return ThreadedCommentNode.handle_token(parser, token)
