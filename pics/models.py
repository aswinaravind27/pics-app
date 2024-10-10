from django.db import models

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Customers(models.Model):
    name = models.CharField(max_length=100, verbose_name="Full Name")
    password = models.CharField(max_length=128, verbose_name="Password")
    email = models.EmailField(max_length=255, verbose_name="Email Address")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    
    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
	
    class Meta:
        verbose_name_plural = "Customers Database"

# Create your models here.
class AlbumsManager(models.Manager):
    def create_with_username(self, code, path, email):
        user = Customers.objects.get(email=email)
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

        return f"{self.code} | {self.user.email}"
    class Meta:
        verbose_name_plural = "Albums Database"

import os



def uploadto(instance, filename):
    return os.path.join(f'{instance.album.code}/',filename)

class Photo(models.Model):
    album = models.ForeignKey(Albums, on_delete=models.CASCADE, related_name='photos')
    images = models.FileField(upload_to=uploadto,null=True , blank=True) 
    uploaded_by = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = "Photos Database"



class FavAlbums(models.Model):
    user = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='favorite_albums')
    album = models.ForeignKey(Albums, on_delete=models.CASCADE, related_name='favorited_by')
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'album')  # Ensures that a user can only favorite an album once
        verbose_name_plural = "Favourite Albums Database"

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.album.name}"
