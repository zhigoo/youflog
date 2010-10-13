from django.template import Library
register = Library()

from blog.models import Entry

@register.inclusion_tag('menus.html', takes_context = True)
def get_menus(context):
    pages=Entry.objects.get_pages()
    current = 'current' in context and context['current']
    return {
            'menus':pages,
            'current': current,
        }