from django import forms

from .models import Post, Comment, User


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': '22', 'rows': '5'})
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'
