from django import forms

from .models import Post, Comment, User


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'image',
            'pub_date',
            'location',
            'category'
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
