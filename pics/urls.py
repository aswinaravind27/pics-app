"""Pixora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.index,name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('albumcreate/', views.albumcreation, name='albumcreate'),
    path('album/<str:id>/', views.album_view, name='album_view'),  # Use <str:id> for string ID
    path('album/<str:id>/upload/', views.upload_photos, name='upload_photos'),  # Use <str:id> for string ID
    path('delete/<id>/<pid>/', views.delete_photo, name='delete_photo'),
    path('album/delete/<int:id>/', views.delete_album, name='delete_album'),
    path('album/<uuid:id>/favorite/', views.Fav_albums, name='favorite_album'),
    path('album/<uuid:id>/edit/',views.EditAlbum,name='editalbum')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
