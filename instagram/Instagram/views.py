# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime
from demo_app.forms import SignUpForm
from django.contrib.auth.hashers import make_password
from demo_app.models import UserModel
# Create your views here.

def signup_view(request):
    #Business Logic
    if request.method == 'GET':
        #display Signup Form
        signup_form = SignUpForm()

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

    return render(request, 'signup.html', {'signup_form': signup_form})

