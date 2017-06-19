from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

class SearchForm(forms.Form):
    search_field=forms.CharField(max_length=25,
                                 widget=forms.TextInput(attrs={'class': 'form-control mr-sm-2', 'placeholder':'Search'}),
                                 label='')