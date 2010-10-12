import datetime

from django import forms
from django.forms.util import ErrorDict
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from models import Comment

MAX_TAG_LENGTH = getattr(settings, 'MAX_TAG_LENGTH', 50)

class CommentForm(forms.Form):
    author = forms.CharField(label=_("Name"), max_length=50)
    email = forms.EmailField(label=_("Email address"))
    url = forms.URLField(label=_("URL"), required=False)
    content = forms.CharField(label=_('Comment'), widget=forms.Textarea,max_length=300)
    
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_pk = forms.CharField(widget=forms.HiddenInput)

    parent_id = forms.IntegerField(widget = forms.HiddenInput, initial = 0)
    mail_notify = forms.BooleanField(initial = False, required = False)
   
    def __init__(self, target_object, data=None, initial=None):
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial.update({
            'content_type'  : str(self.target_object._meta),
            'object_pk': str(self.target_object._get_pk_val()),
        })
        super(CommentForm, self).__init__(data=data, initial=initial)

    def get_comment_object(self):
       
        if not self.is_valid():
            raise ValueError("get_comment_object may only be called on valid forms")

        new = Comment(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_pk    = force_unicode(self.target_object._get_pk_val()),
            author    = self.cleaned_data["author"],
            email   = self.cleaned_data["email"],
            weburl     = self.cleaned_data["url"],
            content      = self.cleaned_data["content"],
            date  = datetime.datetime.now(),
            mail_notify=self.cleaned_data["mail_notify"],
            is_public    = True,
            parent_id    = 0,
        )

        return new

    def security_errors(self):
        errors = ErrorDict()
        return errors
    
    def clean_comment(self):
        content = self.cleaned_data["content"]
        return content
