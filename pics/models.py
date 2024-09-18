from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.contrib.auth.hashers import make_password, check_password

class Customers(models.Model):
    name = models.CharField(max_length=100, verbose_name="Full Name")
    password = models.CharField(max_length=128, verbose_name="Password")
    email = models.EmailField(max_length=255, verbose_name="Email Address")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    class Meta:
        db_table = 'pics_customers'
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']  # Add any other fields that are required for creating a user

    objects = BaseUserManager()
    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    

# Create your models here.
class AlbumsManager(models.Manager):
    def create_with_username(self, code, path, username):
        user = Customers.objects.get(username=username)
        return self.create(code=code, path=path, user=user)

class Albums(models.Model):
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255 )
    share = models.BooleanField(default=False)
    path = models.CharField(max_length=255,default=f'{code}\\')
    user = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='albums')
    created_at = models.DateTimeField(auto_now_add=True)
    objects = AlbumsManager()  # Use the custom manager

    def __str__(self):  

        return f"Album {self.code} by {self.user.username}"

import os

def uploadto(instance, filename):
    return os.path.join(f'{instance.album.code}/',filename)

class Photo(models.Model):
    album = models.ForeignKey(Albums, on_delete=models.CASCADE, related_name='photos')
    images = models.FileField(upload_to=uploadto,null=True , blank=True) 
    uploaded_by = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)




