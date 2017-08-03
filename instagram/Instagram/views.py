# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render, redirect
from datetime import timedelta
from django.utils import timezone
from demo_app.forms import SignUpForm,LoginForm, PostForm, LikeForm, CommentForm, LikeCommForm
from django.contrib.auth.hashers import make_password,check_password
from demo_app.models import UserModel,SessionToken, PostModel, LikeModel, CommentModel, LikeComm
from Instagram.settings import BASE_DIR
from imgurpython import ImgurClient
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
import yagmail
import ctypes
from clarifai.rest import ClarifaiApp
from clarifai import rest
from clarifai.rest import Image as ClImage
import tkMessageBox
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
            ctypes.windll.user32.MessageBoxW(0, u"You are Successfully Registered.",
                                             u"Done", 0)
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
                    ctypes.windll.user32.MessageBoxW(0, u"Login Successfull.",
                                                     u"Done", 0)
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response

                else:
                    #Failed
                    ctypes.windll.user32.MessageBoxW(0, u"Check Username Or Password.",
                                                     u"Done", 0)
                    response_data['message'] = 'Incorrect Password! Please try again!'
        ctypes.windll.user32.MessageBoxW(0, u"Check Username Or Password.",
                                         u"Done", 0)


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

                ctypes.windll.user32.MessageBoxW(0, u"Post is Ready.",
                                                 u"Done", 0)
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
                like = LikeModel.objects.create(post_id=post_id, user=user)

                ctypes.windll.user32.MessageBoxW(0, u"Post Has Liked Successfully.",
                                                 u"Done", 0)

                email = like.post.user.email
                # sending welcome Email To User That Have Commented Successfully
                message = "Hii!.. Someone Liked your Post on Instaclone. Login Your accout to Check."
                yag = yagmail.SMTP('khiladimanu1@gmail.com', 'pallllavi@@')
                yag.send(to=email, subject='Liked Your Post', contents=message)
            else:
                existing_like.delete()
                ctypes.windll.user32.MessageBoxW(0, u"Post Has UnLiked Successfully.",
                                                 u"Done", 0)

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

            ctypes.windll.user32.MessageBoxW(0, u"Successfully Commented On Post.",
                                             u"Done", 0)

            # sending welcome Email To User That Have Commented Successfully
            email = comment.post.user.email
            message = "Hii!.. Someone Commented On your Post on Instaclone. Login Your accout to Check."
            yag = yagmail.SMTP('khiladimanu1@gmail.com', 'pallllavi@@')
            yag.send(to=email, subject='Commented On Post', contents=message)
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')

def add_category(post):
    app = ClarifaiApp(api_key='{ab1b812d1beb46ff8872acea4f341b4c}')

    # Logo model

    model = app.models.get('general-v1.3')
    response = model.predict_by_url(url=post.image_url)

    if response["status"]["code"] == 10000:
        if response["outputs"]:
            if response["outputs"][0]["data"]:
                if response["outputs"][0]["data"]["concepts"]:
                    for index in range(0, len(response["outputs"][0]["data"]["concepts"])):
                        category = CategoryModel(post=post,
                                                 category_text=response["outputs"][0]["data"]["concepts"][index][
                                                     "name"])
                        category.save()
                else:
                    print "No concepts list error."
            else:
                print "No data list error."
        else:
            print "No output lists error."
    else:
        print "Response code error."



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
    request.session.modified = True
    response = redirect("/login/")

    ctypes.windll.user32.MessageBoxW(0, u"You've been logged out successfully!",
                                     u"Thank you!", 0)

    response.delete_cookie(key="session_token")
    return response


def search(request):
    if "q" in request.GET:
        q = request.GET["q"]
        posts = PostModel.objects.filter(user__username__icontains=q)
        return render(request, "feeds.html", {"posts": posts, "query": q})
    return render(request, "feeds.html")



def like_comm(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeCommForm(request.POST)
        if form.is_valid():
            comment_id = form.cleaned_data.get('comment').id
            existing_like = LikeComm.objects.filter(comment_id=comment_id, user=user).first()
            if not existing_like:
                LikeComm.objects.create(comment_id=comment_id, user=user,)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')
