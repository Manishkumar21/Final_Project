# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render, redirect
from datetime import timedelta
from django.utils import timezone
from demo_app.forms import SignUpForm,LoginForm, PostForm, LikeForm, CommentForm
from django.contrib.auth.hashers import make_password,check_password
from demo_app.models import UserModel,SessionToken, PostModel, LikeModel, CommentModel
from Instagram.settings import BASE_DIR
from imgurpython import ImgurClient
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
import yagmail
# Create your views here.


def signup_view(request):
    # it will Create an Account of User So He/She Can Login and Use Application...

    if request.method == "POST":
        # if Method is POST

        form = SignUpForm(request.POST)
        if form.is_valid():
            # if Valid Then Below Values Are Going To Stored In Database..
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            #saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()

            # sending welcome Email To User That Have Signup Successfully
            message = "Welcome!! Your Account has been SSuccessfully Created At p2p marketplace by Manish Kumar." \
                      "It is the place Where You Can Upload the Images Of the Product For Sale."
            yag = yagmail.SMTP('khiladimanu1@gmail.com', 'pallllavi@@')
            yag.send(to=email, subject='p2p Marketplace', contents=message)
            return email
            #   SUCCESSFULLY SEND EMAIL TO THE USER WHO HAS SIGNUP.

            return render(request, 'login.html')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form' : form})



def login_view(request):
    # it will fetch the data from the database and redirect to feed.html page...

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

                else:
                    #Failed
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        # Display Login Page
        form = LoginForm()

    return render(request, 'login.html', {'form' : form})



def post_view(request):
    # it creates the new post in timeline of the application...
    user = check_validation(request)
    if user:
        # if valid user
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()
                # it will save the image on local directory and imgur used to save on cloud...
                path = str(BASE_DIR+"//"+post.image.url)
                client = ImgurClient('4eb011a7402a650', '9aadcedb0bb5d5b384615153a9c15a5102e64d0a')
                post.image_url = client.upload_from_path(path,anon=True)['link']
                post.save()
                # save the Image

                return redirect('/feed/')   # directed to feed.html

        else:
            form = PostForm()
        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')



def feed_view(request):
    # it shows the all posts by the Users..
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        sorted(posts, key=str)
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feeds.html', {'posts': posts})
    else:
        return redirect('/login/')



def like_view(request):
    # it shows the like of the user....
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
                posts = PostModel.objects.all().order_by('-created_on')
                sorted(posts, key=str)
                for post_id in posts:
                    # sending welcome Email To User That Have Commented Successfully
                    message = "Hii!.. Someone Liked your Post on Instaclone. Login Your accout to Check."
                    yag = yagmail.SMTP('khiladimanu1@gmail.com', 'pallllavi@@')
                    yag.send(to=post_id.user.email, subject='Liked Your Post', contents=message)
            else:
                existing_like.delete()

            return redirect('/feed/')
    else:
        return redirect('/login/')




def comment_view(request):

    # it can create comment on the users post..
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            posts = PostModel.objects.all().order_by('-created_on')
            sorted(posts, key=str)
            for post_id in posts:

            # sending welcome Email To User That Have Commented Successfully
                message = "Hii!.. Someone Commented On your Post on Instaclone. Login Your accout to Check."
                yag = yagmail.SMTP('khiladimanu1@gmail.com', 'pallllavi@@')
                yag.send(to=post_id.user.email, subject='Commented On Post', contents=message)
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



def logout_view(request):
    # For logout the current User..
    logout(request)
    return redirect('/login/')