from django import forms
from models import UserModel, PostModel, LikeModel, CommentModel

class SignUpForm(forms.ModelForm):
    # for signup User
    class Meta:
        model = UserModel
        fields = ['name', 'email', 'username', 'password']


class LoginForm(forms.ModelForm):
    # for User Login
    class Meta:
        model = UserModel
        fields = ['username','password']


class PostForm(forms.ModelForm):
    # To create Post
    class Meta:
        model = PostModel
        fields=['image', 'caption']


class LikeForm(forms.ModelForm):
    # To like The Post
    class Meta:
        model = LikeModel
        fields=['post']


class CommentForm(forms.ModelForm):
    # To Comment On Post
    class Meta:
        model = CommentModel
        fields = ['comment_text', 'post']