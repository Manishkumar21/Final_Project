# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from datetime import timedelta
from django.utils import timezone
from demo_app.forms import SignUpForm,LoginForm, PostForm, LikeForm, CommentForm
from django.contrib.auth.hashers import make_password,check_password
from demo_app.models import UserModel,SessionToken, PostModel, LikeModel, CommentModel
from Instagram.settings import BASE_DIR
from imgurpython import ImgurClient
# Create your views here.


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            #saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            return render(request, 'success.html')
            #return redirect('login/')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form' : form})


def login_view(request):
    if request.method == 'POST':
        #Process The Data
        response_data = {}
        form = LoginForm(request.POST)
        if form.is_valid():
            #Validation Success
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            #read Data From db
            user = UserModel.objects.filter(username=username).first()
            if user:
                #compare Password
                if check_password(password, user.password):
                    #successfully Login
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response

                    #template_name = 'login_success.html'
                else:
                    #Failed
                    response_data['message'] = 'Incorrect Password! Please try again!'
                   # template_name = 'login_fail.html'

    elif request.method == 'GET':
        # Display Login Page
        form = LoginForm()
        #template_name = 'login.html'

    #response_data['form'] = form
    return render(request, 'login.html', {'form' : form})



def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + post.image.url)

                client = ImgurClient('4eb011a7402a650', '9aadcedb0bb5d5b384615153a9c15a5102e64d0a')
                post.image_url = client.upload_from_path(path,anon=True)['link']
                post.save()

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:

        posts = PostModel.objects.all().order_by('created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feeds.html', {'posts': posts})
    else:
        return redirect('/login/')



def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')




def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')




#For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None