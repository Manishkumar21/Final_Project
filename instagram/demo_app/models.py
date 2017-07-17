from __future__ import unicode_literals
from django.db import models

# Create your models here.
class User(models.Model):
	email = models.EmailField()
    name = models.CharField(max_length=120)
	username = models.CharField(max_length=120)
	password = models.CharField(max_length=40)
    created_on = models.DateTimeField(auto_now_add = True)
	updated_on = models.DateTimeField(auto_now = True)