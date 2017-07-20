from __future__ import unicode_literals
from django.db import models
import uuid

# Create your models here.
class UserModel(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=250)
	username = models.CharField(max_length=120)
	password = models.CharField(max_length=40)
	created_on = models.DateTimeField(auto_now_add = True)
	updated_on = models.DateTimeField(auto_now = True)

class SessionToken(models.model):
	user = models.ForeignKey(UserModel)
	session_token = models.CharField(max_length=255)
	created_on = models.DateTimeField(auto_now_add=True)
	is_valid = models.BooleanField(default=True)

	def create_token(self):
		self.session_token = uuid.uuid4()
