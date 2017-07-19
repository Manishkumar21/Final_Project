# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime
from demo_app.forms import SignUpForm,LoginForm
from django.contrib.auth.hashers import make_password,check_password
from demo_app.models import UserModel
# Create your views here.

def signup_view(request):
    #Business Logic
    if request.method == 'GET':
        #display Signup Form
        signup_form = SignUpForm()
        template_name = 'signup.html'
    elif request.method == 'POST':
        #process the data
        signup_form = SignUpForm(request.POST)
        #Validate the Form Dat
        if signup_form.is_valid():
            #Validation Success
            username = signup_form.cleaned_data['username']
            name = signup_form.cleaned_data['name']
            email = signup_form.cleaned_data['email']
            password = signup_form.cleaned_data['password']
            #Save Data to db
            new_user = UserModel(name=name, email=email,password=make_password(password),username=username)
            new_user.save()
            template_name = 'success.html'

    return render(request,template_name, {'signup_form': signup_form})

def login_view(request):
    if request.method == 'GET':
        #Display Login Page
        login_form = LoginForm()
        template_name = 'login.html'
    elif request.method == 'POST':
        #Process The Data
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            #Validation Success
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            #read Data From db
            user = UserModel.objects.filter(username=username).first()
            if user:
                #compare Password
                if check_password(password, user.password):
                    #successfully Login
                    template_name = 'login_success.html'
                else:
                    #Failed
                    template_name = 'login_fail.html'
            else:
                #user doesn't exist
                template_name = 'login_fail.html'
        else:
            #Validation Failed
            template_name = 'login_fail.html'


    return render(request,template_name,{'login_form':login_form})

