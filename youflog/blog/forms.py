import datetime
from django import forms
from django.forms.util import ErrorDict
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.contrib.sites.models import Site
from models import Comment
from models import Blog

class CommentForm(forms.Form):
    author = forms.CharField(widget=forms.TextInput(attrs={'id':'author'}),max_length=50)
    email = forms.EmailField(widget=forms.TextInput(attrs={'id':'email'}))
    url = forms.URLField(widget=forms.TextInput(attrs={'id':'url'}),required=False)
    content = forms.CharField(widget=forms.Textarea,max_length=300)
    
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
            content=self.clean_comment(),
            date  = datetime.datetime.now(),
            mail_notify=self.cleaned_data["mail_notify"],
            is_public    = True,
            parent_id    = self.cleaned_data["parent_id"],
        )
        return new

    def security_errors(self):
        errors = ErrorDict()
        return errors
    
    def clean_comment(self):
        domain=Site.objects.get_current().domain
        content = self.cleaned_data["content"].replace('<script','&lt;script').replace('</script>','&lt;/script&gt;')
        content=content.replace('^~',"<img src=http://%s/static/images/smilies/icon_"%(domain)).replace('~^','.gif />')
        return content

class SettingForm(forms.Form):
    title= forms.CharField(max_length=200,initial = False, required = False)
    subtitle = forms.CharField(max_length=200,required = False)
    blognotice = forms.CharField(widget=forms.Textarea(attrs={'rows':2,'cols':10}),required = False)
    sitekeywords=forms.CharField(max_length=200,required = False)
    sitedescription=forms.CharField(max_length=200,required = False)
    email=forms.EmailField(required = False)
    #theme=forms.ChoiceField()
    
    def __init__(self, data=None, initial=None):
       
        if initial is None:
            initial = {}
        initial.update(self.generate_initial_data())
        super(SettingForm, self).__init__(data=data, initial=initial)
    
    def get_form_object(self):
        if not self.is_valid():
            raise ValueError("valid forms")
        blog = Blog.get()
        blog.title=self.cleaned_data['title']
        blog.subtitle=self.cleaned_data['subtitle']
        blog.blognotice=self.cleaned_data['blognotice']
        blog.sitekeywords=self.cleaned_data['sitekeywords']
        blog.sitedescription=self.cleaned_data['sitedescription']
        blog.email=self.cleaned_data['email']
        return blog
     
    def generate_initial_data(self):
        blog=Blog.get()
        dict={
             'title':blog.title,
             'subtitle':blog.subtitle,
             'blognotice':blog.blognotice,
             'sitekeywords':blog.sitekeywords,
             'sitedescription':blog.sitedescription,
             'email':blog.email 
        }
        return dict